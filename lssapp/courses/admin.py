from django.contrib import admin
from .models import Course, Semester, Course_Registration, Brief, Course_uploads, Score
from import_export.admin import ImportExportModelAdmin

class CourseExport(ImportExportModelAdmin, admin.ModelAdmin):
	...

# Register your models here.
admin.site.register(Course, CourseExport)
admin.site.register(Course_Registration)
admin.site.register(Course_uploads)
admin.site.register(Brief)
admin.site.register(Score)
admin.site.register(Semester)