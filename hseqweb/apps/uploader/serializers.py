
import tempfile
import os
import csv
import gzip
import yaml
import logging 
import json

from typing import Sequence
from django.core.exceptions import ValidationError

from rest_framework import serializers
from hseqweb.apps.uploader.qc_fasta import qc_fasta
from hseqweb.apps.uploader.utils import hg19_to_hg38
from uploader.models import Pedigree, PhenotypeFeature, Patient, OntologyClass
from uploader.models import Upload
from uploader.tasks import upload_to_arvados
from django.contrib.auth.models import User
from django.conf import settings
from .tusfile import TusFile
from .utils import is_gzip_file, to_dict


logger = logging.getLogger(__name__)

UPLOADER_PROJECT_UUID = getattr(settings, 'UPLOADER_PROJECT_UUID', 'cborg-j7d0g-nyah4ques5ww7pk')
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

    def find_by_identifier_startsWith(self, term, user=None, limit=10):
        if user:
            return Patient.objects.filter(identifier__istartswith=term, created_by=user).order_by('identifier')[:limit]
        return Patient.objects.filter(identifier__istartswith=term).order_by('identifier')[:limit]
    class Meta:
        model = Patient 
        fields = ('id', 'identifier', 'mrn', 'first_name', 'last_name', 'full_name', 'gender', 'date_of_birth',  'age', 'phenotypes')

class PatientIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient 
        fields = ('id', 'mrn')

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
        logger.info("Saving patient: %s", str(validated_data))
        phenotypes = validated_data.pop('phenotypes') if 'phenotypes' in validated_data else []
        if not phenotypes:
            phenotypes = []

        
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

        logger.info("Saved patient: %s", str(patient.pk))
        return patient

    def update_pedigree(self, validated_data, user):
        patient = Patient.objects.get(id=validated_data['id'])
        if not patient.pedigree:
            patient.pedigree = Pedigree()

        if 'pedigree' not in validated_data:
            return patient
        
        if 'father' in validated_data['pedigree'] and validated_data['pedigree']['father']:
            patient.pedigree.father = self.add_or_update(validated_data['pedigree']['father'], user)
        else:
            patient.pedigree.father = None
        if 'mother' in validated_data['pedigree'] and validated_data['pedigree']['mother']:
            patient.pedigree.mother = self.add_or_update(validated_data['pedigree']['mother'], user)
        else:
            patient.pedigree.mother = None
        if 'sister' in validated_data['pedigree'] and validated_data['pedigree']['sister']:
            patient.pedigree.sister = self.add_or_update(validated_data['pedigree']['sister'], user)
        else:
            patient.pedigree.sister = None
        if 'brother' in validated_data['pedigree'] and validated_data['pedigree']['brother']:
            patient.pedigree.brother = self.add_or_update(validated_data['pedigree']['brother'], user)
        else:
            patient.pedigree.brother = None

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

class SubmissionDetailSerializer(serializers.ModelSerializer):
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
        fields = '__all__'
