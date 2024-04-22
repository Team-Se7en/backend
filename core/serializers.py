from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from djoser.serializers import UserCreateSerializer as BaseUCS
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

class TokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["is_student"] = self.user.is_student

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


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
