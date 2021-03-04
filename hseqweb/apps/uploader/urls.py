from django.urls import include, path
from django.contrib.auth.decorators import login_required
from uploader.views import *

urlpatterns = [
    path('', login_required(UploadCreateView.as_view()), name='uploader-upload'),
    path('view/<int:pk>', login_required(UploadDetailView.as_view()), name='uploader-view'),
    path('list', login_required(UploadListView.as_view()), name='uploader-list'),

    path('submission', submission_list_view , name='uploader-submission_list'),
    path('submission/<path:iri>', submission_details_view , name='uploader-submission_details')
]
