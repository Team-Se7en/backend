from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from eduportal.models import *


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, **kwargs):
    if kwargs["created"]:
        user = kwargs["instance"]

        if user.is_student:
            Student.objects.create(user=user)
        else:
            Professor.objects.create(user=user)
