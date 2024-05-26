from django.contrib.auth import get_user_model
from django.db import models


USER_MODEL = get_user_model()


class ChatSystem(models.Model):
    group_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    text = models.TextField(max_length=255)
    send_time = models.DateTimeField(auto_now_add=True)
    related_chat_group = models.ForeignKey(
        ChatSystem,
        on_delete=models.CASCADE,
    )


class ChatMembers(models.Model):
    chat = models.OneToOneField(
        ChatSystem,
        on_delete=models.CASCADE,
        related_name="chat",
    )
    participants = models.ManyToManyField(
        USER_MODEL,
    )
