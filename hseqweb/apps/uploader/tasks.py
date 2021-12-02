import subprocess
import os
import json

from celery import task
from hseqweb.apps.uploader.utils import remove_file

from uploader.models import Upload
from django.conf import settings

@task
def upload_to_arvados(project_uuid, upload_pk, upload_config):
    cmd = [
        'hguploader',
        '--uploader-project', project_uuid,
        '--metadata-file', upload_config['metadata_file'],
        '--pedigree-file', upload_config['ped_file'],
        '--upload-id', str(upload_pk)]

    upload = Upload.objects.get(pk=upload_pk)

    cmd += ['--sequence-read1', upload_config['sequence_file']]
    print('sequence_file2:', upload_config['sequence_file2'], upload.is_paired, upload.is_exome)
    if upload_config['sequence_file2'] and upload.is_paired:
        cmd += ['--sequence-read2', upload_config['sequence_file2']]
    if upload_config['bed_file'] and upload.is_exome:
        cmd += ['--bed-file', upload_config['bed_file']]
    if upload_config['original_bed_file_grch37'] and upload.is_exome:
        cmd += ['--bed-file-grch37', upload_config['original_bed_file_grch37']]

    
    if upload_config['father_sequence_file']:
        cmd += ['--father-sequence-read1', upload_config['father_sequence_file']]
    if upload_config['father_sequence_file2'] and upload.is_paired_father:
        cmd += ['--father-sequence-read2', upload_config['father_sequence_file2']]
    if upload_config['father_bed_file'] and upload.is_exome_father:
        cmd += ['--father-bed-file', upload_config['father_bed_file']]
    if upload_config['father_original_bed_file_grch37'] and upload.is_exome_father:
        cmd += ['--father-bed-file-grch37', upload_config['father_original_bed_file_grch37']]

    
    if upload_config['mother_sequence_file']:
        cmd += ['--mother-sequence-read1', upload_config['mother_sequence_file']]
    if upload_config['mother_sequence_file2'] and upload.is_paired_mother:
        cmd += ['--mother-sequence-read2', upload_config['mother_sequence_file2']]
    if upload_config['bed_file'] and upload.is_exome_mother:
        cmd += ['--mother-bed-file', upload_config['mother_bed_file']]
    if upload_config['mother_original_bed_file_grch37'] and upload.is_exome_mother:
        cmd += ['--mother-bed-file-grch37', upload_config['mother_original_bed_file_grch37']]

    if upload_config['sibling_sequence_file']:
        cmd += ['--sibling-sequence-read1', upload_config['sibling_sequence_file']]
    if upload_config['sibling_sequence_file2'] and upload.is_paired_sibling:
        cmd += ['--sibling-sequence-read2', upload_config['sibling_sequence_file2']]
    if upload_config['sibling_bed_file'] and upload.is_exome_sibling:
        cmd += ['--sibling-bed-file', upload_config['sibling_bed_file']]
    if upload_config['sibling_original_bed_file_grch37'] and upload.is_exome_sibling:
        cmd += ['--sibling-bed-file-grch37', upload_config['sibling_original_bed_file_grch37']]
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
        print(col)
        col = json.loads(col[-1])
        Upload.objects.filter(pk=upload_pk).update(
            status=Upload.UPLOADED, col_uuid=col['uuid'])

        remove_file(upload_config['metadata_file'])
        remove_file(upload_config['ped_file'])

        remove_file(upload_config['sequence_file'])
        remove_file(upload_config['sequence_file2'])
        remove_file(upload_config['bed_file'])
        remove_file(upload_config['original_bed_file_grch37'])

        remove_file(upload_config['father_sequence_file'])
        remove_file(upload_config['father_sequence_file2'])
        remove_file(upload_config['father_bed_file'])
        remove_file(upload_config['father_original_bed_file_grch37'])

        remove_file(upload_config['mother_sequence_file'])
        remove_file(upload_config['mother_sequence_file2'])
        remove_file(upload_config['mother_bed_file'])
        remove_file(upload_config['mother_original_bed_file_grch37'])

        remove_file(upload_config['sibling_sequence_file'])
        remove_file(upload_config['sibling_sequence_file2'])
        remove_file(upload_config['sibling_bed_file'])
        remove_file(upload_config['sibling_original_bed_file_grch37'])
