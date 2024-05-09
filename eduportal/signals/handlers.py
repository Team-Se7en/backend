from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from eduportal.models import *


@receiver(post_save, sender=get_user_model())
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        return
    if instance.is_active:
        if instance.is_student:
            if not hasattr(instance, "student"):
                Student.objects.create(user=instance)
        else:
            if not hasattr(instance, "professor"):
                Professor.objects.get_or_create(user=instance)


@receiver(post_save, sender=Student)
def create_student_cv(sender, instance, created, **kwargs):
    if created:
        CV.objects.create(student=instance)


@receiver(post_save, sender=Professor)
def create_professor_cv(sender, instance, created, **kwargs):
    if created:
        CV.objects.create(professor=instance)
