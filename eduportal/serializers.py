from .models import Student
from rest_framework import serializers

class StudentGetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ([
            'id',
            'user',
            'student_name',
            'university_name',
        ])

    student_name = serializers.SerializerMethodField(method_name='get_student_name')

    def get_student_name(self,student:Student) -> str:
        return student.user.first_name + ' ' + student.user.last_name
