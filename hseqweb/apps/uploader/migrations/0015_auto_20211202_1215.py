# Generated by Django 3.0.6 on 2021-12-02 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0014_auto_20211201_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='upload',
            name='pedigree_snapshot',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name='upload',
            name='phenotypes_snapshot',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]