from django import forms
from .models import Image


class StudentForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ("image",)


class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ("image",)
