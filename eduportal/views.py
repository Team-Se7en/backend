from .models import Student
from .serializers import StudentSerializer
from rest_framework.generics import ListAPIView

class StudentListAPI(ListAPIView):
    queryset = Student.objects.select_related('user').all()
    serializer_class = StudentSerializer