from django.apps import apps
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_countries.serializer_fields import CountryField as CountrySerializer
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


# University Serializers -------------------------------------------------------


class UniversitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(name_only=True)

    class Meta:
        model = University
        fields = "__all__"


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
            "student",
            "user",
            "ssn",
        ]

    user = SimpleUserSerializer()
    student = serializers.SerializerMethodField(method_name="username")

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
        (OPEN, CLOSED, INACTIVE) = ("Open", "Closed", "Not Active")
        if pos.start_date > timezone.now().date():
            return INACTIVE
        if pos.capacity <= pos.filled:
            return CLOSED
        if pos.end_date < timezone.now().date():
            return CLOSED
        return OPEN


class BasePositionListSerializer(
    BasePositionSerializer,
):
    university_name = serializers.SerializerMethodField("get_university_name")
    university_id = serializers.SerializerMethodField("get_university_id")

    class Meta:
        model = Position
        exclude = [
            "description",
            "capacity",
            "filled",
            "request_count",
        ]

    def get_university_name(self, pos: Position):
        try:
            return pos.professor.university.name
        except:
            return None

    def get_university_id(self, pos: Position):
        try:
            return pos.professor.university.id
        except:
            return None


class BasePositionDetailSerializer(
    BasePositionSerializer,
):
    university = serializers.SerializerMethodField("get_university")

    class Meta:
        model = Position
        exclude = [
            "capacity",
            "filled",
            "request_count",
        ]

    def get_university(self, pos: Position):
        try:
            ser = UniversitySerializer(pos.professor.university)
            return ser.data
        except:
            return None


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
    professor = None

    class Meta(BasePositionListSerializer.Meta):
        exclude = [
            "description",
            "professor",
        ]


class AnonymousPositionDetailSerializer(
    BasePositionDetailSerializer,
):
    pass


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
    requests = serializers.SerializerMethodField("get_requests")
    professor = None

    class Meta:
        model = Position
        exclude = [
            "professor",
        ]

    def get_requests(self, pos: Position):
        reqs = getattr(pos, "position_requests", [])
        return RequestListSeralizer(reqs, many=True).data


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

    def validate(self, data):
        errors = {}
        if data["position_end_date"] < data["position_start_date"]:
            errors["position_end_date"] = (
                "Position end date must be after position start date."
            )
        if data["end_date"] < data["start_date"]:
            errors["end_date"] = "end date must be after start date."
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        validated_data["professor_id"] = self.context["professor_id"]
        return super().create(validated_data)


# Request Serializers ----------------------------------------------------------


class StudentCreateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = (
            "position_id",
            "cover_letter",
        )

    position_id = serializers.IntegerField()

    def create(self, validated_data):
        validated_data["student"] = Student.objects.get(pk=self.context["student_id"])
        validated_data["position"] = get_object_or_404(
            Position, pk=validated_data["position_id"]
        )
        return super().create(validated_data)


class RequestListSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Request
        exclude = [
            "cover_letter",
            "student",
            "share_with_others",
        ]


class ProfessorRequestUpdateSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ("status",)


class StudentRequestUpdateSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ("share_with_others",)


class StudentRequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ("status", "position", "date_applied", "cover_letter")


class ProfessorRequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ("status", "position", "date_applied", "cover_letter")


class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = (
            "date_applied",
            "student",
            "status",
        )

    student = StudentGetListSerializer()


# CV Serializers ---------------------------------------------------------------


class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        exclude = []
