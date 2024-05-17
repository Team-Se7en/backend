from django.apps import apps
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_countries.serializer_fields import CountryField as CountrySerializer
from eduportal.models import Position
from rest_framework import serializers
from django.db.models import Avg

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


class SimpleUniversitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(name_only=True)

    class Meta:
        model = University
        fields = "__all__"


class UniversitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(name_only=True)
    position_count = serializers.IntegerField(read_only=True)
    recent_positions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = University
        fields = "__all__"

    def get_recent_positions(self, obj):
        poses = (
            Position.objects.filter(professor__university=obj)
            .select_related("professor", "professor__user", "professor__university")
            .prefetch_related("tags", "tags2")
        )

        poses = poses.filter(start_date__lte=timezone.now()).order_by("-start_date")[:5]
        return BasePositionListSerializer(poses, many=True).data


class LandingUniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = [
            "id",
            "name",
            "icon",
            "rank",
        ]


# Student Serializers ----------------------------------------------------------


class StudentGetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

    major = serializers.CharField(source="get_major_display")

    user = UserDetailSerializer()


class StudentRequestGetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

    user = SimpleUserSerializer()


class OwnStudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        # fields need to be changed
        fields = ["university", "student", "user", "ssn", "major", "profile_image"]

    user = SimpleUserSerializer()
    student = serializers.SerializerMethodField(method_name="username")
    profile_image = serializers.ImageField()

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


class LandingStudentSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    rank = serializers.IntegerField()
    accepted_request_count = serializers.IntegerField()

    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "rank",
            "accepted_request_count",
        ]

    def get_first_name(self, obj: Student):
        return obj.user.first_name

    def get_last_name(self, obj: Student):
        return obj.user.last_name


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
            "major",
            "profile_image",
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


class LandingProfessorSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    rank = serializers.IntegerField()
    accepted_request_count = serializers.IntegerField()

    class Meta:
        model = Professor
        fields = [
            "id",
            "first_name",
            "last_name",
            "rank",
            "accepted_request_count",
        ]

    def get_first_name(self, obj: Professor):
        return obj.user.first_name

    def get_last_name(self, obj: Professor):
        return obj.user.last_name


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
            ser = SimpleUniversitySerializer(pos.professor.university)
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


class ProfessorPositionFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = (
            "title",
            "start_date",
            "end_date",
            "position_start_date",
            "position_end_date",
            "university_name",
            "fee",
            "capacity",
            "request_count",
            "tags",
        )

    university_name = serializers.SerializerMethodField()

    def get_university_name(self, pos: Position):
        if pos.professor.university is not None:
            return pos.professor.university.name
        return None


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


class StudentRequestListSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Request
        exclude = [
            "cover_letter",
            "share_with_others",
        ]

    student = StudentRequestGetListSerializer()


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


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        exclude = [
            "cv",
        ]


class EducationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationHistory
        exclude = [
            "cv",
        ]


class ProjectExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectExperience
        exclude = [
            "cv",
        ]


class HardSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = HardSkill
        exclude = [
            "cv",
        ]


class LanguageSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageSkill
        exclude = [
            "cv",
        ]


# Notification Serializers -----------------------------------------------------


class NotifPositionSerializer(serializers.ModelSerializer):
    university_name = serializers.SerializerMethodField()

    class Meta:
        model = Position
        exclude = []

    def get_university_name(self, obj: Position):
        try:
            return obj.professor.university.name
        except:
            return None


class NotifStudentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    university_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        exclude = []

    def get_name(self, obj: Student):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_university_name(self, obj: Student):
        try:
            return obj.university.name
        except:
            return None


class NotificationSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        exclude = []

    def get_position(self, obj: Notification):
        request = self.get_model_item(obj, Request)

        if request:
            return NotifPositionSerializer(request.position).data
        else:
            position = self.get_model_item(obj, Position)

            if position:
                return NotifPositionSerializer(position).data
        return None

    def get_student(self, obj: Notification):
        request = self.get_model_item(obj, Request)

        if request:
            return NotifStudentSerializer(request.student).data
        return None

    def get_model_item(self, obj: Notification, model):
        pass
        item: NotificationItem
        for item in obj.items.all():
            if isinstance(item.content_object, model):
                return item.content_object
        return None


# Top 5 Student Seralizer ------------------------------------------------------


class UniversityLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["name", "country", "city"]

    country = CountrySerializer(name_only=True)


class Top5StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("student_name", "major", "university", "gpa")

    university = UniversityLocationSerializer()
    gpa = serializers.SerializerMethodField()
    major = serializers.CharField(source="get_major_display")
    student_name = serializers.SerializerMethodField()

    def get_student_name(self, student: Student):
        return " ".join(
            [
                student.user.first_name.lower().capitalize(),
                student.user.last_name.lower().capitalize(),
            ]
        )

    def get_gpa(self, student: Student):
        student_cv = CV.objects.filter(student=student).prefetch_related(
            "education_histories"
        )
        if not student_cv:
            return 0
        return (
            student_cv.filter(education_histories__end_date__isnull=False)
            .annotate(gpa_avg=Avg("education_histories__grade"))
            .first()
            .gpa_avg
        )


class Top5ProfessorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = (
            "professor_name",
            "major",
            "university",
            "department",
            "project_num",
        )

    project_num = serializers.IntegerField()
    university = UniversityLocationSerializer()
    major = serializers.CharField(source="get_major_display")
    professor_name = serializers.SerializerMethodField()

    def get_professor_name(self, professor: Professor):
        return " ".join(
            [
                professor.user.first_name.lower().capitalize(),
                professor.user.last_name.lower().capitalize(),
            ]
        )