class UploadRequestSerializer(serializers.ModelSerializer):
    sequence_file1 = serializers.CharField(allow_blank=True)
    sequence_file2 = serializers.CharField(allow_blank=True)
    bed_file = serializers.CharField(allow_blank=True)
    father_sequence_file1 = serializers.CharField(allow_blank=True)
    father_sequence_file2 = serializers.CharField(allow_blank=True)
    father_bed_file = serializers.CharField(allow_blank=True)
    mother_sequence_file1 = serializers.CharField(allow_blank=True)
    mother_sequence_file2 = serializers.CharField(allow_blank=True)
    mother_bed_file = serializers.CharField(allow_blank=True)
    sibling_sequence_file1 = serializers.CharField(allow_blank=True)
    sibling_sequence_file2 = serializers.CharField(allow_blank=True)
    sibling_bed_file = serializers.CharField(allow_blank=True)
    patient = PatientIdSerializer()
    class Meta:
        model = Upload
        fields = '__all__'

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance=instance, data=data, **kwargs)


    def add_or_update(self, validated_data, user):
        logger.info("Saving submission: %s", str(validated_data))
        self.remove_file_fields(validated_data)
        patient = validated_data.pop('patient')
        patient = Patient.objects.get(id=patient['id'])

        self.validate(validated_data)

        upload = Upload(**validated_data)
        upload.patient = patient
        upload.user = user
        upload.save()
        return upload

    def submit(self, validated_data, user):
        logger.info("Submitting submission: %s", str(validated_data))
        self.tus_files_moved = {}
        self.remove_file_fields(validated_data)
        patient = validated_data.pop('patient')
        patient = Patient.objects.get(id=patient['id'])

        upload = Upload(**validated_data)
        upload.patient = patient
        upload.user = user
        upload.status = Upload.SUBMITTED

        upload_config = {}
        upload_config['sequence_file'] = self.create_sequence_filepath(validated_data, 'sequence_file_location1', 'sequence_filename1')
        upload_config['sequence_file2'] = self.create_sequence_filepath(validated_data, 'sequence_file_location2', 'sequence_filename2')
        (upload_config['bed_file'], upload_config['original_bed_file_grch37']) = self.create_bed_filepath(validated_data, 'bed_file_location', 'bed_filename', 'assembly')
        upload.is_paired = True if upload_config['sequence_file2'] else False
        upload.is_exome = True if upload_config['bed_file'] else False


        upload_config['father_sequence_file'] = self.create_sequence_filepath(validated_data, 'father_sequence_file_location1', 'father_sequence_filename1')
        upload_config['father_sequence_file2'] = self.create_sequence_filepath(validated_data, 'father_sequence_file_location2', 'father_sequence_filename2')
        (upload_config['father_bed_file'], upload_config['father_original_bed_file_grch37']) = self.create_bed_filepath(validated_data, 'father_bed_file_location', 'father_bed_filename', 'father_assembly')
        upload.is_paired_father = True if upload_config['father_sequence_file2'] else False
        upload.is_exome_father = True if upload_config['father_bed_file'] else False

        upload_config['mother_sequence_file'] = self.create_sequence_filepath(validated_data, 'mother_sequence_file_location1', 'mother_sequence_filename1')
        upload_config['mother_sequence_file2'] = self.create_sequence_filepath(validated_data, 'mother_sequence_file_location2', 'mother_sequence_filename2')
        (upload_config['mother_bed_file'], upload_config['mother_original_bed_file_grch37']) = self.create_bed_filepath(validated_data, 'mother_bed_file_location', 'mother_bed_filename', 'mother_assembly')
        upload.is_paired_mother = True if upload_config['mother_sequence_file2'] else False
        upload.is_exome_mother = True if upload_config['mother_bed_file'] else False

        upload_config['sibling_sequence_file'] = self.create_sequence_filepath(validated_data, 'sibling_sequence_file_location1', 'sibling_sequence_filename1')
        upload_config['sibling_sequence_file2'] = self.create_sequence_filepath(validated_data, 'sibling_sequence_file_location2', 'sibling_sequence_filename2')
        (upload_config['sibling_bed_file'], upload_config['sibling_original_bed_file_grch37']) = self.create_bed_filepath(validated_data, 'sibling_bed_file_location', 'sibling_bed_filename', 'sibling_assembly')
        upload.is_paired_sibling = True if upload_config['sibling_sequence_file2'] else False
        upload.is_exome_sibling = True if upload_config['sibling_bed_file'] else False
       
        upload.save()
        upload_obj = SubmissionMetadataSerializer(upload).data
        patient_obj = self.trim_patient(upload_obj['patient'])
        
        upload_config['metadata_file'] = self.save_yaml_file(upload_obj)
        upload_config['ped_file'] = self.create_ped_file(upload_obj['patient'])

        upload.phenotypes_snapshot = json.dumps(patient_obj['phenotypes'])
        if 'pedigree' in patient_obj and patient_obj['pedigree']:
            upload.pedigree_snapshot = json.dumps(patient_obj['pedigree'])
        upload.save()

        project_uuid = UPLOADER_PROJECT_UUID
        if user.userprofile.project_uuid:
            project_uuid = user.userprofile.project_uuid
        upload_to_arvados.delay(project_uuid, upload.id, upload_config)
        return upload

    def trim_patient(self, patient):
        del patient['id']
        for pheno in patient['phenotypes']:
            del pheno['id']
            del pheno['phenotype']['id']

        if 'pedigree' in patient and patient['pedigree']:
            del patient['pedigree']['id']
            if 'father' in  patient['pedigree'] and patient['pedigree']['father']:
                del  patient['pedigree']['father']['phenotypes']
            if 'mother' in  patient['pedigree'] and patient['pedigree']['mother']:
                del  patient['pedigree']['mother']['phenotypes']
            if 'brother' in  patient['pedigree'] and patient['pedigree']['brother']:
                del  patient['pedigree']['brother']['phenotypes']
            if 'sister' in  patient['pedigree'] and patient['pedigree']['sister']:
                del  patient['pedigree']['sister']['phenotypes']

        return patient


    def validate_sequence_file_location1(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        
        return self.validate_sequence_file(value)

    def validate_sequence_file_location2(self, value):
        return self.validate_sequence_file(value)
        
    def validate_bed_file_location(self, value):
        return self.validate_bed_files_format(value)

    def validate_father_sequence_file_location1(self, value):
        return self.validate_sequence_file(value)

    def validate_father_sequence_file_location2(self, value):
        return self.validate_sequence_file(value)

    def validate_father_bed_file_location(self, value):
        return self.validate_bed_files_format(value)

    def validate_mother_sequence_file_location1(self, value):
        return self.validate_sequence_file(value)

    def validate_mother_sequence_file_location2(self, value):
        return self.validate_sequence_file(value)

    def validate_mother_bed_file_location(self, value):
        return self.validate_bed_files_format(value)

    def validate_sibling_sequence_file_location1(self, value):
        return self.validate_sequence_file(value)

    def validate_sibling_sequence_file_location2(self, value):
        return self.validate_sequence_file(value)

    def validate_sibling_bed_file_location(self, value):
        return self.validate_bed_files_format(value)

    def validate_sequence_file(self, sequence_file_location):
        if not sequence_file_location:
            return sequence_file_location

        filepath = os.path.join(settings.TUS_UPLOAD_DIR, sequence_file_location)
        if not os.path.exists(filepath):
            raise serializers.ValidationError("Something went wrong. Unable to find uploaded file")
        try:
            if is_gzip_file(filepath):
                sf = gzip.open(filepath, 'r')
            else:
                raise ValidationError("Files should be compressed with gzip!")
            qc_fasta(sf)
        except ValueError:
            raise ValidationError("Invalid file format")
        return sequence_file_location

    def validate_bed_files_format(self, bed_file_location):
        if bed_file_location:
            filepath = os.path.join(settings.TUS_UPLOAD_DIR, bed_file_location)
            if not os.path.exists(filepath):
                raise serializers.ValidationError("Something went wrong. Unable to find uploaded file")
            # try:
            #     bf = open(filepath, 'r')
            #     # TODO: check file format
            #     bf.close()
            # except ValueError:
            #     raise ValidationError("Invalid file format")

        return bed_file_location



    def create_sequence_filepath(self, validated_data, location_field, filename_field):
        sequence_file_loc = validated_data.pop(location_field)
        sequence_filename = validated_data.pop(filename_field)

        if sequence_file_loc in self.tus_files_moved:
            return self.tus_files_moved[sequence_file_loc]

        if sequence_file_loc and sequence_filename:
            sequence_tus_file = TusFile(str(sequence_file_loc))
            sequence_tus_file.clean()
            sequence_tus_filepath = os.path.join(settings.TUS_UPLOAD_DIR, sequence_file_loc)
            self.tus_files_moved[sequence_file_loc] = sequence_tus_filepath
            return sequence_tus_filepath

    def create_bed_filepath(self, validated_data, location_field, filename_field, assembly_field):
        bed_file_loc = validated_data.pop(location_field)
        bed_filename = validated_data.pop(filename_field)
        bed_file_assembly = validated_data.pop(assembly_field)

        if bed_file_loc in self.tus_files_moved:
            return self.tus_files_moved[bed_file_loc]

        bed_file = None
        original_bed_file_grch37 = None
        if bed_file_loc and bed_filename:
            bed_tus_file = TusFile(str(bed_file_loc))
            bed_tus_file.clean()

            bed_file = os.path.join(settings.TUS_UPLOAD_DIR, bed_file_loc)
            logger.info("Bed file assembly: %s", bed_file_assembly)
            if bed_file and bed_file_assembly == 'GRCh37':
                bed_hg38_out_file = tempfile.NamedTemporaryFile('wt', delete=False)
                hg19_to_hg38(bed_file, bed_hg38_out_file.name)
                logger.info("bed file conversion from hg19 to hg38 completed: %s $s", bed_file, bed_hg38_out_file.name)
                original_bed_file_grch37 = bed_file
                bed_file = bed_hg38_out_file.name
            
            bed_tus_filepaths = (bed_file, original_bed_file_grch37)
            self.tus_files_moved[bed_file_loc] = bed_tus_filepaths
            return bed_tus_filepaths

        return (None, None)

    def save_yaml_file(self, data):
        tmp_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        yaml.safe_dump(to_dict(data), tmp_file, sort_keys=False)
        tmp_file.flush()
        return tmp_file.name 

    def create_ped_file(self, patiend_obj):
        ped_file_comments = "#PED format pedigree \
        \n# \
        \n#fam-id/ind-id/pat-id/mat-id: 0=unknown \
        \n#sex: 1=male; 2=female; 0=unknown \
        \n#phenotype: -9=missing, 0=missing; 1=unaffected; 2=affected \
        \n# \
        \n#family-id ind-id  pat-id  mat-id  sex     phen" 
        tmp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='UTF8')
        writer = csv.writer(tmp_file)
        writer.writerow([ped_file_comments])

        data = []
        patient_entry = [patiend_obj['identifier'], patiend_obj['identifier']]
        father_entry = None
        mother_entry = None
        brother_entry = None
        sister_entry = None
        if 'pedigree' in patiend_obj and patiend_obj['pedigree']:
            if 'father' in  patiend_obj['pedigree'] and patiend_obj['pedigree']['father']:
                father = patiend_obj['pedigree']['father']
                patient_entry.append(father['identifier'])
                father_entry = [patiend_obj['identifier'], father['identifier'], 0, 0, 1, 0]
            else:
                patient_entry.append(0)

            if 'mother' in  patiend_obj['pedigree'] and patiend_obj['pedigree']['mother']:
                mother = patiend_obj['pedigree']['mother']
                patient_entry.append(mother['identifier'])
                mother_entry = [patiend_obj['identifier'], mother['identifier'], 0, 0, 2, 0]
            else:
                patient_entry.append(0)

            if 'brother' in  patiend_obj['pedigree'] and patiend_obj['pedigree']['brother']:
                brother = patiend_obj['pedigree']['brother']
                brother_entry = [patiend_obj['identifier'], brother['identifier'], father_entry if father_entry else 0, mother_entry if mother_entry else 0, 1, 0]

            if 'sister' in  patiend_obj['pedigree'] and patiend_obj['pedigree']['sister']:
                sister = patiend_obj['pedigree']['sister']
                sister_entry = [patiend_obj['identifier'], sister['identifier'], father_entry if father_entry['identifier'] else 0, mother_entry['identifier'] if mother_entry else 0, 2, 0]
        else:
            patient_entry += [0, 0]

        if patiend_obj['gender'] == 'male':
            patient_entry.append(1)
        elif patiend_obj['gender'] == 'female':
            patient_entry.append(2)
        else:
            patient_entry.append(0)

        patient_entry.append(2)
        data.append(patient_entry)
        if father_entry:
            data.append(father_entry)
        if mother_entry:
            data.append(mother_entry)
        if brother_entry:
            data.append(brother_entry)
        if sister_entry:
            data.append(sister_entry)

        writer.writerows(data)
        tmp_file.close()
        return tmp_file.name 


    def remove_file_fields(self, validated_data):
        validated_data.pop('sequence_file1')
        validated_data.pop('sequence_file2')
        validated_data.pop('bed_file')
        validated_data.pop('father_sequence_file1')
        validated_data.pop('father_sequence_file2')
        validated_data.pop('father_bed_file')
        validated_data.pop('mother_sequence_file1')
        validated_data.pop('mother_sequence_file2')
        validated_data.pop('mother_bed_file')
        validated_data.pop('sibling_sequence_file1')
        validated_data.pop('sibling_sequence_file2')
        validated_data.pop('sibling_bed_file')


