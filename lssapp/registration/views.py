from django.shortcuts import render, HttpResponse, redirect
from .admin import StudentForm
from .models import Student
from courses.models import Course_Registration, Course, Score, Semester, Course_uploads, Brief
from courses.forms import RegistrationForm, ScoreForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import formset_factory
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP

# Create your views here.
def signup(request):
	if request.method == 'POST':
		form = StudentForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return HttpResponse('Done')
		else:
			messages.warning(request, form.errors)
			return redirect('reg:signup')
	else:
		form = StudentForm()
		return render(request, 'registration/signup.html', {'form': form})

def student_login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		student_user = authenticate(request, username  = username, password = password)
		if student_user is not None:
			login(request, student_user)
			student = Student.objects.get(user_ptr_id=request.user.id)
			if student.entry_mode == 'UTME':
				request.session['registration_session'] = 1
			elif student.entry_mode == 'DE':
				request.session['registration_session'] = 2
			request.session['registration_semester'] = 1
			current_semester = Semester.objects.get(current_semester = True)
			if student.session == current_semester.session:
				return redirect('reg:register_course')
			else:
				messages.warning(request, 'There is something wrong with your information, please contact an admin or upload proof of Leave of Absence')
				return redirect('student/leave_of_abs.html')


			return redirect('reg:home')
		else:
			messages.warning(request,'Matriculation and/or Password is incorrect')
			return redirect('login')
	else:
		return render(request, 'registration/login.html', {})

def dashboard(request):
	student = student.objects.get(user_ptr_id = request.user.id)
	return render(request, 'base.html', {'student':student})


@login_required
def profile(request):
	profile = request.user
	courses = Course_Registration.objects.filter(student = profile)
	return render(request, 'student/profile.html', {'profile':profile, 'courses':courses})

@login_required
def register_course(request):
	student = Student.objects.get(user_ptr_id = request.user.id)
	registration_session = request.session.get('registration_session')
	registration_semester = request.session.get('registration_semester')
	current_semester = Semester.objects.get(current_semester = True)
	if registration_session < 6: 
		levels = f'{registration_session}00 Level'
	elif registration_session == 6:
		levels = 'Spill One'
	elif registration_session == 7:
		levels = 'Spill Two'
	session = int(current_semester.session) - (int(student.level) - registration_session)
	semester = Semester.objects.get(session= session, semester = registration_semester)
	semester_courses = Course.objects.filter(semester = registration_semester)
	main = semester_courses.filter(level = registration_session)
	if student.entry_mode == 'UTME':
		gst = main.filter(designation = 'CU')
		law_compulsory = main.filter(designation = 'CL')
	elif student.entry_mode == 'DE' and registration_session == 2:
		gst = main.filter(designation ='CU').exclude(code = ('GST 211') or ('GST 222'))
		if registration_semester == 1:
			law_compulsory = Course.objects.filter(Q(semester = registration_semester, level = registration_session, designation = 'CL')|Q (code ='JIL 101'))
		elif registration_semester == 2:
			law_compulsory = Course.objects.filter(Q(semester = registration_semester, level = registration_session, designation = 'CL')|Q (code ='JIL 102'))
	elif student.entry_mode == 'DE' and registration_session == 3:
		gst = semester_courses.filter(Q(code = ('GST 121'))|Q (code ='GST 113') |Q (code = 'GST 123') |Q (code ='GST 211') |Q (code ='GST 222'))

	nonlaw_compulsory = main.filter(designation = 'CN')
	law_electives = main.filter(designation = 'OL')
	others = main.filter(designation = 'OT')
	try:
		outstanding = semester_courses.filter(course_registration__score__status = 'Outstanding')
	except Course.DoesNotExist:
		outstanding = None	
	context = {'student':student, 'semester_courses':semester_courses, 'main':main, 'law_compulsory': law_compulsory, 'gst':gst, 'nonlaw_compulsory': nonlaw_compulsory, 'law_electives': law_electives, 'others':others, 'outstanding':outstanding, 'registration_session':registration_session, 'registration_semester':registration_semester, 'session': session, 'semester':semester, 'levels': levels}
	if registration_session < int(student.session) or (registration_session == int(student.session) and registration_semester <= int(student.semester)):
		if request.method == 'POST':
			law_comp = request.POST.getlist('lc')
			gst = request.POST.getlist('gst')
			other_comp = request.POST.getlist('nc')
			law_elect = request.POST.getlist('le')
			other_elect = request.POST.getlist('ne')
			outstand = request.POST.getlist('fc')
			total_courses = [Course.objects.get(code=course[0:7]) for course in law_comp + gst + other_comp + law_elect + other_elect + outstand]
			count_elect_law = sum(1 for course in total_courses if course.designation =='OL' )
			count_elect_other = sum(1 for course in total_courses if course.designation =='OT')
			total_units = sum(course.units for course in total_courses)
			if total_units > 28:
				messages.warning(request, 'You cannot register more than 28 units, please review and adjust accordingly')
				return redirect('reg:register_course')
			if registration_session ==  1:
				if count_elect_other < 2:
					messages.warning(request, 'The minimum units for non-law electives is 6. You must register at least 2 non-law elective courses')
					return redirect('reg:register_course')
			elif registration_session == 2 or 3 or 4:
				if count_elect_law < 1:
					messages.warning(request, 'The minimum units for law electives is 4. You must register at least 1 law elective course')
					return redirect('reg:register_course')
				elif count_elect_other < 1:
					messages.warning(request, 'The minimum units for non-law electives is 3. You must register at least 1 non-law elective course')
					return redirect('reg:register_course')
			elif registration_session == 5 and registration_semester == 1:
				if count_elect_law < 2:
					messages.warning(request, 'The minimum units for law electives is 8. You must register at least 2 law elective courses')
					return redirect('reg:register_course')
			elif registration_session == 5 and registration_semester == 2:
				messages.warning(request, 'The minimum units for law electives is 4. You must register at least 1 law elective courses')
				return redirect('reg:register_course')
			for course in total_courses:
				if not Course_Registration.objects.filter(**{'student_id':student.id, 'semester': semester, 'courses': course}).exists():
					Course_Registration.objects.create(student = student, semester = semester, courses = course)
				else:
					message.warning('You have registered for this semester or something is wrong with your Page, please contact the admin')
			request.session['registration_session'] = registration_session
			request.session['registration_semester'] = registration_semester
			return redirect('reg:add_score')
	elif registration_session > int(student.session) or (registration_session == int(student.session) and registration_semester > int(student.semester)):
		return redirect(dashboard)
	return render(request, 'student/reg_courses.html', context)



