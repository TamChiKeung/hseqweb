import subprocess
import os
import json

from celery import task
from celery.schedules import crontab
from celery.task import periodic_task

from uploader.models import Upload
from .galaxy import create_folder, upload, clean_folder
from django.conf import settings

@task
def upload_to_arvados(project_uuid, upload_pk, sequence_file, sequence_file2, bed_file, metadata_file):
    cmd = [
        'hguploader',
        '--uploader-project', project_uuid,
        '--metadata-file', metadata_file]
    upload = Upload.objects.get(pk=upload_pk)
    cmd += ['--sequence-read1', sequence_file]
    if sequence_file2 and upload.is_paired:
        cmd += ['--sequence-read2', sequence_file2]
    if bed_file and upload.is_exome:
        cmd += ['--bed-file', bed_file]
    cmd.append('--no-sync')
    print(" ".join(cmd))
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        error_message=str(result.stderr.decode('utf-8'))
        Upload.objects.filter(pk=upload_pk).update(
            status=Upload.ERROR,
            error_message=error_message)
    else:
        col = str(result.stdout.decode('utf-8')).splitlines()
        col = json.loads(col[-1])
        Upload.objects.filter(pk=upload_pk).update(
            status=Upload.UPLOADED, col_uuid=col['uuid'])
        os.remove(sequence_file)
        os.remove(metadata_file)
        if sequence_file2:
            os.remove(sequence_file2)
