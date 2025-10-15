from django.urls import include
from django.urls import path

from core.restframework.routers import get_router

from .views.customer import RestaurantCustomerAPIViewSet

router = get_router()
router.register("customers", RestaurantCustomerAPIViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
