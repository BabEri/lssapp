# Generated by Django 4.2.7 on 2024-01-13 21:23

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import registration.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=20, unique=True, verbose_name='Admin Username')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Admin Email')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Admin Full Name')),
                ('is_active', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Admin',
                'verbose_name_plural': 'Admins',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('session', models.CharField(choices=[('14', '2029/2030'), ('13', '2028/2029'), ('12', '2027,2028'), ('11', '2026/2027'), ('10', '2025/2026'), ('9', '2024/2025'), ('8', '2023/2024'), ('7', '2022/2023'), ('6', '2021/2022'), ('5', '2019/2020'), ('4', '2018/2019'), ('3', '2017/2018'), ('2', '2016/2017'), ('1', '2015/2016')], max_length=3, verbose_name='Current Academic Session')),
                ('level', models.CharField(choices=[('1', 'Part One'), ('2', 'Part Two'), ('3', 'Part Three'), ('4', 'Part Four'), ('5', 'Part Five'), ('6', 'Spill One'), ('7', 'Spill Two')], max_length=1, verbose_name='Current Level')),
                ('semester', models.CharField(choices=[('1', 'First Semester'), ('2', 'Second Semester')], max_length=1, verbose_name='Current Semester')),
                ('d_o_b', models.DateField(blank=True, null=True, verbose_name='Date of Birth')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1, verbose_name='Gender')),
                ('phone_no', models.CharField(blank=True, max_length=13, null=True, verbose_name='Phone Number')),
                ('entry_mode', models.CharField(choices=[('UTME', 'Unified Tertiary Matriculation Examination'), ('DE', 'Direct Entry')], max_length=4, verbose_name='Mode of Admission')),
                ('TUP', models.IntegerField(blank=True, null=True, verbose_name='Total Unit Passed')),
                ('CTCP', models.IntegerField(blank=True, null=True, verbose_name='Cummulative Total Credit Passed')),
                ('CTLU', models.IntegerField(blank=True, null=True, verbose_name='Cummulative Total Load Unit')),
                ('CGPA', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='Cummulative Grade Point Average')),
                ('student_status', models.CharField(blank=True, choices=[('GS', 'Good Standing'), ('GD', 'Graduated'), ('PR', 'Probation'), ('EX', 'Advised to Withdraw'), ('WN', 'Warning'), ('LA', 'Leave of Absence')], max_length=20, null=True)),
                ('evid', models.FileField(blank=True, null=True, upload_to=registration.models.upload_directory, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png', 'gif', 'doc', 'docx', 'csv', 'xlsx']), registration.models.FileSizeValidator], verbose_name='Evidence of Studentship')),
            ],
            options={
                'verbose_name': 'Student',
                'verbose_name_plural': 'Students',
                'ordering': ['username', 'name', 'email', 'level'],
            },
            bases=('registration.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
