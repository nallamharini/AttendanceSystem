"""
Script to create User accounts for existing students
This is needed for students who were registered before the user creation was implemented
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsense.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Student

print('Creating user accounts for existing students...\n')

students_without_users = []
created_count = 0
skipped_count = 0

for student in Student.objects.filter(is_active=True):
    # Check if user already exists
    if User.objects.filter(username=student.roll_number).exists():
        print(f'⏭️  Skipping {student.name} (Roll: {student.roll_number}) - User already exists')
        skipped_count += 1
        continue
    
    try:
        # Create user account
        user = User.objects.create_user(
            username=student.roll_number,
            email=student.email,
            password=student.roll_number,  # Default password = roll number
            first_name=student.name.split()[0] if student.name else '',
            last_name=' '.join(student.name.split()[1:]) if len(student.name.split()) > 1 else ''
        )
        user.is_staff = False
        user.save()
        
        print(f'✅ Created user for {student.name} (Roll: {student.roll_number})')
        print(f'   Username: {student.roll_number}')
        print(f'   Password: {student.roll_number}')
        created_count += 1
        
    except Exception as e:
        print(f'❌ Error creating user for {student.name}: {str(e)}')

print('\n📊 Summary:')
print(f'   Created: {created_count}')
print(f'   Skipped: {skipped_count}')
print(f'   Total students: {Student.objects.filter(is_active=True).count()}')
