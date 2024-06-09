# Generated by Django 5.0.4 on 2024-06-05 19:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eduportal', '0032_professorimage_studentimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='professor',
            name='image',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='eduportal.professorimage'),
        ),
        migrations.AddField(
            model_name='student',
            name='image',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='eduportal.studentimage'),
        ),
    ]