@login_required
def add_score(request):
	student = Student.objects.get(user_ptr_id = request.user.id)
	registration_session = request.session.get('registration_session')
	registration_semester = request.session.get('registration_semester')
	current_semester = Semester.objects.get(current_semester = True)
	if registration_session < 6: 
		levels = f'{registration_session}00 Level'
	elif registration_session == 6:
		levels = 'Spill One'
	elif registration_session == 7:
		levels = 'Spill Two'
	session = int(current_semester.session) - (int(student.level) - registration_session)
	semester = Semester.objects.get(session= session, semester = registration_semester)
	equals = (int(student.session) == session) and (int(student.semester) == registration_semester)
	semester_courses =  Course_Registration.objects.filter(student = student, semester = semester)
	context = {'equals':equals, 'semester_courses':semester_courses, 'semester': semester, 'levels': levels}
	if request.method == 'POST':
		semester_registration = request.POST.getlist('semester_registration')
		course = [Course.objects.get(code = semester_registration[i][0:7]) for i in range(len(semester_registration)) ]
		print(semester_registration)
		print (course)
		courses_score = [Course_Registration.objects.get(student = student, courses = cours, semester = semester) for cours in course]
		print (courses_score)
		for course in courses_score:
			Score.objects.create(course_score = course, test = float(request.POST[f'{course}Test']), exam = float(request.POST[f'{course}Exam']))
			print (Score.objects.all())
		if 'proceed' in request.POST:
			proceed = request.POST['proceed']
			if proceed == 'dashboard':
				request.session['registration_session'] = registration_session
				request.session['registration_semester'] = registration_semester
				return redirect('reg:semester_dashboard')
			elif proceed == 'nextReg':
				if registration_semester == 1:
					request.session['registration_session'] = registration_session
					request.session['registration_semester'] = 2
				elif registration_semester == 2:
					request.session['registration_session'] = registration_session + 1
					request.session['registration_semester'] = 1
					return redirect('reg:register_course')
	return render(request, 'student/course.html', context)

