# Generated by Django 5.0.4 on 2024-05-15 14:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eduportal", "0022_student_major"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="interest_tags",
            field=models.ManyToManyField(related_name="students", to="eduportal.tag2"),
        ),
    ]
