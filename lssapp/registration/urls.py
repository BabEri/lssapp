from .views import signup, profile, student_login, dashboard, register_course, courses_detail, add_score, semester_dashboard
# home, reg_semester
from django.urls import path, include
app_name = 'reg'


urlpatterns = [
path('accounts/signup/', signup, name = 'signup'),
# path('', home, name ='home'),
path('login', student_login, name = 'login'),
path('profile/', profile, name = 'profile'),
path('dashboard/', dashboard, name = 'dashboard'),
path('register/courses', register_course, name ='register_course'),
path('course/<int:id>', courses_detail, name = 'courses_detail'),
path('score/courses', add_score, name = 'add_score'),
path('semester/dashboard', semester_dashboard, name = 'semester_dashboard')
# path('register/semester', reg_semester, name ='semester'),
]