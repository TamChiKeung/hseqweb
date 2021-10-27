from rest_framework import serializers
from rest_framework_recaptcha.fields import ReCaptchaField
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

from accounts.models import UserProfile


class ReCaptchaSerializer(serializers.Serializer):
    recaptcha = ReCaptchaField()

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'organization')

    def __init__(self, *args, **kwargs):
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

    def get_first_name(self, obj):
        return self.instance.user.first_name  

    def get_last_name(self, obj):
        return self.instance.user.last_name  

    def save(self, *args, **kwargs):
        super(UserProfileSerializer, self).save(*args, **kwargs)
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        self.instance.user.first_name = first_name
        self.instance.user.last_name = last_name
        self.instance.user.save()
        return self.instance



class UserShortSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'organization')
        
    def get_organization(self, obj):
        return self.instance.userprofile.organization  

class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)