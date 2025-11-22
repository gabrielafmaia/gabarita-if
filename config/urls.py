from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", include("website.urls")),
    path("gabarita-if/", include("gabarita_if.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("select2/", include("django_select2.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)