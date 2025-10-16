from rest_framework import mixins
from rest_framework import viewsets

from ..models import CustomerProfile
from ..serializers.customer import CustomerProfileModelSerializer


class RestaurantCustomerAPIViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        CustomerProfile.objects.select_related("user")
        .filter(
            dietary_preference__in=[
                CustomerProfile.DietaryPreference.VEGAN,
                CustomerProfile.DietaryPreference.VEGETARIAN,
            ]
        )
        .order_by("-id")
    )
    serializer_class = CustomerProfileModelSerializer
