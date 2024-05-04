# Generated by Django 5.0.4 on 2024-05-04 13:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eduportal", "0009_remove_professor_university"),
    ]

    operations = [
        migrations.AddField(
            model_name="professor",
            name="university",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="professors",
                to="eduportal.university",
            ),
        ),
    ]