from django.contrib import admin
from .models import Student, Faculty

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'name', 'email', 'department', 'phone')
    search_fields = ('roll_number', 'name', 'email')
    list_filter = ('department', 'is_active')

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'name', 'email', 'department', 'phone', 'is_active')
    search_fields = ('faculty_id', 'name', 'email', 'department')
    list_filter = ('department', 'is_active')
    list_editable = ('is_active',)
