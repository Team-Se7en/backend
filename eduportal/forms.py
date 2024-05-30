from django import forms
from .models import Student, Professor


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ("profile_image",)


class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ("profile_image",)
