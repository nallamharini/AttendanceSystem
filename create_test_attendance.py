"""
Script to create test attendance for a student
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

print('\n📋 Creating Test Attendance\n')

# Get the student
students = Student.objects.filter(is_active=True)

if not students.exists():
    print('❌ No students found in database.')
    print('Please register a student first!')
    exit(1)

student = students.first()
print(f'Student: {student.name} ({student.roll_number})')

# Get today's date
today = timezone.now().date()

# Check if attendance already exists
existing = Attendance.objects.filter(student=student, date=today).first()

if existing:
    print(f'\n⚠️  Attendance already exists for today:')
    print(f'   Entry Time: {existing.entry_time}')
    print(f'   Is Late: {existing.is_late}')
    print(f'\nDeleting existing record...')
    existing.delete()

# Create test attendance
print(f'\nChoose a test scenario:')
print('1. On Time Entry (9:30 AM)')
print('2. Late Entry (10:00 AM)')
print('3. Very Late Entry (10:15 AM)')

choice = input('\nEnter choice (1-3): ')

if choice == '1':
    entry_time = time(9, 30)
    is_late = False
    print('\n✅ Creating ON TIME attendance...')
elif choice == '2':
    entry_time = time(10, 0)
    is_late = True
    print('\n⚠️  Creating LATE attendance...')
elif choice == '3':
    entry_time = time(10, 15)
    is_late = True
    print('\n⚠️  Creating LATE attendance...')
else:
    print('Invalid choice!')
    exit(1)

# Create attendance record
attendance = Attendance.objects.create(
    student=student,
    date=today,
    entry_time=entry_time,
    is_late=is_late,
    status='ENTRY'
)

print(f'\n✅ Test attendance created successfully!')
print(f'   Student: {student.name}')
print(f'   Entry Time: {attendance.entry_time.strftime("%I:%M %p")}')
print(f'   Status: {"LATE" if is_late else "ON TIME"}')
print(f'\n🔄 Refresh the student list page to see the changes!')
