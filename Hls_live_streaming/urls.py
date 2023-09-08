from django.contrib import admin
from django.urls import path
from Live_Stream import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',views.home),
    path('viewers',views.viewers),
    path('admin/', admin.site.urls),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

