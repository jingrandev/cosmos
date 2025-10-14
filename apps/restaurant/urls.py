from django.urls import include
from django.urls import path

from core.restframework.routers import get_router

router = get_router()

urlpatterns = [
    path("", include(router.urls)),
]
