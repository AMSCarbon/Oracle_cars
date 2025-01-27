from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path("", lambda _: redirect("/api/")),
    path("admin/", admin.site.urls),
    path("api/", include("car_api.urls")),
] + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)  # Apparently only for debug mode
