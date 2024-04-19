from django.contrib import admin
from django.conf import settings
from django.db import models


# Create your models here.


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_profile"
    )
    university_name = models.CharField(max_length=255,null=True)
    ssn = models.IntegerField(null=True)

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