@login_required
def semester_dashboard(request):
	student = Student.objects.get(user_ptr_id = request.user.id)
	registration_session = request.session.get('registration_session')
	registration_semester = request.session.get('registration_semester')
	current_semester = Semester.objects.get(current_semester = True)
	session = int(current_semester.session) - (int(student.level) - registration_session)
	semester = Semester.objects.get(session = session, semester = registration_semester)
	brief = Brief.objeects.create(student = student, semester = semester)
	if registration_session < 6: 
		levels = f'{registration_session}00 Level'
	elif registration_session == 6:
		levels = 'Spill One'
	elif registration_session == 7:
		levels = 'Spill Two'
	registrations = Course_Registration.objects.filter( student = student, semester = semester)
	course_score_ids = registrations.values_list('id', flat = True)
	semester_registrations = Score.objects.filter(course_score_id__in = course_score_ids)
	TLU = 0
	TCP = 0	
	Grade_point = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
	for course in semester_registrations:
		TLU += course.course_score.courses.units
		TCP += (course.course_score.courses.units * Grade_point[course.grade]) 
		brief.TLU = TLU
		brief.TCP = TCP
		brief.save()
	GPA = Decimal(TCP/TLU).quantize(Decimal('0.01'), rounding = ROUND_HALF_UP)

	all_registrations = Course_Registration.objects.filter( student = student)
	all_course_score_ids = registrations.values_list('id', flat = True)
	all_semester_registrations = Score.objects.filter(course_score_id__in = course_score_ids)
	student.CTLU = 0
	student.CTCP = 0
	student.TUP = 0
	for all_course in all_semester_registrations:
		student.CTLU += all_course.course_score.courses.units
		student.CTCP += (all_course.course_score.courses.units * Grade_point[all_course.grade])
		student.save()
		if all_course.status != 'Outstanding':
			student.TUP += all_course.course_score.courses.units
			student.save()
	if registration_semester == 1:
		request.session['registration_session'] = registration_session
		request.session['registration_semester'] = 2
	elif registration_semester == 2:
		request.session['registration_session'] = registration_session + 1
		request.session['registration_semester'] = 1
		return redirect('reg:register_course')


	context = {'student':student, 'semester_registrations':semester_registrations, 'levels':levels, 'semester':semester, 'TLU':TLU,'TCP': TCP,'GPA':GPA}
	return render(request, 'student/semester_brief.html', context)

	

def courses_detail(request, id):
	course = Course.objects.get(id = id)
	uploads = Course_uploads.objects.filter(course= course)
	return render(request, 'student/course.html', {'course': course, 'uploads':uploads})
	

# @login_required
# def reg_semester(request):
# 	default = Semester.objects.get(id = 13)
# 	semesters = Semester.objects.all()
# 	if request.method =='POST':
# 	  	semester= request.POST.get('current semester')
# 	  	student = request.user	  	
# 	  	if not Course_Registration.objects.filter(**{'student':student, 'semester': Semester.objects.get(id=semester) }).exists():
# 	  		registered_student = Course_Registration.objects.create(student= Student(user_ptr_id=student.id), semester = Semester.objects.get(id = semester))
# 	  		registered_student.save()
# 	  		request.session['registered_student_id'] = registered_student.id
# 	  		return redirect('reg:courses', student_id = student.id, semester_id = semester)
# 	  	else:
# 	  		messages.success(request, 'You have already been captured, Kindly proceed to your Course Dashboard to register your Courses')
# 	  		return redirect('reg:profile')
# 	print (request.user)  	
# 	return render(request, 'student/semester_select.html', {'semesters': semesters, 'default':default})

