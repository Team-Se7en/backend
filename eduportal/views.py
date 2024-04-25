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
    @action(detail=False, methods=["get"])
    def userinfo(self, request):
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
    queryset = Professor.objects.all()
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

        queryset = Position.objects.select_related("professor", "professor__user")

        if self.action == "list":
            queryset = queryset.exclude(professor__user__id=user.id)

        queryset = queryset.prefetch_related("tags")

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
            return [IsAuthenticated()]
        if self.action == "create":
            return [IsProfessor()]
        if self.action in ["update" or "partial_update", "destroy"]:
            return [IsPositionOwner()]
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
        if self.action == "update":
            return [IsAuthenticated(), IsProfessor(),IsPositionOwner()]
        if self.action == "destroy":
            return [AllowNone()]
        if self.action == "retrieve":
            return [IsAuthenticated()]
        return []

    def get_serializer_class(self):
        if self.action == "create":
            return StudentCreateRequestSerializer
        if self.action == "update":
            return RequestUpdateSeralizer
        if self.action == "retrieve":
            if self.request.user.is_student:
                return StudentRequestDetailSerializer
            else:
                return ProfessorRequestDetailSerializer
        return RequestListSeralizer

    def partial_update(self, request, *args, **kwargs):
        request_object =get_object_or_404(Request,pk=kwargs["pk"])
        if request_object.position.professor.user.id != request.user.id:
            return Response("Access denied", status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        request_object =get_object_or_404(Request,pk=kwargs["pk"])
        if request_object.student.user.id == request.user.id:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response("Access denied", status=status.HTTP_403_FORBIDDEN)

    def list(self, request, *args, **kwargs):
        queryset = Request.objects
        if request.user.is_student:
            queryset = queryset.select_related("student").filter(
                student__user__id=request.user.id
            )
        else:
            queryset = queryset.select_related("position").filter(
                position__professor__user__id=request.user.id
            )
        seializer = RequestListSeralizer(queryset, many=True)
        return Response(seializer.data)

    def create(self, request, *args, **kwargs):
        student = Student.objects.select_related("user").get(user__id=request.user.id)
        sent_requests = student.request_set.filter(
            position__id=request.data.get("position_id")
        )
        if sent_requests.exists():
            if sent_requests.filter(status = "R").exists():
                return Response("You are not allowed to request anymore",
                                status= status.HTTP_403_FORBIDDEN)
            return Response(
                "Request already exists", status=status.HTTP_400_BAD_REQUEST
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


class AdmissionViewSet(ListModelMixin, GenericViewSet):
    serializer_class = AdmissionSerializer
    queryset = Request.objects.filter(status="P").all()
