# Generated by Django 4.2.7 on 2024-01-23 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_course_registration_deans_list_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='session',
            field=models.CharField(choices=[('8', '2023/2024'), ('7', '2022/2023'), ('6', '2021/2022'), ('5', '2019/2020'), ('4', '2018/2019'), ('3', '2017/2018'), ('2', '2016/2017'), ('1', '2015/2016')], max_length=3, verbose_name='Academic Session'),
        ),
    ]
