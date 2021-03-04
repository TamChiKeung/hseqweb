from rest_framework import serializers
from uploader.models import Upload
from django.contrib.auth.models import User

class UploadSerializer(serializers.ModelSerializer):

    token = serializers.CharField(max_length=127)
    class Meta:
        model = Upload
        fields = ['token', 'is_fasta', 'is_paired', 'col_uuid', 'status']
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
        self.instance = super(UploadSerializer, self).save()
        self.instance.user = self.user
        self.instance.save()
        return self.instance
