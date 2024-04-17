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


class StudentGetListViewSet(
    ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Student.objects.all()
    serializer_class = serializers.StudentGetListSerializer


class StudentProfileViewSet(
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Student.objects.all()
    serializer_class = serializers.StudentProfileSerializer
    permission_classes = [IsAuthenticated, CurrentUserOrAdmin]
    http_method_names = [
        "get",
        "patch",
        "delete",
    ]
    def destroy(self, request, *args, **kwargs):
        student_id = self.kwargs["pk"]
        student = get_object_or_404(Student, pk=student_id)
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
