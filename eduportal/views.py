from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from djoser.permissions import CurrentUserOrAdmin
from pprint import pprint
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.mixins import *
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import *
from .serializers import *
from .permissions import *
from .utils.views import *


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
    serializer_class = StudentProfileSerializer
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
            serializer = StudentProfileSerializer(student)
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = StudentProfileSerializer(
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
        permission_classes=[IsAuthenticated],
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
        if action == "list":
            if user_type == "Anonymous":
                return AnonymousPositionListSerializer
            if user_type == "Student":
                return StudentPositionListSerializer
            if user_type == "Professor":
                return ProfessorPositionListSerializer
            return None
        if action == "retrieve":
            if self.get_object().professor.user.id == user.id:
                return OwnerPositionDetailSerializer
            if user_type == "Student":
                return StudentPositionDetailSerializer
            if user_type == "Professor":
                return ProfessorPositionDetailSerializer
            return None
        if action in ["create", "update", "partial_update"]:
            return PositionUpdateSerializer
        return None

    def get_queryset(self):
        if self.action == "list":
            user = self.request.user
            qs = Position.objects
            if user.is_authenticated:
                qs = qs.exclude(professor__user__id=user.id)

            return (
                qs.select_related("professor", "professor__user")
                .prefetch_related("tags")
                .all()
            )
        else:
            return (
                Position.objects.select_related("professor", "professor__user")
                .prefetch_related("tags")
                .all()
            )

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
