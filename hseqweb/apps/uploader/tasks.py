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
def upload_to_arvados(project_uuid, upload_pk, sequence_file, sequence_file2, metadata_file):
    cmd = [
        'cborguploader',
        '--uploader-project', project_uuid,
        '--metadata-file', metadata_file]
    upload = Upload.objects.get(pk=upload_pk)
    if upload.is_fasta:
        cmd += ['--sequence-fasta', sequence_file]
    else:
        cmd += ['--sequence-read1', sequence_file]
        if sequence_file2 and upload.is_paired:
            cmd += ['--sequence-read2', sequence_file2]
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

# Every 12th hour
@periodic_task(run_every=crontab(minute=0, hour='11,23'))
def run_pangenome_analysis():
    logger = run_pangenome_analysis.get_logger()
    cmd = 'bh20-seq-analyzer --kickoff'
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, shell=True)
    for line in process.stdout:
        logger.info(line.strip())

# Every 3rd hour
@periodic_task(run_every=crontab(minute=0, hour='2,14'))
def sync_results2galaxy():
    logger = sync_results2galaxy.get_logger()
    clean_folder()
    folder_id=settings.GALAXY_PANGENOME_RESULT_DIR
    collection_url = settings.ARVADOS_COL_BASE_URI + "/" + settings.PANGENOME_RESULT_UUID
    
    cwl_output_url = collection_url + "/" + 'cwl.output.json'
    logger.info("uploading: %s", cwl_output_url)
    upload(cwl_output_url, folder_id)

    mergedmetadata_ttl_url = collection_url + "/" + 'mergedmetadata.ttl'
    logger.info("uploading: %s", mergedmetadata_ttl_url)
    upload(mergedmetadata_ttl_url, folder_id)

    readsMergeDedup_url = collection_url + "/" + 'readsMergeDedup.fasta'
    logger.info("uploading: %s", readsMergeDedup_url)
    upload(readsMergeDedup_url, folder_id)

    readsMergeDedup_gfa_url = collection_url + "/" + 'readsMergeDedup.gfa'
    logger.info("uploading: %s", readsMergeDedup_gfa_url)
    upload(readsMergeDedup_gfa_url, folder_id)

    readsMergeDedup_odgi_url = collection_url + "/" + 'readsMergeDedup.odgi'
    logger.info("uploading: %s", readsMergeDedup_odgi_url)
    upload(readsMergeDedup_odgi_url, folder_id)

    readsMergeDedup_png_url = collection_url + "/" + 'readsMergeDedup.png'
    logger.info("uploading: %s", readsMergeDedup_png_url)
    upload(readsMergeDedup_png_url, folder_id)

    readsMergeDedup_ttl_xz_url = collection_url + "/" + 'readsMergeDedup.ttl.xz'
    logger.info("uploading: %s", readsMergeDedup_ttl_xz_url)
    upload(readsMergeDedup_ttl_xz_url, folder_id)

    logger.info('Finished syncing pangenomic analysis results to galaxy server')
