from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver

from eduportal.models import *
from ticketing_system.models import *
from ..serializers import NotificationSerializer, RetrieveMessageSerializer


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
@transaction.atomic
def delete_notification(sender, instance, **kwargs):
    instance.notification.delete()


@receiver(post_save, sender=Request)
@transaction.atomic
def create_request_notification(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(instance)

        notification_item, created = NotificationItem.objects.get_or_create(
            content_type=content_type, object_id=instance.id
        )

        print(
            f"create_request_notification:\tDebug:\t\t{'Created' if created else 'Retrieved'} NotificationItem object."
        )

        notif = Notification.objects.create(
            notification_type=NotificationTypeChoices.STUDENT_CREATED_REQUEST,
            user=instance.position.professor.user,
        )

        print("create_request_notification:\tDebug:\t\tCreated Notification object.")

        notification_item.notifications.add(notif)

        print("create_request_notification:\tDebug:\t\tCreated Notification object.")


@receiver(pre_save, sender=Request)
@transaction.atomic
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
@transaction.atomic
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


@receiver(post_save, sender=Position)
@transaction.atomic
def mark_position_as_created(sender, instance, created, **kwargs):
    if created:
        created_positions = cache.get("created_positions", set())
        created_positions.add(instance.id)
        cache.set("created_positions", created_positions)


@receiver(m2m_changed, sender=Position.tags2.through)
@transaction.atomic
def create_interested_students_notification(sender, instance, action, **kwargs):
    if action == "post_add":
        created_positions = cache.get("created_positions", set())
        if instance.id in created_positions:
            content_type = ContentType.objects.get_for_model(instance)

            position_ni, created = NotificationItem.objects.get_or_create(
                content_type=content_type, object_id=instance.id
            )

            tags = instance.tags2
            notified = set()

            for t in tags.all():
                students = t.students

                for s in students.all():
                    if s.id not in notified:
                        std_ct = ContentType.objects.get_for_model(s)
                        std_ni, std_ni_created = NotificationItem.objects.get_or_create(
                            content_type=std_ct, object_id=s.id
                        )

                        notif = Notification.objects.create(
                            notification_type=NotificationTypeChoices.NEW_TAGGED_POST,
                            user=s.user,
                        )

                        position_ni.notifications.add(notif)
                        std_ni.notifications.add(notif)
                        notified.add(s.id)

            # Remove the instance from the set in the cache
            created_positions.remove(instance.id)
            cache.set("created_positions", created_positions)


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created:

        print("notification_created:\t\tDebug:\t\tBefore defining the action.")

        def send_notification():
            print("notification_created:\t\tDebug:\t\tStarting the action.")

            channel_layer = get_channel_layer()
            print(
                f"notification_created:\t\tDebug:\t\tRetrieved channel: {channel_layer}"
            )
            group_name = f"notification_{instance.user.id}"
            print(f"notification_created:\t\tDebug:\t\tRetrieved group: {group_name}")
            serializer = NotificationSerializer(instance)
            print(
                f"notification_created:\t\tDebug:\t\tRetrieved serializer: {serializer}"
            )
            message = serializer.data
            print(f"notification_created:\t\tDebug:\t\tRetrieved message: {message}")

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "message": message,
                },
            )

            print("notification_created:\t\tDebug:\t\tGroup send initiated.")

        print("notification_created:\t\tDebug:\t\tDefined the action.")

        transaction.on_commit(send_notification)

        print("notification_created:\t\tDebug:\t\tRegistered the transaction.")


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    if created:
        print("message_created:\t\tDebug:\t\tBefore defining the action.")

        def send_message():
            print("message_created:\t\tDebug:\t\tStarting the action.")

            channel_layer = get_channel_layer()
            print(f"message_created:\t\tDebug:\t\tRetrieved channel: {channel_layer}")
            group_name = f"chat_{instance.related_chat_group.id}"
            print(f"message_created:\t\tDebug:\t\tRetrieved group: {group_name}")
            serializer = RetrieveMessageSerializer(instance)
            print(f"message_created:\t\tDebug:\t\tRetrieved serializer: {serializer}")
            message = serializer.data
            print(f"message_created:\t\tDebug:\t\tRetrieved message: {message}")

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_message",
                    "message": message,
                },
            )

            print("message_created:\t\tDebug:\t\tGroup send initiated.")

        print("message_created:\t\tDebug:\t\tDefined the action.")

        transaction.on_commit(send_message)

        print("message_created:\t\tDebug:\t\tRegistered the transaction.")
