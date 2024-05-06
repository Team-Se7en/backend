from typing import Iterable
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from .majors import *

# Create your models here.


class University(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to="universities/")
    icon = models.ImageField(upload_to="universities/")
    website_url = models.URLField(max_length=255)
    rank = models.IntegerField()
    city = models.CharField(max_length=63)
    country = CountryField()
    total_student_count = models.IntegerField()
    international_student_count = models.IntegerField()

    def delete(self, *args, **kwargs):
        self.image.delete()
        self.icon.delete()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_self = University.objects.get(pk=self.pk)
            if old_self.image.name != self.image.name:
                old_self.image.delete(save=False)
            if old_self.icon.name != self.icon.name:
                old_self.icon.delete(save=False)
        super().save(*args, **kwargs)


class Student(models.Model):
    GENDER = [
        ("M", "Male"),
        ("F", "Female"),
        ("R", "Rather not to say"),
    ]
    STATUS = [("A", "Active"), ("I", "Inactive"), ("G", "Graduated")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    university_name = models.CharField(max_length=255, null=True)
    ssn = models.IntegerField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER, null=True)
    nationality = models.CharField(max_length=50, null=True)
    enrollment_date = models.DateField(null=True)
    status = models.CharField(max_length=1, choices=STATUS, null=True)
    major = models.CharField(max_length=4, choices=MAJORS, null=True)


class Professor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    university = models.ForeignKey(
        University, models.SET_NULL, blank=True, null=True, related_name="professors"
    )
    department = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @admin.display(ordering="user__first_name")
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self):
        return self.user.last_name


class Tag(models.Model):
    label = models.CharField(max_length=31, primary_key=True)

    def __str__(self) -> str:
        return self.label


class Position(models.Model):
    title = models.CharField(max_length=63)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    professor = models.ForeignKey(
        Professor, on_delete=models.PROTECT, related_name="positions"
    )
    capacity = models.IntegerField()
    filled = models.IntegerField(default=0)
    request_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    start_date = models.DateField()
    end_date = models.DateField()
    position_start_date = models.DateField()
    position_end_date = models.DateField()

    fee = models.FloatField()


class Request(models.Model):
    REQUEST_STATUS = [
        ("P", "Pending"),
        ("R", "Rejected"),
        ("A", "Accepted"),
    ]
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=REQUEST_STATUS, default="P", blank=True, null=True
    )
    date_applied = models.DateTimeField(auto_now_add=True, null=True)
    # متنی که دانشجو در ریکوئست می‌نویسد
    cover_letter = models.TextField()
    share_with_others = models.BooleanField(default=False)


class CV(models.Model):
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name="cv", null=True, blank=True
    )
    professor = models.OneToOneField(
        Professor, on_delete=models.CASCADE, related_name="cv", null=True, blank=True
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("R", "Rather not to say"),
    ]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, null=True, blank=True
    )
    EMPLOYMENT_STATUS_CHOICES = [
        ("E", "Employed"),
        ("U", "Unemployed"),
        ("S", "Student"),
        ("AS", "Actively Seeking Work"),
        ("OW", "Open to Work"),
        ("NI", "Not Interested"),
    ]
    employment_status = models.CharField(
        max_length=2, choices=EMPLOYMENT_STATUS_CHOICES, null=True, blank=True
    )
    about = models.TextField(null=True, blank=True)
    soft_skills = models.ManyToManyField("SoftSkill")

class WorkExperience(models.Model):
    cv = models.ForeignKey(
        CV, on_delete=models.CASCADE, related_name="work_experiences"
    )
    company_name = models.CharField(max_length=255)
    company_website = models.URLField(max_length=200, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    job_title = models.CharField(max_length=255)


class EducationHistory(models.Model):
    cv = models.ForeignKey(
        CV, on_delete=models.CASCADE, related_name="education_histories"
    )
    institute = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    grade = models.FloatField(null=True, blank=True)


class ProjectExperience(models.Model):
    cv = models.ForeignKey(
        CV, on_delete=models.CASCADE, related_name="project_experiences"
    )
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=200)
    description = models.TextField(null=True, blank=True)


class HardSkill(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="hard_skills")
    technology = models.CharField(max_length=255)
    skill_level = models.IntegerField()
    experience_time = models.DurationField()

class SoftSkill(models.Model):
    name = models.CharField(max_length=255)
