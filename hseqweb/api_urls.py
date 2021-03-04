from django.urls import path, include

urlpatterns = [
    path('uploader/', include('uploader.api_urls')),
]