# @login_required
# def reg_sem_course(request, student_id, session = '1', semester = '1'):
# 	one = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if course.code[4]=='1']
# 	two = [course for course in courses in Course.objects.filter(Q(code__endswith='2')|Q(code__endswith='4')|Q(code__endswith='6')|Q(code__endswith='8')|Q(code__endswith='0')) if course.code[4]=='1']
# 	three = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if course.code[4]=='2']
# 	four = [course for course in courses in Course.objects.filter(Q(code__endswith='2')|Q(code__endswith='4')|Q(code__endswith='6')|Q(code__endswith='8')|Q(code__endswith='0')) if course.code[4]=='2']
# 	five = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if course.code[4]=='3']
# 	six = [course for course in courses in Course.objects.filter(Q(code__endswith='2')|Q(code__endswith='4')|Q(code__endswith='6')|Q(code__endswith='8')|Q(code__endswith='0')) if course.code[4]=='3']
# 	seven = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if course.code[4]=='4']
# 	eight = [course for course in courses in Course.objects.filter(Q(code__endswith='2')|Q(code__endswith='4')|Q(code__endswith='6')|Q(code__endswith='8')|Q(code__endswith='0')) if course.code[4]=='4']
# 	nine = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if course.code[4]=='5']
# 	ten = [course for course in courses in Course.objects.filter(Q(code__endswith='2')|Q(code__endswith='4')|Q(code__endswith='6')|Q(code__endswith='8')|Q(code__endswith='0')) if course.code[4]=='5']
# 	student = Student.objects.get(id = student_id)
# 	a = student.filter(level = '1', semes = '1')
# 	b = student.filter(level = '1', semes = '2')
# 	c = student.filter(level = '2', semes = '1')
# 	d = student.filter(level = '2', semes = '2')
# 	e = student.filter(level = '3', semes = '1')
# 	f = student.filter(level = '3', semes = '2')
# 	g = student.filter(level = '4', semes = '1')
# 	h = student.filter(level = '4', semes = '2')
# 	i = student.filter(level = '5', semes = '1')
# 	j = student.filter(level = '5', semes = '2')
# 	k = student.filter(level = '6', semes = '1')
# 	l = student.filter(level = '6', semes = '2')
# 	m = student.filter(level = '7', semes = '1')
# 	n = student.filter(level = '7', semes = '2')
# 	match_course_dict = {'1':one, '2': two, '3': three, '4': four, '5': five, '6': six, '7': seven, '8': eight, '9': nine, '10': ten}
# 	match_student_dict = {a:1, b: 2, c:3, d: 4, e:5, f:6, g: 7, h:8 , i:9, j:10, k:11, l:12, m:13, n:14 }
# 	no_courses = int(request.POST.get('number of courses'))
# 	RegistrationFormSet = formset_factory(RegistrationForm, extra = no_courses) 
# 	formset =  RegistrationFormSet(request.POST)
# 	if formset.is_valid():
# 		for form in formset:
# 			if form.cleaned_data.get('course') and form.cleaned_data.get('semester'):
# 				registration = form.save(commit = False)
# 				registration.student = student
# 				registration.save()
# def reg_one_one(request, student_id, semester_id):
# 	compulsory_laws = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if (course.code[4]=='1' and course.designation=='CL')]
# 	gsts = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if (course.code[4]=='1' and course.designation=='CU')]
# 	uni_comps = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if (course.code[4]=='1' and course.designation=='CN')]
# 	electives = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if (course.code[4]=='1' and course.designation=='OL')]
# 	others = [course for course in courses in Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9')) if (course.code[4]=='1' and course.designation=='OT')]
# 	student = Student.objects.get(id = student_id)
# 	if student.level == '1' and student.semes =='1':
# 		if request.method == 'POST'
# 		selected_courses = request.POST.getlist('selected courses')
# 		for course in selected_courses:
# 			if not Course_Registration.objects.filter(**{'student_id':student_id, 'semester_id': semester_id, course_id: course.id}).exists():
# 			registered_student.objects.create(course_id = course.id)
# 			registered_student.save()
# 			return rediret('reg:one_score')





# @login_required
# def reg_courses(request, semester_id):
# 	registered_student_id = request.session.get('registered_student_id')
# 	if registered_student_id:
# 		rj = Course_Registration.objects.get(id = registered_student_id)
# 	if rj.semester.semester_ch == '1':
# 		available_courses = Course.objects.filter(Q(code__endswith='1')|Q(code__endswith='3')|Q(code__endswith='5')|Q(code__endswith='7')|Q(code__endswith='9'))
# 	else:
# 		available_courses = Course.objects.filter(Q(code__endswith='0')|Q(code__endswith='2')|Q(code__endswith='4')|Q(code__endswith='6')|Q(code__endswith='8'))
# 	compulsory = available_courses.filter(designation ='CL')
# 	gst = available_courses.filter(designation='CU')
# 	uni_compulsory = available_courses.filter(designation='CN')
# 	electives = available_courses.filter(designation='OL')
# 	others = available_courses.filter(designation='OT')
# 	# outstanding = Course_Registration.objects.all().filter

# 	if request.method == 'POST':
# 		form = RegistrationForm(request.POST)
# 		if form.is_valid():
# 			registration = form.save(commit = False)
# 			registration.student = student_courses
# 			registration.save()
# 			print(registered_student.semester)
# 			return redirect('home')
# 	else:
# 		form = RegistrationForm()
# 		context = {
# 		'form':form,
# 		'available_courses':available_courses,
# 		'compulsory':compulsory,
# 		'gst':gst,
# 		'uni_compulsory':uni_compulsory,
# 		'electives':electives,
# 		'others':others
# 		# 'outstanding':outstanding
# 		}
# 		print (Student.username)
# 		return render(request, 'student/reg_courses.html', context)



