from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# derivative functions
def FileSizeValidator(value):
	''' a function to limit filesize of evidence of studentship'''
	limit = 1 * 1024 * 1024
	if value.size > limit:
		raise ValidationError('File Size must not be more than 1 MB.')

def upload_directory(instance, filename):
	folder = instance.name
	return Path('Student_uploads')/folder/filename


# modelManager
class UserManager(BaseUserManager):
	''' A Manager for the custom Model written to override the customary Django User Model'''
	def create_user(self, username, password=None, **other_fields):
		if not username:
			raise ValueError('You need an Admin Username')
		if self.model.objects.filter(username=username).exists():
			raise ValueError('Admin Username already taken, please choose another Username')
		admin = self.model(username =username, **other_fields)
		admin.set_password(password)
		admin.save(using=self._db)
		return admin5555555
	def create_superuser(self, username=None,  password=None, **other_fields):
		return self.create_user(username, password=password, **other_fields)
# models

class User(AbstractUser, PermissionsMixin):
	'''
	A model to create Admin users, typically, all Admins are superusers and staff(of the project, not Faculty, obviously), however Groups may subsequently be created to differentiate levels of Admins, Admins may also be students or staff members of the Faculty
	'''
	username = models.CharField(max_length = 20, unique = True, verbose_name= 'Admin Username')
	email = models.EmailField(null = True, blank = True, verbose_name = 'Admin Email')
	name = models.CharField(max_length= 50,null = True, blank = True, verbose_name = 'Admin Full Name')
	is_active = models.BooleanField(default= False)
	is_admin = models.BooleanField(default = False)
	is_superuser = models.BooleanField(default = False)
	USERNAME_FIELD = 'username'
	EMAIL_FIELD = 'email'
	REQUIRED_FIELD = []
	class Meta:
		verbose_name = 'Admin' 
		verbose_name_plural = 'Admins'
		
	def get_username(self):
		return self.username
	def __str__(self):
		if self.name:
			return f'{self.name}'
		else:
			return f'{self.username}'

	def has_perm(self, perm, object=None):
		return True
	def save(self, *args, **kwargs):
		super().save(*args,**kwargs)


class Student(User):
	'''
	A model to create Student users different from Admin users
	'''
	SESSION_CHOICE = [
					# ('14', '2029/2030'),
					# ('13', '2028/2029'),
					# ('12', '2027,2028'),
					# ('11', '2026/2027'),
					# ('10', '2025/2026'),
					# ('9', '2024/2025'),
					('8', '2023/2024'),
					('7', '2022/2023'),
					('6', '2021/2022'),
					('5', '2019/2020'),
					('4', '2018/2019'),
					('3', '2017/2018'),
					('2', '2016/2017'),
					('1', '2015/2016'),
				]
	SEMESTER_CHOICE = [
						('1', 'First Semester'),
						('2', 'Second Semester')
						]
	
	LEVEL_CHOICE = [
				('1', '100 Level'),
				('2','200 Level'),
				('3', '300 Level'),
				('4', '400 Level'),
				('5', '500 Level'),
				('6', 'Spill One'),
				('7', 'Spill Two'),
				]
	ADMISSION_TYPE = [('UTME', 'Unified Tertiary Matriculation Examination'),
					('DE', 'Direct Entry')]
	GENDER_CHOICE = [
						('M', 'Male'),
						('F', 'Female'),
						]
	STUDENT_STATUS_CHOICE = [
								('GS', 'Good Standing'),
								('GD', 'Graduated'),
								('PR', 'Probation'),
								('EX', 'Advised to Withdraw'),
								('WN', 'Warning'),
								('LA', 'Leave of Absence'),
							]
	session= models.CharField(verbose_name = 'Current Academic Session', max_length= 3, choices = SESSION_CHOICE, default = '8', )
	level= models.CharField(verbose_name = 'Current Level',max_length = 1, choices= LEVEL_CHOICE)
	semester = models.CharField(verbose_name = 'Current Semester', max_length = 1, choices = SEMESTER_CHOICE, default = '1')
	# username = models.CharField(verbose_name = 'Matriculation Number', max_length = 16, unique=True, )
	# name = models.CharField(verbose_name= 'Full Name' ,max_length=50, blank=True)
	# email = models.EmailField(verbose_name =  'Email Address', blank=True, null=True)
	d_o_b = models.DateField(verbose_name = 'Date of Birth', blank=True, null=True)
	gender = models.CharField(verbose_name = 'Gender',max_length=1, choices = GENDER_CHOICE)
	phone_no = models.CharField(verbose_name='Phone Number', max_length = 13 ,blank=True, null=True)
	# is_active = models.BooleanField(default=True)
	entry_mode = models.CharField(verbose_name ='Mode of Admission', max_length= 4, choices = ADMISSION_TYPE)
	TUP = models.IntegerField(verbose_name = 'Total Unit Passed', blank= True, null = True) # this is the aggregate of aggregate of the Unit Passed by student in semester, it is useful to calculate if the student will graduate at 500 2nd and beyond. for the above student, TUP is 7 since he only passed the 4 and 3 units courses. 
	CTCP = models.IntegerField(verbose_name = 'Cummulative Total Credit Passed', blank= True, null = True)#cummulative of TCP for all finished semesters, useful for calculating CGPA.
	CTLU = models.IntegerField(verbose_name = 'Cummulative Total Load Unit', blank= True, null = True) #cummulative of TLU for all finished semesters, useful for calculating CGPA.
	CGPA = models.DecimalField(max_digits = 3, decimal_places= 2, verbose_name = 'Cummulative Grade Point Average', blank= True, null = True)# calculated by dividing CTCP by CTLU i.e. CTCP/CTLU
	student_status = models.CharField(max_length= 20, choices =STUDENT_STATUS_CHOICE, blank = True, null = True)
	evid = models.FileField(verbose_name = 'Evidence of Studentship',upload_to =upload_directory, blank = True, null = True, validators = [FileExtensionValidator(allowed_extensions = ['pdf', 'jpg', 'png', 'gif', 'doc', 'docx', 'csv', 'xlsx']) ,FileSizeValidator])
	class Meta:
		verbose_name = 'Student'
		verbose_name_plural = 'Students'
		ordering =['username', 'name', 'email', 'level']
	def __repr__(self):
		return fr'Student(username={self.username})'

	def __str__(self):
		return f'{self.name}: {self.username}'

	def save (self, *args, **kwargs):
		if self.CTCP is not None and self.CTLU is not None:
			self.CGPA = Decimal(self.CTCP/self.CTLU, ).quantize(Decimal('0.01'), rounding = ROUND_HALF_UP)
		else:
			self.CGPA = None
		if self.CGPA is not None and self.CGPA < 1.00: 
			self.student_status = 'PR'
		super().save(*args, **kwargs)