from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.mixins import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import *
from .serializers import *


class StudentListAPI(ListAPIView):
    queryset = Student.objects.select_related("user").all()
    serializer_class = StudentSerializer


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
