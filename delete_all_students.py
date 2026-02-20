"""
Script to delete all students and their related data
WARNING: This will permanently delete all student records, user accounts, and attendance data
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsense.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Student
from attendance.models import Attendance

print('\n⚠️  WARNING: PERMANENT DELETION ⚠️')
print('=' * 60)
print('This script will PERMANENTLY DELETE:')
print('✗ ALL student profiles')
print('✗ ALL student user accounts')
print('✗ ALL attendance records')
print('✗ ALL face recognition data')
print('=' * 60)

# Get counts
student_count = Student.objects.count()
attendance_count = Attendance.objects.count()
student_user_count = User.objects.filter(is_staff=False, faculty_profile__isnull=True).count()

print(f'\nCurrent Database Status:')
print(f'  - Students: {student_count}')
print(f'  - Student User Accounts: {student_user_count}')
print(f'  - Attendance Records: {attendance_count}')

if student_count == 0:
    print('\n✓ No students found in database. Nothing to delete.')
    exit(0)

print('\n' + '=' * 60)
confirmation = input('\nType "DELETE ALL" to confirm permanent deletion: ')

if confirmation != 'DELETE ALL':
    print('\n✓ Deletion cancelled.')
    exit(0)

print('\n🗑️  Starting deletion process...\n')

try:
    # Delete all student user accounts
    deleted_users = 0
    for student in Student.objects.all():
        user = User.objects.filter(username=student.roll_number).first()
        if user:
            user.delete()
            deleted_users += 1
            print(f'  ✓ Deleted user account: {student.roll_number}')
    
    # Delete all students (this will cascade delete attendance records)
    deleted_students = Student.objects.all().delete()
    
    print('\n✅ Deletion completed successfully!')
    print(f'\n📊 Summary:')
    print(f'  - Students deleted: {student_count}')
    print(f'  - User accounts deleted: {deleted_users}')
    print(f'  - Attendance records deleted: {attendance_count} (cascade)')
    print(f'\nDatabase is now clean.')
    
except Exception as e:
    print(f'\n❌ Error during deletion: {str(e)}')
    exit(1)
