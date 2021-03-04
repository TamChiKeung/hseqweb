from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from uploader.utils import api
from django.conf import settings

UPLOADER_PROJECT_UUID = getattr(settings, 'UPLOADER_PROJECT_UUID', 'cborg-j7d0g-nyah4ques5ww7pk')


def check_unique_email(sender, instance, **kwargs):
    if instance.email and sender.objects.filter(
            email=instance.email).exclude(username=instance.username).count():
        raise ValidationError(_("The email %(email)s already exists!") % {
            'email': instance.email
        })

pre_save.connect(check_unique_email, sender=User)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, primary_key=True, on_delete=models.CASCADE)
    organization = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=127, blank=True, null=True, unique=True)
    project_uuid = models.CharField(max_length=31, blank=True, null=True)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        project = api.groups().create(body={
            "group_class": "project",
            "name": instance.username,
            "owner_uuid": UPLOADER_PROJECT_UUID,
        }, ensure_unique_name=True).execute()
        profile, created = UserProfile.objects.get_or_create(
            user=instance)
        profile.project_uuid = project['uuid']
        profile.save()

post_save.connect(create_user_profile, sender=User)
