from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', include('website.urls')),
    path('gabarita_if/', include('gabarita_if.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('users/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)