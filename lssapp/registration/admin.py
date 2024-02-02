from django.contrib import admin
from django import forms
from django.forms.widgets import DateInput
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Student
import re
# Register your models here.
regex = re.compile(r'^(?:\d{9}|\d{10}[a-zA-Z]{2})$')
class StudentForm(forms.ModelForm):
	'''A form for creating new students. Includes all required field as well as repeated passwords.'''
	password1 =forms.CharField(label= 'Password', widget= forms.PasswordInput)
	password2 = forms.CharField(label= 'Confirm Password', widget= forms.PasswordInput)
	d_o_b_form = forms.DateField(widget= DateInput (attrs={'type':'date', 'placeholder': 'DD-MM-YYYY'}), label = 'Date of Birth')

	class Meta:
		model = Student
		fields = ['username', 'name', 'email', 'd_o_b_form',  'level', 'gender', 'phone_no', 'entry_mode', 'evid']
		labels = {'username': 'Matriculation Number', 'name': 'Full Name', 'email': 'Electronic Mail'}

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			raise ValidationError('Please your passwords do not match, try again')
		return password2

	def clean_username(self):
		username = self.cleaned_data['username']
		if not regex.match(username):
			raise ValidationError('Invalid Matriculation Number, Enter the correct Matriculation Number or JAMB Registration  Number if you are in 100 level')
		return username


	def save(self, commit=True):
		student = super().save(commit=False)
		student.set_password(self.cleaned_data['password1'])
		student.d_o_b = self.cleaned_data['d_o_b_form']
		student.name = self.cleaned_data['name'].title()
		if commit:
			student.save()
		return student
class StudentChangeForm(forms.ModelForm):
	'''A form for updating users. Includes all the fields on the user, but replaces the password field with admin's disabled password hash display field. '''
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = Student
		fields = ['username', 'email', 'password', 'd_o_b', 'level',  'gender', 'phone_no', 'entry_mode']

class StudentAdmin(BaseUserAdmin):
	form = StudentChangeForm
	add_form = StudentForm
	list_display = ['username', 'name', 'level', 'is_active']
	list_filter = ['is_active']
	fieldsets = [
	(None, {'fields': ['username', 'email', 'password']}), 
	('Personal info', {'fields': ['d_o_b','entry_mode']}), 
	('Permissions', {'fields': ['is_active']}), 
	('Current Academic info',{'fields':['session','semester', 'level', 'CGPA', 'TUP', 'CTCP', 'CTLU', 'student_status']}),]
	add_fieldsets = [
	(None,{ 'classes': ['wide'],
	'fields': ['username', 'name', 'email', 'd_o_b_form',  'level',  'gender', 'phone_no', 'entry_mode', 'password1', 'password2'],},),
	]
	search_fields = ['username']
	ordering = ['username']
	filter_horizontal = []

	def formfield_for_dbfield(self, db_field, **kwargs):
		formfield = super().formfield_for_dbfield(db_field, **kwargs)
		if db_field.name == 'username':
			formfield.label = 'Matriculation Number'
		if db_field.name == 'name':
			formfield.label = 'Full Name'
		if db_field.name == 'email':
			formfield.label = 'Electronic Mail'
		return formfield

admin.site.register(Student, StudentAdmin)
