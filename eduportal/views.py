from .models import Student
from .serializers import StudentGetListSerializer
from rest_framework import viewsets
from rest_framework import mixins

class StudentGetListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Student.objects.all()
    serializer_class = StudentGetListSerializer
