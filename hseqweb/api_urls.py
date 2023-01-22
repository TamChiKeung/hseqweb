from django.urls import include, path
from django.contrib.auth.decorators import login_required
from hseqweb.apps.accounts.api_views import *
from hseqweb.apps.uploader.api_views import FullSubmissionView, \
    GetValidationRunsView, DownloadView, ListSubmissionView, \
    PatientInstanceView, PatientPedigreeView, PatientStartsWithView, \
    PatientView, SubmissionView, SubmitSubmissionView, SyncMetadataRDF, \
    SyncUpload, HPOClassStartsWithView
from hseqweb.apps.uploader.tus_views import TusUpload

urlpatterns = [
    path('sync', SyncUpload.as_view()),
    path('metadata/<col_id>', SyncMetadataRDF.as_view()),

    path('user/_login', Login.as_view()),
    path('user/_logout', UserLogoutView.as_view()),
    path("siteverify", VerifyTokenAPI.as_view()),
    path('user/_register', CreateUser.as_view()),
    path('user/_changepassword', ChangePasswordView.as_view()),
    path('user/_edit', ProfileUpdateView.as_view()),
    path('user', GetUser.as_view()),

    path('validationrun', GetValidationRunsView.as_view()),
    path('download/<path:col_uuid>/<path:filename>', DownloadView.as_view()),
    path('class/_startwith', HPOClassStartsWithView.as_view()),
    path('submission', ListSubmissionView.as_view()),
    path('submission/<int:id>', SubmissionView.as_view()),
    path('submission/_submit', SubmitSubmissionView.as_view()),
    path('submission/<int:id>/full', FullSubmissionView.as_view()),
    path('patient', PatientView.as_view()),
    path('patient/<int:id>', PatientInstanceView.as_view()),
    path('patient/<int:id>/pedigree', PatientPedigreeView.as_view()),
    path('patient/startswith', PatientStartsWithView.as_view()),

    path('tus_upload/', TusUpload.as_view(), name='tus_upload'),
    path('tus_upload/<uuid:resource_id>', TusUpload.as_view(), name='tus_upload_chunks'),

]
