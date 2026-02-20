"""
Quick script to create test attendance (on time)
"""
import os
import django
from datetime import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsense.settings')
django.setup()

from django.utils import timezone
from accounts.models import Student
from attendance.models import Attendance

print('\n📋 Creating Test Attendance (On Time)\n')

# Get the student
students = Student.objects.filter(is_active=True)

if not students.exists():
    print('❌ No students found in database.')
    exit(1)

student = students.first()
print(f'Student: {student.name} ({student.roll_number})')

# Get today's date
today = timezone.now().date()

# Delete existing attendance if any
Attendance.objects.filter(student=student, date=today).delete()

# Create ON TIME attendance at 9:30 AM
attendance = Attendance.objects.create(
    student=student,
    date=today,
    entry_time=time(9, 30),
    is_late=False,
    status='ENTRY'
)

print(f'\n✅ Test attendance created successfully!')
print(f'   Student: {student.name}')
print(f'   Entry Time: {attendance.entry_time.strftime("%I:%M %p")}')
print(f'   Status: ON TIME')
print(f'\n🔄 Refresh the student list page to see the login time displayed!')
