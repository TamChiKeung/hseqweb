from django.urls import include, path
from django.contrib.auth.decorators import login_required
from hseqweb.apps.accounts.api_views import *
from hseqweb.apps.uploader.api_views import GetValidationRunsView, DownloadView, ListSubmissionView, SubmissionView, SyncMetadataRDF, SyncUpload

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
    path('submission', ListSubmissionView.as_view()),
    path('submission/<int:id>', SubmissionView.as_view()),
]
