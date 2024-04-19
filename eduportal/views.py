from django.shortcuts import get_object_or_404
from .models import Student
from . import serializers
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
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import *
from .serializers import *
from .permissions import *


class StudentGetListViewSet(
    ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Student.objects.select_related('user').all()
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
        methods=["GET", "PATCH","DELETE"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request ,  *args, **kwargs):
        student = get_object_or_404(Student, user_id=request.user.id)
        if request.method == "GET":
            serializer = StudentProfileSerializer(student)
            return Response(serializer.data)
        elif request.method == "PATCH":
            serializer = StudentProfileSerializer(student, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == "DELETE":
            user = student.user 
            student.delete()
            user.delete()
            return Response(status=status.HTTP_202_ACCEPTED)


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


class PositionViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.request.method == "GET":
            return ReadPositionSerializer
        elif self.request.method == "POST":
            return CreatePositionSerializer
        print(self.request.method)
        return ReadPositionSerializer

    def get_queryset(self):
        return Position.objects.select_related("professor", "professor__user").all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsProfessor()]
        else:
            return []

    def create(self, request, *args, **kwargs):
        serializer = CreatePositionSerializer(
            data=request.data, context={"professor_id": self.request.user.professor.id}
        )
        serializer.is_valid(raise_exception=True)
        position = serializer.save()
        serializer = ReadPositionSerializer(position)
        return Response(serializer.data)
