# Generated by Django 5.0.4 on 2024-05-30 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing_system', '0004_chatsystem_chat_enable'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatsystem',
            name='start_chat',
            field=models.BooleanField(default=False),
        ),
    ]
