# Generated by Django 5.0.4 on 2024-05-29 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing_system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='seen_flag',
            field=models.BooleanField(default=False),
        ),
    ]
