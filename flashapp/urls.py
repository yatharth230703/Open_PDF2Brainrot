from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    # delegate all root URLs to the viewer app
    path('', include('viewer.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)