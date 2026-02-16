"""
Script to check student profile for user
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsense.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Student

# Check for user with username '2'
username = '2'
print(f'Checking student profile for user: {username}\n')

if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f'✅ User found!')
    print(f'   Username: {user.username}')
    
    # Check if student exists with this roll number
    if Student.objects.filter(roll_number=username).exists():
        student = Student.objects.get(roll_number=username)
        print(f'\n✅ Student profile found!')
        print(f'   Name: {student.name}')
        print(f'   Roll: {student.roll_number}')
        print(f'   Email: {student.email}')
        print(f'   Branch: {student.branch}')
        print(f'   Year: {student.year}')
        print(f'   Is Active: {student.is_active}')
    else:
        print(f'\n❌ No student profile found for roll number: {username}')
        print(f'\nAll students:')
        for s in Student.objects.all()[:5]:
            print(f'   - {s.name} (Roll: {s.roll_number})')
else:
    print(f'❌ User not found!')
