# Generated by Django 5.0.4 on 2024-05-13 08:06

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eduportal", "0015_remove_student_university_name_student_university"),
    ]

    operations = [
        migrations.CreateModel(
            name="LanguageSkill",
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
                (
                    "language",
                    models.IntegerField(
                        choices=[
                            (1, "Mandarin Chinese"),
                            (2, "Spanish"),
                            (3, "English"),
                            (4, "Hindi"),
                            (5, "Bengali"),
                            (6, "Portuguese"),
                            (7, "Russian"),
                            (8, "Japanese"),
                            (9, "Western Punjabi"),
                            (10, "Marathi"),
                            (11, "Telugu"),
                            (12, "Wu Chinese"),
                            (13, "Turkish"),
                            (14, "Korean"),
                            (15, "French"),
                            (16, "German"),
                            (17, "Vietnamese"),
                            (18, "Tamil"),
                            (19, "Yue Chinese"),
                            (20, "Urdu"),
                            (21, "Javanese"),
                            (22, "Italian"),
                            (23, "Arabic"),
                            (24, "Gujarati"),
                            (25, "Persian"),
                            (26, "Bhojpuri"),
                            (27, "Southern Min"),
                            (28, "Hakka"),
                            (29, "Jinyu Chinese"),
                            (30, "Hausa"),
                        ]
                    ),
                ),
                (
                    "skill_level",
                    models.FloatField(
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(5.0),
                        ]
                    ),
                ),
                (
                    "cv",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="language_skills",
                        to="eduportal.cv",
                    ),
                ),
            ],
        ),
    ]