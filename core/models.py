from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)

        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user


class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=255, unique=True)
    is_student = models.BooleanField()

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "is_student"]

    def __str__(self) -> str:
        return self.email
