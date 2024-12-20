from django.apps import apps
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_countries.serializer_fields import CountryField as CountrySerializer
from eduportal.models import Position
from ticketing_system.models import *
from rest_framework import serializers
from django.db.models import Avg

from pprint import pprint

from .models import *
from .utils.views import get_user_type


# Profile Image Serializer -----------------------------------------------------


class StudentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentImage
        fields = ["image"]


class ProfessorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessorImage
        fields = ["image"]


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
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    status = serializers.CharField(source="get_status_display")
    major = serializers.CharField(source="get_major_display")
    gender = serializers.CharField(source="get_gender_display")

    class Meta:
        model = Student
        fields = "__all__"

    def get_first_name(self, student: Student):
        return student.user.first_name

    def get_last_name(self, student: Student):
        return student.user.last_name


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


class UserDetailSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    professor = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()

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
        if user.is_anonymous:
            return "Anonymous"
        elif user.is_student:
            return "Student"
        else:
            return "Professor"

    def get_professor(self, user):
        if (not user.is_authenticated) or user.is_student:
            return None
        return SimpleProfessorSerializer(user.professor).data

    def get_student(self, user):
        if (not user.is_authenticated) or (not user.is_student):
            return None
        return SimpleStudentSerializer(user.student).data


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
    image = StudentImageSerializer(read_only=True)
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
        fields = [
            "university",
            "student",
            "user",
            "ssn",
            "major",
            "interest_tags",
            "image",
        ]

    image = StudentImageSerializer(read_only=True)
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
    image = ProfessorImageSerializer(read_only=True)

    class Meta:
        model = Professor
        fields = [
            "id",
            "user",
            "university",
            "department",
            "birth_date",
            "major",
            "image",
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

    def get_my_request(self, pos: Position):
        my_requests = getattr(pos, "my_request", [])
        if my_requests:
            my_req = my_requests[0]
            return RequestListSeralizer(my_req).data
        return None


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
    remaining = serializers.SerializerMethodField()
    my_request = serializers.SerializerMethodField()


class ProfessorPositionDetailSerializer(
    BasePositionDetailSerializer,
):
    pass


class OwnerPositionRequestDetailSerializer(
    serializers.ModelSerializer,
):
    student = SimpleStudentSerializer()
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = Request
        fields = "__all__"


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
        return OwnerPositionRequestDetailSerializer(reqs, many=True).data


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
            "id",
            "university_id",
            "status",
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

    status = serializers.SerializerMethodField("get_status")
    university_name = serializers.SerializerMethodField()
    university_id = serializers.SerializerMethodField()

    def get_status(self, pos: Position) -> str:
        (OPEN, CLOSED, INACTIVE) = ("Open", "Closed", "Not Active")
        if pos.start_date > timezone.now().date():
            return INACTIVE
        if pos.capacity <= pos.filled:
            return CLOSED
        if pos.end_date < timezone.now().date():
            return CLOSED
        return OPEN

    def get_university_id(self,pos:Position):
        if pos.professor.university is not None:
            return pos.professor.university.id
        return None 

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


class NotifUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["first_name", "last_name"]


class NotifUniSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["id", "name"]


class NotifStudentSerializer(serializers.ModelSerializer):
    user = NotifUserSerializer()
    university = NotifUniSerializer()

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "university",
        ]


class NotifProfessorSerializer(serializers.ModelSerializer):
    user = NotifUserSerializer()
    university = NotifUniSerializer()

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "university",
        ]


