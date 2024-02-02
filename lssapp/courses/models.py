from django.db import models
from registration.models import Student
from decimal import Decimal
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from pathlib import Path
from datetime import date
from django.db.models.signals import pre_save
from django.dispatch import receiver
# Create your models here.

def FileSizeValidator(value):
	''' a function to limit filesize of evidence of studentship'''
	limit = 75 * 1024 * 1024
	if value.size > limit:
		raise ValidationError('File Size must not be more than 75 MB.')

def upload_directory(instance, filename):
	folder = instance.course.code
	return Path('course_uploads')/folder/date.today().strftime('%Y/%m/%d')/filename

class Course(models.Model):
	''' Courses for registration, others are non law courses that are neither GST or ENT courses, so they automatically are optional and usually 3 units, University courses are typically 2 units while law courses except for JIL 101/102:Legal Methods 1 and 2 are 2 units and Law 500: Project is 6 Uints. student is passed in as a parameter so as to enable aggregation of students writing a course'''
	COURSE_TYPE = [
					('CL', 'Compulsory Law Course'),
					('CU', 'Compulsory University Course (GST/ENT)'),
					('OL', 'Optional Law Course'),
					('CN', 'Compulsory Non Law Course'),
					('OT', 'Others; Non Law/University Course')]
	LEVEL_CHOICE = [
				('1', '100 Level'),
				('2','200 Level'),
				('3', '300 Level'),
				('4', '400 Level'),
				('5', '500 Level'),
				]
	SEMESTER_CHOICE = [
						('1', 'First Semester'),
						('2', 'Second Semester')]
	level= models.CharField(verbose_name = 'Current Level',max_length = 1, choices= LEVEL_CHOICE, blank = True, null = True)
	semester = models.CharField(verbose_name = 'Current Semester', max_length = 1, choices = SEMESTER_CHOICE, blank =  True, null = True)
	title = models.CharField(max_length= 100, unique = True, verbose_name = 'Course Title')
	code  = models.CharField(max_length= 7, unique = True, verbose_name= 'Course Code')
	units = models.IntegerField( verbose_name = 'Units', default = 4)
	description  = models.CharField(max_length= 150, unique = True, verbose_name = 'Course Description')
	designation = models.CharField(max_length=2, choices = COURSE_TYPE, verbose_name = 'Course Type')
	outline = models.TextField(verbose_name = 'Course Outline')
	student = models.ManyToManyField(Student, through = 'Course_Registration', related_name = 'Students')

	def __repr__(self):
		return rf'Course({self.code})'

	def __str__(self):
		return f'{self.code}: {self.title}'

class Semester(models.Model):
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
						('2', 'Second Semester')]
	
	session= models.CharField(verbose_name = 'Academic Session', max_length= 3, choices = SESSION_CHOICE )
	semester = models.CharField(max_length=1, choices = SEMESTER_CHOICE, verbose_name = 'Semester', )
	current_semester = models.BooleanField(default = False)
	
	def __str__(self):
		return f'{self.get_semester_display()}, {self.get_session_display()}'
@receiver(pre_save, sender= Semester)
def ensure_single_current_semester(sender, instance, **kwargs):
	if instance.current_semester:
		Semester.objects.exclude(id=instance.id).update(current_semester = False)

class Course_Registration(models.Model):
	semester = models.ForeignKey(Semester, on_delete = models.CASCADE, blank = True, null = True )
	courses = models.ForeignKey(Course, on_delete= models.CASCADE, blank= True, null = True) 
	student = models.ForeignKey(Student, on_delete = models.CASCADE, blank = True, null = True)
	
	
	

	class Meta:
		verbose_name = 'Course Registration'
		verbose_name_plural = 'Courses Registration'

	def __str__(self):
		return f'{self.get_semester_display()}, {self.get_session_display()}'

	def __str__(self):
		return f'{self.student}:{self.courses} in {self.semester}'


