from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from licenses.admin import admin_site  # 👈 tu importes ton admin personnalisé

urlpatterns = [
    path('admin/', admin_site.urls),  # 👈 tu l'utilises ici à la place de admin.site.urls
    path('', include('licenses.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
