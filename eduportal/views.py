from django.shortcuts import get_object_or_404
from .models import Student
from . import serializers
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from djoser.permissions import CurrentUserOrAdmin
from pprint import pprint
from rest_framework.response import Response
from rest_framework import status

class StudentGetListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Student.objects.all()
    serializer_class = serializers.StudentGetListSerializer


class StudentProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
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
