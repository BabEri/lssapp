# Generated by Django 4.2.7 on 2024-01-14 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='level',
            field=models.CharField(blank=True, choices=[('1', 'Part One'), ('2', 'Part Two'), ('3', 'Part Three'), ('4', 'Part Four'), ('5', 'Part Five')], max_length=1, null=True, verbose_name='Current Level'),
        ),
        migrations.AddField(
            model_name='course',
            name='semester',
            field=models.CharField(blank=True, choices=[('1', 'First Semester'), ('2', 'Second Semester')], max_length=1, null=True, verbose_name='Current Semester'),
        ),
        migrations.AlterField(
            model_name='course_registration',
            name='session',
            field=models.CharField(choices=[('7', '2022/2023'), ('6', '2021/2022'), ('5', '2019/2020'), ('4', '2018/2019'), ('3', '2017/2018'), ('2', '2016/2017'), ('1', '2015/2016')], max_length=3, verbose_name='Academic Session'),
        ),
    ]