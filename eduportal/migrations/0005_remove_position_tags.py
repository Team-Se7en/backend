# Generated by Django 5.0.4 on 2024-04-18 19:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("eduportal", "0004_remove_tag_id_alter_tag_label"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="position",
            name="tags",
        ),
    ]