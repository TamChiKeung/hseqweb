from rest_framework import serializers
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


class UploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Upload
        fields = ('__all__')

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
    class Meta:
        model = Upload
        fields = ('id', 'is_exome', 'is_paired', 'is_trio', 'patient_id', 'col_uuid', 'status', 'date', 
        'error_message', 'collection', 'name', 'token', 'files', 'output_files', 'output_status',
        'output_collection', 'out_col_uuid', 'metadata_filename', 'sequence_filename')