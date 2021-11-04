from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from hseqweb.apps.uploader.serializers import PatientSerializer, PatientShortSerializer, UploadCreateSerializer, UploadDetailSerializer
from uploader.models import Upload
from hseqweb.apps.uploader.utils import collection_content
from uploader.serializers import UploadSerializer
from rdflib import Graph
from django.db.models import Count

from django.http import StreamingHttpResponse, Http404

from uploader.utils import api, parse_manifest_text
import arvados.collection
import logging


logger = logging.getLogger(__name__)

class SyncUpload(CreateAPIView):

    serializer_class = UploadCreateSerializer
    
class SyncMetadataRDF(APIView):
    """
    Sync's metadata with triple store 
    """

    def post(self, request, col_id, format=None):
        try:
            res_uri = settings.ARVADOS_COL_BASE_URI + col_id + "/metadata.rdf"
            g = Graph()
            g.parse(res_uri)
            insert(g)
            return Response()
        except Exception as e:
            logger.exception("message")


class GetValidationRunsView(APIView):
    """ 
    Get the results of validation runs 
    """

    permission_classes = [AllowAny]
    def get(self, request, format='json'):
        data = {}
        wg_col_uuid = 'cborg-4zz18-0l7m048bpsivyzb'
        ex_col_uuid = 'cborg-4zz18-szhgxdetn190fug'
        tr_col_uuid = 'cborg-4zz18-pv7ev6qeu3d23oj'
        data['wg_col_uuid'] = wg_col_uuid
        data['ex_col_uuid'] = ex_col_uuid
        data['tr_col_uuid'] = tr_col_uuid
        col = api.collections().get(uuid=wg_col_uuid).execute()
        wg_files = parse_manifest_text(col['manifest_text'])
        data['wg_files'] = wg_files
        col = api.collections().get(uuid=ex_col_uuid).execute()
        ex_files = parse_manifest_text(col['manifest_text'])
        data['ex_files'] = ex_files
        col = api.collections().get(uuid=tr_col_uuid).execute()
        tr_files = parse_manifest_text(col['manifest_text'])
        data['tr_files'] = tr_files
        return Response(data, status=status.HTTP_200_OK)

class DownloadView(APIView):

    permission_classes = [AllowAny]
    def get(self, request, col_uuid, filename, format=None):
        response = StreamingHttpResponse(collection_content(col_uuid, filename))
        response['Content-Disposition'] = \
            f'attachment; filename="{filename}"'
        return response

class ListSubmissionView(APIView):

    def get(self, request):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        result = []
        total = 0
        user = self.request.user
        if user.is_authenticated:
            result = Upload.objects.filter(user=user).order_by('-date')[offset:(offset + limit)]
            total = Upload.objects.filter(user=user).count()
        else:
            result = Upload.objects.filter(user__isnull=True).order_by('-date')[offset:(offset + limit)]
            total = Upload.objects.filter(user__isnull=True).count()
            
        data = {
            'result': UploadSerializer(result, many=True).data,
            'total': total
        }
        return Response(data, status=status.HTTP_200_OK)

class SubmissionView(APIView):

    def get(self, request, id):
        object = self.get_object(id)
        if object.user_id != request.user.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(UploadDetailSerializer(object).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        upload = self.get_object(id)
        if upload.status != Upload.UPLOADED:
            return Response(status=status.HTTP_404_NOT_FOUND)
        api.collections().delete(uuid=upload.col_uuid).execute()
        upload.delete()
        return Response(status=status.HTTP_200_OK)

    def get_object(self, id):
        return Upload.objects.get(id=id)

class PatientView(APIView):
    
    serializer = PatientSerializer()

    def post(self, request, format=None):
        try:
            patient = None
            patient = self.serializer.add_or_update(request.data, request.user)

            return Response(PatientShortSerializer(patient).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("message")

    def get(self, request):
        result = self.serializer.find()
        return Response(PatientShortSerializer(result, many=True).data, status=status.HTTP_200_OK)

class PatientStartsWithView(APIView):
    
    serializer = PatientShortSerializer()

    def get(self, request):
        term = request.GET.get('term', '')
        limit = int(request.GET.get('limit', 10))
        result = self.serializer.find_by_identifier_startsWith(term, limit)
        return Response(PatientShortSerializer(result, many=True).data, status=status.HTTP_200_OK)