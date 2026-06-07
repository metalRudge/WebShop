"""Root URL configuration for the webshop project.

Phase 1 wires the project root to the `MyShop` app, which serves the
Hello World project-start page. Later phases will mount additional URL
namespaces here (catalog, cart, checkout, auth, admin dashboard).
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('MyShop.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)