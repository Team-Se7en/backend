from django.conf import settings
from django.apps import apps
from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


class ProfessorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Professor
        fields = [
            "id",
            "user",
            "university",
            "department",
            "birth_date",
        ]

    def update(self, instance, validated_data):
        try:
            user_data = validated_data.pop("user")
            user_instance = instance.user
            user_serializer = UserSerializer(
                user_instance, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        except KeyError:
            pass
        return super().update(instance, validated_data)


class StudentGetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        # fields need to be changed
        fields = [
            "id",
            "user",
            "student_name",
            "university_name",
        ]

    student_name = serializers.SerializerMethodField(method_name="get_student_name")

    def get_student_name(self, student: Student) -> str:
        return student.user.first_name + " " + student.user.last_name


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        # fields need to be changed
        fields = [
            "university_name",
            "user_profile",
            "ssn",
        ]

    user_profile = serializers.SerializerMethodField(method_name="username")

    def username(self, student: Student):
        return student.user.id
