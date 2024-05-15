# Generated by Django 5.0.4 on 2024-05-15 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eduportal', '0020_notification_bookmarked_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='major',
            field=models.IntegerField(choices=[(1, 'Computer Engineering'), (2, 'Software Engineering'), (3, 'Mechanical Engineering'), (4, 'Electrical Engineering'), (5, 'Civil Engineering'), (6, 'Aerospace Engineering'), (7, 'Biology'), (8, 'Chemistry'), (9, 'Physics'), (10, 'Mathematics'), (11, 'Statistics'), (12, 'Economics'), (13, 'Psychology'), (14, 'Sociology'), (15, 'Political Science'), (16, 'Philosophy'), (17, 'English'), (18, 'History'), (19, 'Art'), (20, 'Music'), (21, 'Theatre'), (22, 'Education'), (23, 'Business'), (24, 'Accounting'), (25, 'Finance'), (26, 'Marketing'), (27, 'Human Resource Management'), (28, 'International Business'), (29, 'Entrepreneurshi')], null=True),
        ),
    ]
