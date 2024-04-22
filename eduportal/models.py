from django.conf import settings
from django.contrib import admin
from django.db import models

from .majors import *

# Create your models here.


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
    university = models.CharField(max_length=255)
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
    deadline = models.DateField()
    starts_at = models.DateField()
    duration = models.DurationField()

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