class NotifPositionSerializer(serializers.ModelSerializer):
    professor = NotifProfessorSerializer()

    class Meta:
        model = Position
        fields = [
            "id",
            "title",
            "end_date",
            "professor",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        exclude = []

    def get_position(self, obj: Notification):
        pos = None
        request = self.get_model_item(obj, Request)

        if request:
            pos = request.position
        else:
            pos = self.get_model_item(obj, Position)

        if pos:
            return NotifPositionSerializer(pos).data
        return None

    def get_student(self, obj: Notification):
        stu = None

        request = self.get_model_item(obj, Request)

        if request:
            stu = request.student
        else:
            stu = self.get_model_item(obj, Student)

        if stu:
            return NotifStudentSerializer(stu).data
        return None

    def get_model_item(self, obj: Notification, model):
        item = None
        item_list = getattr(
            obj, f"{model._meta.app_label}_{model._meta.model_name}_items", []
        )
        if item_list:
            item = item_list[0]
        if item:
            return item.content_object
        return None


# Top 5 Student Seralizer ------------------------------------------------------


class UniversityLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["name", "country", "city"]

    country = CountrySerializer(name_only=True)


class TopStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("student_name", "major", "university", "gpa", "image")

    image = StudentImageSerializer(read_only=True)
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
        if hasattr(student, 'avg_grade'):
            return student.avg_grade




class TopProfessorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = (
            "professor_name",
            "major",
            "university",
            "department",
            "project_num",
            "image",
        )

    image = ProfessorImageSerializer(read_only=True)
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


class ProfessorPositionSearchSerializer(BasePositionSerializer):
    university_name = serializers.SerializerMethodField("get_university_name")
    university_id = serializers.SerializerMethodField("get_university_id")

    class Meta:
        model = Position
        exclude = [
            "description",
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


# Chat System Serializers ------------------------------------------------------


class ChatSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSystem
        fields = [
            "id",
            "group_name",
            "part_of_last_message",
            "time_of_the_last_message",
            "person_of_the_last_message",
            "chat_enable",
            "unseen_messages_flag",
        ]

    part_of_last_message = serializers.SerializerMethodField()
    time_of_the_last_message = serializers.SerializerMethodField()
    person_of_the_last_message = serializers.SerializerMethodField()
    unseen_messages_flag = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()

    def get_group_name(self, chat: ChatSystem):
        user_pk = self.context["request"].user.id
        person = chat.participants.exclude(pk=user_pk).first()
        return " ".join([person.first_name, person.last_name])

    def get_person_of_the_last_message(self, chat: ChatSystem):
        last_message = chat.messages.order_by("-send_time").first()
        if last_message is None:
            return None
        return last_message.user.first_name + last_message.user.last_name

    def get_time_of_the_last_message(self, chat: ChatSystem):
        last_message = chat.messages.order_by("send_time").reverse().first()
        if last_message is None:
            return None
        return last_message.send_time

    def get_part_of_last_message(self, chat: ChatSystem):
        last_message = chat.messages.order_by("send_time").reverse().first()
        if last_message is None:
            return None
        return last_message.text[:50]

    def get_unseen_messages_flag(self, chat: ChatSystem):
        if chat.messages is None:
            return False
        chat_messages = chat.messages.all()
        user = self.context["request"].user
        other_person_chats = chat_messages.exclude(user=user)
        unseen_messages = other_person_chats.filter(seen_flag=False)
        if unseen_messages.exists():
            return True
        return False


class NoChatProfessorsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSystem
        fields = ["id", "name", "university"]

    name = serializers.SerializerMethodField()
    university = serializers.SerializerMethodField()

    def get_name(self, chat: ChatSystem):
        chat_members = chat.participants
        professor = chat_members.filter(is_student=False).first()
        return " ".join([professor.first_name, professor.last_name])

    def get_university(self, chat: ChatSystem):
        chat_members = chat.participants
        professor = chat_members.filter(is_student=False).first()
        professor = Professor.objects.get(user__pk=professor.pk)
        if professor.university is None:
            return None
        else:
            return professor.university.name


class NoChatStudentsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSystem
        fields = ["id", "name", "university"]

    name = serializers.SerializerMethodField()
    university = serializers.SerializerMethodField()

    def get_name(self, chat: ChatSystem):
        chat_members = chat.participants
        student = chat_members.filter(is_student=True).first()
        return " ".join([student.first_name, student.last_name])

    def get_university(self, chat: ChatSystem):
        chat_members = chat.participants
        student = chat_members.filter(is_student=False).first()
        student = Professor.objects.get(user__pk=student.pk)
        if student.university is None:
            return None
        else:
            return student.university.name


class UnseenChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSystem
        fields = ["number"]

    number = serializers.SerializerMethodField()

    def get_number(self, chat: ChatSystem):
        return self.context["number"]


class StartNewChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSystem
        fields = []


class RetrieveMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "text",
            "send_time",
            "chat_id",
            "is_student",
            "sender",
        ]

    chat_id = serializers.SerializerMethodField()
    is_student = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()

    def get_chat_id(self, message: Message):
        return message.related_chat_group.id

    def get_is_student(self, message: Message):
        if message.user is None:
            return True
        return message.user.is_student

    def get_sender(self, message: Message):
        return message.user.first_name + " " + message.user.last_name


class UpdateMessageLastSeenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["seen_flag"]


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["text", "related_chat_group", "user"]


class DeleteMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id"]


class EditMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["text"]
