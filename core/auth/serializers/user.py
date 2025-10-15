from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Custom user create serializer for Djoser.
    """

    class Meta(BaseUserCreateSerializer.Meta):
        model = User

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]


class UserSerializer(BaseUserSerializer):
    """
    Custom user serializer for Djoser.
    """

    class Meta(BaseUserSerializer.Meta):
        model = User

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
        ]

        read_only_fields = ["id", "is_active", "is_staff"]
