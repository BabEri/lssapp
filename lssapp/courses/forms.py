from django import forms
from .models import Course_Registration, Score, Semester

class RegistrationForm(forms.ModelForm):
	class Meta:
		model = Course_Registration
		fields = ['courses', 'student', 'semester', ]


class ScoreForm(forms.ModelForm):
	class Meta:
		model = Score
		fields = ['test', 'exam', 'course_score']

class SemesterForm(forms.ModelForm):
	class Meta:
		model = Semester
		fields ='__all__'