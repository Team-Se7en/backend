# Generated by Django 5.0.4 on 2024-04-26 01:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eduportal", "0005_request_share_with_others"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="position",
            name="duration",
        ),
        migrations.AddField(
            model_name="position",
            name="ends_at",
            field=models.DateField(default="2050-12-12"),
            preserve_default=False,
        ),
    ]