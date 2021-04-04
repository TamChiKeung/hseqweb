from django.urls import include, path
from django.contrib.auth.decorators import login_required
from uploader.views import *
from hseqweb.apps.uploader.tus_views import TusUpload

urlpatterns = [
    path('', login_required(UploadCreateView.as_view()), name='uploader-upload'),
    path('tus_upload/', TusUpload.as_view(), name='tus_upload'),
    path('tus_upload/<uuid:resource_id>', TusUpload.as_view(), name='tus_upload_chunks'),

    path('view/<int:pk>', login_required(UploadDetailView.as_view()), name='uploader-view'),
    path('list', login_required(UploadListView.as_view()), name='uploader-list'),

    path('download/<path:col_uuid>/<path:filename>',
         DownloadView.as_view() ,
         name='uploader-download'),
    path('validations',
         ValidationRunsView.as_view() ,
         name='uploader-validations')
]
