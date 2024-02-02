# Generated by Django 4.2.7 on 2024-01-13 21:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('registration', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course_registration',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registration.student'),
        ),
        migrations.AddField(
            model_name='course',
            name='student',
            field=models.ManyToManyField(related_name='Students', through='courses.Course_Registration', to='registration.student'),
        ),
    ]