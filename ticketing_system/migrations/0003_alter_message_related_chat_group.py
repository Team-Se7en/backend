# Generated by Django 5.0.4 on 2024-05-29 09:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing_system', '0002_message_seen_flag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='related_chat_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='ticketing_system.chatsystem'),
        ),
    ]
