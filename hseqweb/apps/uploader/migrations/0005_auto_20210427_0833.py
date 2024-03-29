# Generated by Django 3.0.6 on 2021-04-27 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0004_upload_is_exome'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='upload',
            name='is_fasta',
        ),
        migrations.AddField(
            model_name='upload',
            name='is_trio',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='upload',
            name='error_message',
            field=models.TextField(blank=True, null=True),
        ),
    ]
