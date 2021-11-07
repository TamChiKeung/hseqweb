from rest_framework import serializers
from uploader.models import Pedigree, PhenotypeFeature, Patient, OntologyClass
from uploader.models import Upload
from django.contrib.auth.models import User

class UploadCreateSerializer(serializers.ModelSerializer):

    token = serializers.CharField(max_length=127)
    class Meta:
        model = Upload
        fields = ['token', 'is_exome', 'is_paired', 'col_uuid', 'status']
        extra_kwargs = {
            'token': {'write_only': True}
        }

    def validate_token(self, token):
        try:
            self.user = User.objects.get(userprofile__token=token)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid token!')    
        return token

    def validate_col_uuid(self, col_uuid):
        upload = Upload.objects.filter(col_uuid=col_uuid)
        if upload.exists():
            raise serializers.ValidationError('Upload already exists!')    
        return col_uuid

    
    def save(self):
        token = self.validated_data.pop('token')
        self.instance = super(UploadCreateSerializer, self).save()
        self.instance.user = self.user
        self.instance.save()
        return self.instance


class OntologyClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = OntologyClass
        fields = '__all__'
class PhenotypeFeatureSerializer(serializers.ModelSerializer):
    phenotype = OntologyClassSerializer()
    class Meta:
        model = PhenotypeFeature
        fields = '__all__'

class PatientShortSerializer(serializers.ModelSerializer):
    phenotypes = PhenotypeFeatureSerializer(many=True)
    age = serializers.ReadOnlyField()

    def find_by_identifier_startsWith(self, term, limit=10):
        return Patient.objects.filter(identifier__istartswith=term).order_by('identifier')[:limit]
    class Meta:
        model = Patient 
        fields = ('id', 'identifier', 'mrn', 'first_name', 'last_name', 'full_name', 'gender', 'date_of_birth',  'age', 'phenotypes')

    # def get_phenotypes(self, obj):
    #     return getattr(obj, 'phenotypes', [])
class PedigreeSerializer(serializers.ModelSerializer):
    father = PatientShortSerializer()
    mother = PatientShortSerializer()
    sister = PatientShortSerializer()
    brother = PatientShortSerializer()
    class Meta:
        model = Pedigree
        fields = ('__all__')
class PatientSerializer(serializers.ModelSerializer):
    phenotypes = PhenotypeFeatureSerializer(many=True)
    pedigree = PedigreeSerializer()
    age = serializers.ReadOnlyField()

    def add_or_update(self, validated_data, user):
        print(validated_data)
        
        phenotypes = []
        if 'phenotypes' in validated_data:
            phenotypes = validated_data.pop('phenotypes')
        
        patient = None
        if not ('id' in validated_data and validated_data['id']):
            patient = Patient(**validated_data)
            patient.created_by = user
        else:
            patient = Patient.objects.get(id=validated_data['id'])
            patient.first_name = validated_data['first_name']
            patient.last_name = validated_data['last_name']
            patient.date_of_birth = validated_data['date_of_birth']
            patient.gender = validated_data['gender']
            patient.modified_by = user
            
        patient.date_of_birth =  validated_data['date_of_birth'] if 'date_of_birth' in validated_data else None
        patient.full_name = validated_data['first_name'] + (' ' + validated_data['last_name'] if validated_data['last_name'] else '')
        patient.save()
        for phenotype in phenotypes:
            ontClass, c_created = OntologyClass.objects.get_or_create(**phenotype['phenotype'])
            phenotype['phenotype'] = ontClass
            pf, created = PhenotypeFeature.objects.get_or_create(**phenotype)
            patient.phenotypes.add(pf)

        if 'id' not in validated_data:
            patient.mrn = 'P' + str(patient.pk).rjust(11, '0')
        
        patient.save()
        return patient

    def update_pedigree(self, validated_data, user):
        patient = Patient.objects.get(id=validated_data['id'])
        if not patient.pedigree:
            patient.pedigree = Pedigree()

        if 'pedigree' not in validated_data:
            return patient
        
        if 'father' in validated_data['pedigree'] and validated_data['pedigree']['father']:
            patient.pedigree.father = self.add_or_update(validated_data['pedigree']['father'], user)
        if 'mother' in validated_data['pedigree'] and validated_data['pedigree']['mother']:
            patient.pedigree.mother = self.add_or_update(validated_data['pedigree']['mother'], user)
        if 'sister' in validated_data['pedigree'] and validated_data['pedigree']['sister']:
            patient.pedigree.sister = self.add_or_update(validated_data['pedigree']['sister'], user)
        if 'brother' in validated_data['pedigree'] and validated_data['pedigree']['brother']:
            patient.pedigree.brother = self.add_or_update(validated_data['pedigree']['brother'], user)

        patient.pedigree.save()
        patient.save()

        return patient
            

    def find():
        return Patient.objects.all().order_by('full_name')
    class Meta:
        model = Patient 
        fields = '__all__'
        
class UploadSerializer(serializers.ModelSerializer):        
    patient = PatientSerializer()
    class Meta:
        model = Upload
        fields = '__all__'

class UploadDetailSerializer(serializers.ModelSerializer):
    collection = serializers.ReadOnlyField()
    output_status = serializers.ReadOnlyField()
    output_collection = serializers.ReadOnlyField()
    out_col_uuid = serializers.ReadOnlyField()
    output_files = serializers.ReadOnlyField()
    files = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    token = serializers.ReadOnlyField()
    metadata_filename = serializers.ReadOnlyField()
    sequence_filename = serializers.ReadOnlyField()        
    patient = PatientSerializer()
    class Meta:
        model = Upload
        fields = ('id', 'is_exome', 'is_paired', 'is_trio', 'patient_id', 'col_uuid', 'status', 'date', 
        'error_message', 'collection', 'name', 'token', 'files', 'output_files', 'output_status',
        'output_collection', 'out_col_uuid', 'metadata_filename', 'sequence_filename')