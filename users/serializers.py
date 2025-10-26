from rest_framework import serializers
from .models import User


class InvitedUserSerializer(serializers.ModelSerializer):
    """Cериализатор используется для представления пользователей, которых пригласил текущий пользователь."""

    class Meta:
        model = User
        fields = ["id", "phone"]


class InvitedByUserSerializer(serializers.ModelSerializer):
    """Cериализатор используется для представления информации о пользователе, который пригласил текущего пользователя."""
    class Meta:
        model = User
        fields = ["id", "phone", "invaite_code"]


class UserSerializer(serializers.ModelSerializer):
    invited_users = InvitedUserSerializer(many=True, read_only=True)
    invited_by_user = InvitedByUserSerializer(source="invaited_by", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "invaite_code",
            "invaited_by_user",
            "created_at",
            "invaited_users",
        ]


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    invaited_by = serializers.CharField(
        max_length=6, required=False, allow_blank=True
    )


class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=4)
