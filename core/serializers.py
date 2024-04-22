from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUCS
from rest_framework import serializers

User = get_user_model()


class UserCreateSerializer(BaseUCS):
    class Meta(BaseUCS.Meta):
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_student",
        )
