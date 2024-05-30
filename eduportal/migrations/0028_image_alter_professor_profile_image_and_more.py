# Generated by Django 5.0.4 on 2024-05-30 17:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eduportal', '0027_alter_request_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='image/')),
            ],
        ),
        migrations.AlterField(
            model_name='professor',
            name='profile_image',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='eduportal.image'),
        ),
        migrations.AlterField(
            model_name='student',
            name='profile_image',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='eduportal.image'),
        ),
    ]
