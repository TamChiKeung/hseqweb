import logging
import shutil
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

logger = logging.getLogger(__name__)

HTTP_PROT = 'http://'
VIRTUOSO_HOST = getattr(settings, 'VIRTUOSO_HOST')
VIRTUOSO_SPARQL_PORT = getattr(settings, 'VIRTUOSO_SPARQL_PORT')
VIRTUOSO_USER = getattr(settings, 'VIRTUOSO_USER')
VIRTUOSO_PWD = getattr(settings, 'VIRTUOSO_PWD')
RDF_GRAPH_URI = getattr(settings, 'RDF_GRAPH_URI')
SPARQL_ENDPOINT_URL = HTTP_PROT + VIRTUOSO_HOST + ":" + str(VIRTUOSO_SPARQL_PORT) + "/sparql"

class Command(BaseCommand):
    help = 'upload rdf files'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', type=str, help='source rdf file that needs to be uploaded', )    
                
    def handle(self, *args, **options):
        source_file = options['file']

        try:
            curd_endpoint = SPARQL_ENDPOINT_URL + "-graph-crud-auth?graph-uri=" + RDF_GRAPH_URI
            CMD = "time curl --digest --user " + VIRTUOSO_USER + ":" + VIRTUOSO_PWD + " --verbose -X POST \
                --url " + curd_endpoint + " \
                --upload-file '" + source_file + "' \
                --write-out '%{url_effective};%{http_code};%{time_total};%{time_namelookup};%{time_connect};%{size_download};%{speed_download}\\n' \
                && echo `date +%Y-%m-%d.%H%M.%S.%N` Processing file '" + source_file + "' completed with exit status:$e_status at `date +%Y-%m-%d.%H%Mhrs:%S.%N`;"
            print("command:", CMD)
            process = subprocess.Popen(CMD, stdout=subprocess.PIPE, text=True, shell=True)
            for line in process.stdout:
                print(line.strip())
            
        except Exception as e:
            logger.exception("message")