from django.urls import include
from django.urls import path

app_name = "v1"


endpoints = [
    path("", include("apps.api.urls")),
    path("auth/", include("core.auth.urls")),
]

urlpatterns = [
    path("v1/", include(endpoints)),
]
