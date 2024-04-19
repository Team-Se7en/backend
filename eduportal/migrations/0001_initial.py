# Generated by Django 5.0.4 on 2024-04-19 16:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "label",
                    models.CharField(max_length=31, primary_key=True, serialize=False),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Professor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("university", models.CharField(max_length=255)),
                ("department", models.CharField(max_length=255)),
                ("birth_date", models.DateField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("university_name", models.CharField(max_length=255, null=True)),
                ("ssn", models.IntegerField(null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Position",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=63)),
                ("description", models.TextField()),
                ("capacity", models.IntegerField()),
                ("filled", models.IntegerField(default=0)),
                ("request_count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deadline", models.DateField()),
                ("starts_at", models.DateField()),
                ("duration", models.DurationField()),
                (
                    "professor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="positions",
                        to="eduportal.professor",
                    ),
                ),
                ("tags", models.ManyToManyField(blank=True, to="eduportal.tag")),
            ],
        ),
    ]
