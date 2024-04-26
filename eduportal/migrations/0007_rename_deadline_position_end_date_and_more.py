# Generated by Django 5.0.4 on 2024-04-26 15:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eduportal", "0006_remove_position_duration_position_ends_at"),
    ]

    operations = [
        migrations.RenameField(
            model_name="position",
            old_name="deadline",
            new_name="end_date",
        ),
        migrations.RenameField(
            model_name="position",
            old_name="ends_at",
            new_name="position_end_date",
        ),
        migrations.RenameField(
            model_name="position",
            old_name="starts_at",
            new_name="position_start_date",
        ),
        migrations.AddField(
            model_name="position",
            name="start_date",
            field=models.DateField(default="2000-01-01"),
            preserve_default=False,
        ),
    ]