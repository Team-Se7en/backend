from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save, post_delete
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


@receiver(post_delete, sender=NotificationItem)
def delete_notification(sender, instance, **kwargs):
    instance.notification.delete()


@receiver(post_save, sender=Request)
def create_request_notification(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(instance)

        notification_item, created = NotificationItem.objects.get_or_create(
            content_type=content_type, object_id=instance.id
        )

        notif = Notification.objects.create(
            notification_type=NotificationTypeChoices.STUDENT_CREATED_REQUEST,
            user=instance.position.professor.user,
        )

        notification_item.notifications.add(notif)


@receiver(pre_save, sender=Request)
def create_professor_response_notification(sender, instance, **kwargs):
    if instance.pk:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.status == "PP" and instance.status in ["PA", "PR"]:
            content_type = ContentType.objects.get_for_model(instance)

            notification_item, created = NotificationItem.objects.get_or_create(
                content_type=content_type, object_id=instance.id
            )

            notification_type = (
                NotificationTypeChoices.PROFESSOR_ACCEPTED_REQUEST
                if instance.status == "PA"
                else NotificationTypeChoices.PROFESSOR_REJECTED_REQUEST
            )

            notif = Notification.objects.create(
                notification_type=notification_type,
                user=instance.student.user,
            )

            notification_item.notifications.add(notif)


@receiver(pre_save, sender=Request)
def create_student_response_notification(sender, instance, **kwargs):
    if instance.pk:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.status == "PA" and instance.status in ["SA", "SR"]:
            content_type = ContentType.objects.get_for_model(instance)

            notification_item, created = NotificationItem.objects.get_or_create(
                content_type=content_type, object_id=instance.id
            )

            notification_type = (
                NotificationTypeChoices.STUDENT_ACCEPTED_REQUEST
                if instance.status == "SA"
                else NotificationTypeChoices.STUDENT_REJECTED_REQUEST
            )

            notif = Notification.objects.create(
                notification_type=notification_type,
                user=instance.position.professor.user,
            )

            notification_item.notifications.add(notif)