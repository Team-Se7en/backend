# Generated by Django 5.0.4 on 2024-05-04 13:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("eduportal", "0008_university"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="professor",
            name="university",
        ),
    ]