class Score(models.Model):
	''' model for scores for each course '''
	test = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)
	exam = models.DecimalField(max_digits = 4, decimal_places = 2, blank = True, null = True)
	total  = models.DecimalField(max_digits = 4, decimal_places = 0, blank = True, null = True)
	grade = models.CharField(max_length = 1, blank = True, null = True)
	status = models.CharField(max_length= 12, default = 'Pending', blank =True, null =True)
	course_score = models.ForeignKey(Course_Registration, on_delete = models.CASCADE, null = True, blank = True)

	def save (self, *args, **kwargs):
		self.total = self.test + self.exam
		if 69.99 < self.total <= 100.0:
			self.grade = 'A'
			self.status = 'Passed'
		elif 59.99 < self.total <= 69.99:
			self.grade = 'B'
			self.status = 'Passed'
		elif 49.99 < self.total <= 59.99:
			self.grade = 'C'
			self.status = 'Passed'
		elif 44.99 < self.total <= 49.99:
			self.grade = 'D'
			self.status = 'Passed'
		elif 39.99 < self.total <= 49.99:
			self.grade = 'E'
			self.status = 'Passed'
		elif self.total < 40.00:
			self.grade = 'F'
			self.status = 'Outstanding'
		elif self.total > 100:
			raise ValueError ('Score cannot be more than 100 marks, Please check the score')
		super().save(*args, **kwargs)

	def __str__(self):
		return f'Score for {self.course_score.student.username} in {self.course_score.courses} for {self.course_score.semester}: {self.grade} '

class Brief(models.Model):
	STUDENT_STATUS_CHOICE = [
								('GS', 'Good Standing'),
								('PR', 'Probation'),
								('LA', 'Leave of Absence'),
								]
	student = models.ForeignKey(Student, on_delete = models.DO_NOTHING)
	semester = models.ForeignKey(Semester, on_delete= models.DO_NOTHING)
	student_status = models.CharField(max_length= 20, choices =STUDENT_STATUS_CHOICE, blank = True, null = True)
	TCP = models.IntegerField( verbose_name = 'Total Credit Passed', blank= True, null = True) #calculated by multiplying grade by unit of courses taken by a student in a semester. If a student takes 3 courses, one 4 units, one 3 units and the last 2 units and  score A,B and F respectively, the TCP is (4*5) + (3*4) + (2*0) which is 32.
	TLU = models.IntegerField(verbose_name = 'Total Load Unit', blank= True, null = True)# calculated by adding all the units taken by a student in a semester. for the example above, the TLU of the student is 9 since the courses are just 3, a  4 units, a 3 units and a 2 units course.
	GPA = models.DecimalField(max_digits = 3, decimal_places= 2, verbose_name = 'Grade Point Average', blank= True, null = True) #caalculated by dividing the TCP of a student by the TLU, for the above example, the GPA is 32/9 which is 3.56 ~ to 2 decimal places.
	is_registered = models.BooleanField(default= False)
	deans_list = models.BooleanField(default = False, verbose_name = 'Dean\'s List')

	def save(self, *args, **kwargs):
		if self.is_registered and self.student_status != 'LA':
			if self.TCP is not None and self.TLU is not None:
				self.GPA = Decimal(self.TCP/self.TLU)
		elif self.student_status == 'LA':
			self.compulsory = self.optional_law = self.optional_others = self.gst = wself.compulsory_other = self.main = self.outstanding = self.total = 0
			self.TCP = self.TLU = self.GPA = None
		else:
			self.GPA = None

		if self.is_registered and self.total == self.TCP and self.GPA >= 4.50:
			self.deans_list = True
		if self.is_registered and self.GPA < 1.00:
			self.student_status == 'PR'
		super().save(*args, **kwargs)	

class Course_uploads(models.Model):
	course = models.ForeignKey(Course, on_delete = models.DO_NOTHING)
	files = models.FileField(verbose_name = 'Course Materials', upload_to = upload_directory, blank = True, null = True, validators = [FileExtensionValidator(allowed_extensions = ['pdf', 'jpg', 'png', 'gif', 'doc', 'docx', 'csv', 'xlsx']) ,FileSizeValidator])

	class Meta:
		verbose_name = 'Uploads for Courses'
		verbose_name_plural = 'Uploads for Courses'

	def __str__(self):
		return f'{str(self.files).split("/")[-1]}:{self.course.code}'
