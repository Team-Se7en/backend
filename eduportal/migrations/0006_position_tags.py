# Generated by Django 5.0.4 on 2024-04-18 19:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eduportal", "0005_remove_position_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="position",
            name="tags",
            field=models.ManyToManyField(blank=True, to="eduportal.tag"),
        ),
    ]