class UploadResponseSerializer(serializers.ModelSerializer):      
    patient = PatientShortSerializer()
    class Meta:
        model = Upload
        exclude = ('is_exome', 'is_paired', 'is_exome_father', 'is_paired_father', 'is_exome_mother', 'is_paired_mother', 'is_exome_sibling', 'is_paired_sibling', 'phenotypes_snapshot', 'pedigree_snapshot')


class SubmissionMetadataSerializer(serializers.ModelSerializer):      
    patient = PatientSerializer()
    class Meta:
        model = Upload
        exclude = ('is_exome', 'is_paired', 'is_exome_father', 'is_paired_father', 'is_exome_mother', 'is_paired_mother', 'is_exome_sibling', 'is_paired_sibling',
        'sequence_file_location1', 'sequence_filename1', 'sequence_file_location2', 'sequence_filename2', 'bed_file_location', 'bed_filename', 'assembly',
        'father_sequence_file_location1', 'father_sequence_filename1', 'father_sequence_file_location2', 'father_sequence_filename2', 'father_bed_file_location', 'father_bed_filename', 'father_assembly',
        'mother_sequence_file_location1', 'mother_sequence_filename1', 'mother_sequence_file_location2', 'mother_sequence_filename2', 'mother_bed_file_location', 'mother_bed_filename', 'mother_assembly',
        'sibling_sequence_file_location1', 'sibling_sequence_filename1', 'sibling_sequence_file_location2', 'sibling_sequence_filename2', 'sibling_bed_file_location', 'sibling_bed_filename', 'sibling_assembly'
        )