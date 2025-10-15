from rest_framework import serializers

from ..models import CustomerProfile


class CustomerProfileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = [
            "customer_name",
            "dietary_preference",
            "favorite_dishes",
        ]

    customer_name = serializers.SerializerMethodField()

    def get_customer_name(self, obj) -> str:
        if obj.user is None:
            return "Anonymous"
        full_name = f"{obj.user.first_name} {obj.user.last_name}"
        if full_name.strip() == "":
            return obj.user.username
        return full_name
