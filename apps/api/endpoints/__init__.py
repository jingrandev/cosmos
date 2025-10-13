from django.urls import include
from django.urls import path

app_name = "api"


endpoints = [
    path("", include("apps.api.endpoints.v1")),
]

urlpatterns = [
    path("api/", include(endpoints)),
]
