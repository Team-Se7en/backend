from django.conf import settings
from django.apps import apps
from .models import *
from rest_framework import serializers


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


class ProfessorSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()

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
            user_serializer = SimpleUserSerializer(
                user_instance, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        except KeyError:
            pass
        return super().update(instance, validated_data)


class ReadTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["label"]


class ReadPositionSerializer(serializers.ModelSerializer):
    professor = ProfessorSerializer()
    tags = serializers.SlugRelatedField(
        slug_field="label", many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Position
        fields = "__all__"

    def get_professor_name(self, position: Position):
        return (
            f"{position.professor.user.first_name} {position.professor.user.last_name}"
        )


class CreatePositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        # fields = "__all__"
        exclude = ("professor",)

    def create(self, validated_data):
        validated_data["professor_id"] = self.context["professor_id"]
        return super().create(validated_data)


class ReadTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["label"]


class ReadPositionSerializer(serializers.ModelSerializer):
    professor = ProfessorSerializer()
    tags = serializers.SlugRelatedField(
        slug_field="label", many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Position
        fields = "__all__"

    def get_professor_name(self, position: Position):
        return (
            f"{position.professor.user.first_name} {position.professor.user.last_name}"
        )


class CreatePositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        # fields = "__all__"
        exclude = ("professor",)

    def create(self, validated_data):
        validated_data["professor_id"] = self.context["professor_id"]
        return super().create(validated_data)


class StudentGetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        # fields need to be changed
        fields = [
            "id",
            "student_name",
            "university_name",
            "user",
        ]

    user = SimpleUserSerializer()
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
            "user",
            "ssn",
        ]

    user = SimpleUserSerializer()
    user_profile = serializers.SerializerMethodField(method_name="username")

    def username(self, student: Student):
        return student.user.id

    def update(self, instance, validated_data):
        try:
            user_data = validated_data.pop("user")
            user_instance = instance.user
            user_serializer = SimpleUserSerializer(
                user_instance, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        except KeyError:
            pass
        return super().update(instance, validated_data)
