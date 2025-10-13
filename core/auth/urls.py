from django.urls import include
from django.urls import path

from core.restframework.routers import URLForceHyphenRouter

from .views import UserViewSet

router = URLForceHyphenRouter()
router.register("users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
