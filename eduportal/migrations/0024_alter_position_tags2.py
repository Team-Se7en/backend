# Generated by Django 5.0.4 on 2024-05-16 11:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eduportal", "0023_alter_student_interest_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="position",
            name="tags2",
            field=models.ManyToManyField(blank=True, to="eduportal.tag2"),
        ),
    ]
