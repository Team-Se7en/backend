from django.apps import apps
from django.conf import settings
from django.utils import timezone
from eduportal.models import Position
from rest_framework import serializers

from .models import *
from .utils.views import get_user_type

# User Serializers -------------------------------------------------------------


class SimpleProfessorSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = Professor
        fields = "__all__"


class SimpleStudentSerializer(
    serializers.ModelSerializer,
):
    status = serializers.CharField(source="get_status_display")
    major = serializers.CharField(source="get_major_display")
    gender = serializers.CharField(source="get_gender_display")

    class Meta:
        model = Student
        fields = "__all__"


class SimpleUserSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


class UserDetailSerializer(
    serializers.ModelSerializer,
):
    user_type = serializers.SerializerMethodField("get_user_type")
    professor = SimpleProfessorSerializer()
    student = SimpleStudentSerializer()

    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        exclude = [
            "password",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "is_student",
            "groups",
            "user_permissions",
        ]

    def get_fields(self):
        fields = super().get_fields()
        for field_name, field in fields.items():
            field.allow_null = True
        return fields

    def get_user_type(self, user):
        return get_user_type(self.context["request"])


# Student Serializers ----------------------------------------------------------


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


class OwnStudentProfileSerializer(serializers.ModelSerializer):
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

            class Meta:
                model = Tag
                exclude = ()

        return super().update(instance, validated_data)


# Professor Serializers --------------------------------------------------------


class ProfessorSerializer(
    serializers.ModelSerializer,
):
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

            class Meta:
                model = Tag
                exclude = ()

        return super().update(instance, validated_data)


# Position Serializers ---------------------------------------------------------


class ReadTagSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = Tag
        fields = ["label"]


class BasePositionSerializer(
    serializers.ModelSerializer,
):
    status = serializers.SerializerMethodField("get_status")
    professor = ProfessorSerializer()
    tags = serializers.SlugRelatedField(
        slug_field="label", many=True, queryset=Tag.objects.all()
    )

    def get_status(self, pos: Position) -> str:
        (OPEN, CLOSED) = ("Open", "Closed")
        if pos.capacity <= pos.filled:
            return CLOSED
        if pos.deadline < timezone.now().date():
            return CLOSED
        return OPEN


class BasePositionListSerializer(
    BasePositionSerializer,
):
    class Meta:
        model = Position
        exclude = [
            "description",
            "capacity",
            "filled",
            "request_count",
        ]


class BasePositionDetailSerializer(
    BasePositionSerializer,
):
    class Meta:
        model = Position
        exclude = [
            "capacity",
            "filled",
            "request_count",
        ]


class StudentStatusMixin:
    def get_remaining(self, pos: Position):
        return pos.capacity - pos.filled

    def get_status(self, pos: Position):
        my_requests = getattr(pos, "my_request", [])
        if my_requests:
            my_req = my_requests[0]
            return my_req.get_status_display()
        return super().get_status(pos)


class AnonymousPositionListSerializer(
    BasePositionListSerializer,
):
    pass


class StudentPositionListSerializer(
    StudentStatusMixin,
    BasePositionListSerializer,
):
    remaining = serializers.SerializerMethodField("get_remaining")


class ProfessorPositionListSerializer(
    BasePositionListSerializer,
):
    pass


class OwnerPositionListSerializer(
    BasePositionListSerializer,
):
    class Meta(BasePositionListSerializer.Meta):
        exclude = [
            "description",
        ]


class StudentPositionDetailSerializer(
    StudentStatusMixin,
    BasePositionDetailSerializer,
):
    remaining = serializers.SerializerMethodField("get_remaining")


class ProfessorPositionDetailSerializer(
    BasePositionDetailSerializer,
):
    pass


class OwnerPositionDetailSerializer(
    BasePositionDetailSerializer,
):
    class Meta:
        model = Position
        fields = "__all__"


class PositionUpdateSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = Position
        exclude = [
            "professor",
            "request_count",
            "filled",
        ]

    def create(self, validated_data):
        validated_data["professor_id"] = self.context["professor_id"]
        return super().create(validated_data)


# Request Serializers ----------------------------------------------------------


class StudentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ("status", "position", "date_applied", "cover_letter")

    def create(self, validated_data):
        # Extract the user from the request
        user = self.context["request"].user

        # Get the student associated with the user
        student = Student.objects.get(user=user)
        validated_data["student"] = student

        # Create the request
        request = Request.objects.create(**validated_data)

        return request
