from django.contrib import admin
from .models import student,profile,Student_choices

# Register your models here.
admin.site.register(student)
admin.site.register(profile)
admin.site.register(Student_choices)
