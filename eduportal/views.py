from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from pprint import pprint
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.mixins import *
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import *
from .permissions import *
from .serializers import *
from .utils.views import *


# User Views -------------------------------------------------------------------


class UserInfoViewSet(GenericViewSet):
    def list(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, context={"request": self.request})
        return Response(serializer.data)


# Student Views ----------------------------------------------------------------


class StudentGetListViewSet(
    ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Student.objects.select_related("user").all()
    serializer_class = StudentGetListSerializer


class StudentProfileViewSet(
    viewsets.GenericViewSet,
):
    queryset = Student.objects.all()
    serializer_class = OwnStudentProfileSerializer
    http_method_names = [
        "get",
        "patch",
        "delete",
    ]

    @action(
        detail=False,
        methods=["GET", "PATCH", "DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        student = get_object_or_404(Student, user_id=request.user.id)
        if request.method == "GET":
            serializer = OwnStudentProfileSerializer(student)
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = OwnStudentProfileSerializer(
                student, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == "DELETE":
            user = student.user
            student.delete()
            user.delete()
            return Response(status=status.HTTP_202_ACCEPTED)


# Professor Views --------------------------------------------------------------


class ProfessorViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    http_method_names = ["get", "patch"]
    queryset = Professor.objects.select_related("user").all()
    serializer_class = ProfessorSerializer

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        permission_classes=[IsProfessor],
    )
    def me(self, request):
        professor = get_object_or_404(Professor, user_id=request.user.id)
        if request.method == "GET":
            serializer = ProfessorSerializer(professor)
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = ProfessorSerializer(professor, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=["GET"], permission_classes=[IsProfessor])
    def my_positions(self, request):
        professor = get_object_or_404(Professor, user_id=request.user.id)
        positions = Position.objects.filter(professor=professor)
        positions = positions.select_related(
            "professor", "professor__user"
        ).prefetch_related("tags")
        serializer = OwnerPositionListSerializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], permission_classes=[IsProfessor])
    def my_recent_positions(self, request):
        professor = get_object_or_404(Professor, user_id=request.user.id)
        positions = Position.objects.filter(professor=professor).order_by(
            "-created_at"
        )[:5]
        positions = positions.select_related(
            "professor", "professor__user"
        ).prefetch_related("tags")
        serializer = OwnerPositionListSerializer(positions, many=True)
        return Response(serializer.data)


# Position Views ---------------------------------------------------------------


class TagListViewSet(
    ListModelMixin,
    GenericViewSet,
):
    queryset = Tag.objects.all()
    serializer_class = ReadTagSerializer


class PositionViewSet(ModelViewSet):
    def get_serializer_class(self):
        action = self.action
        user = self.request.user
        user_type = get_user_type(self.request)
        match action:
            case "list":
                match user_type:
                    case "Anonymous":
                        return AnonymousPositionListSerializer
                    case "Student":
                        return StudentPositionListSerializer
                    case "Professor":
                        return ProfessorPositionListSerializer
                return None
            case "retrieve":
                match user_type:
                    case "Anonymous":
                        return AnonymousPositionDetailSerializer
                    case "Student":
                        return StudentPositionDetailSerializer
                    case "Professor":
                        if self.get_object().professor.user == user:
                            return OwnerPositionDetailSerializer
                        return ProfessorPositionDetailSerializer
                return None
            case "create" | "update" | "partial_update":
                return PositionUpdateSerializer
            case _:
                return None

    def get_queryset(self):
        user = self.request.user
        user_type = get_user_type(self.request)

        queryset = Position.objects.select_related(
            "professor", "professor__user"
        ).prefetch_related("tags")

        if self.action == "list":
            queryset = queryset.exclude(professor__user__id=user.id)
        if self.action == "retrieve":
            if user_type == "Professor":
                requests_for_position = Request.objects.filter(
                    position__professor__user=user
                )
                queryset = queryset.prefetch_related(
                    Prefetch(
                        "request_set",
                        queryset=requests_for_position,
                        to_attr="position_requests",
                    )
                )

        if user_type == "Student":
            # Prefetch the Request objects for the current user
            requests_for_user = Request.objects.filter(student__user=user)
            queryset = queryset.prefetch_related(
                Prefetch(
                    "request_set",
                    queryset=requests_for_user,
                    to_attr="my_request",
                )
            )

        queryset = queryset.all()

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()

        user = self.request.user
        user_type = get_user_type(self.request)

        if user_type == "Student":
            context["student_id"] = user.student.id

        return context

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        if self.action == "retrieve":
            return [AllowAny()]
        if self.action == "create":
            return [IsProfessor()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsProfessor(), IsPositionOwner()]
        else:
            return [AllowNone()]

    def create(self, request, *args, **kwargs):
        serializer = PositionUpdateSerializer(
            data=request.data, context={"professor_id": self.request.user.professor.id}
        )
        serializer.is_valid(raise_exception=True)
        position = serializer.save()
        serializer = ProfessorPositionDetailSerializer(position)
        return Response(serializer.data)


# Request Views ----------------------------------------------------------------


class RequestViewSet(ModelViewSet):
    http_method_names = ["post", "get", "patch", "delete"]

    def get_queryset(self):
        return Request.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsStudent()]
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action in ["partial_update", "update"]:
            return [IsAuthenticated(), IsProfessor(), IsRequestOwner()]
        if self.action == "destroy":
            return [AllowNone()]
        if self.action == "retrieve":
            return [IsAuthenticated(), IsRequestOwner()]
        return [AllowNone()]

    def get_serializer_class(self):
        if self.action == "create":
            return StudentCreateRequestSerializer
        if self.action in ["update", "partial_update"]:
            return ProfessorRequestUpdateSeralizer
        if self.action == "retrieve":
            if self.request.user.is_student:
                return StudentRequestDetailSerializer
            else:
                return ProfessorRequestDetailSerializer
        if self.action == "list":
            return RequestListSeralizer
        return RequestListSeralizer

    def destroy(self, request, *args, **kwargs):
        request_object = get_object_or_404(Request, pk=kwargs["pk"])
        if request_object.student.user.id == request.user.id:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response("Access denied", status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        queryset = Request.objects
        if request.user.is_student:
            queryset = queryset.filter(student__id=request.user.student.id)
        else:
            queryset = queryset.select_related("position").filter(
                position__professor__id=request.user.professor.id
            )
        seializer = RequestListSeralizer(queryset, many=True)
        return Response(seializer.data)

    def create(self, request, *args, **kwargs):
        student = Student.objects.get(pk=request.user.student.id)
        sent_requests = student.request_set.filter(
            position__id=request.data.get("position_id")
        )
        if sent_requests.exists():
            if sent_requests.filter(status="R").exists():
                return Response(
                    "You are not allowed to request anymore",
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(
                "Request already exists", status=status.HTTP_400_BAD_REQUEST
            )
        position = Position.objects.get(pk=request.data.get("position_id"))
        if position.capacity == 0:
            Response(
                "This position is completed.", status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        if position.deadline < timezone.now().date():
            return Response(
                "The deadline is finished.", status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        serializer = StudentCreateRequestSerializer(
            data=request.data,
            context={
                "student_id": student.id,
            },
        )
        serializer.is_valid(raise_exception=True)
        position = serializer.save()
        serializer = StudentCreateRequestSerializer(position)
        return Response(serializer.data)


class AdmissionViewSet(UpdateModelMixin, ListModelMixin, GenericViewSet):
    http_method_names = ["get", "patch"]

    def get_queryset(self):
        if self.action == "list":
            return Request.objects.filter(status="A", share_with_others=True).all()
        if self.action == "partial_update":
            return Request.objects.filter(status="A").all()
        return None

    def get_permissions(self):
        if self.action == "list":
            return []
        if self.action == "partial_update":
            return [IsAuthenticated(), IsStudent(), IsRequestOwner()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "list":
            return AdmissionSerializer
        elif self.action == "partial_update":
            return StudentRequestUpdateSeralizer

    def update(self, request, *args, **kwargs):
        request_object = get_object_or_404(Request, pk=kwargs["pk"])
        if request_object.status != "A":
            return Response("Invalid admission.", status=status.HTTP_400_BAD_REQUEST)
        request_object.share_with_others = True
        return super().update(request, *args, **kwargs)
