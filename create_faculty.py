"""
Script to create a faculty user for SmartSense system
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsense.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Faculty

def create_faculty():
    print("=" * 60)
    print("Create Faculty Account - SmartSense")
    print("=" * 60)
    
    # Get faculty details
    username = input("\nEnter username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        return
    
    # Check if username exists
    if User.objects.filter(username=username).exists():
        print(f"Error: User with username '{username}' already exists")
        return
    
    email = input("Enter email: ").strip()
    if not email:
        print("Error: Email cannot be empty")
        return
    
    # Check if email exists
    if Faculty.objects.filter(email=email).exists():
        print(f"Error: Faculty with email '{email}' already exists")
        return
    
    password = input("Enter password: ").strip()
    if not password:
        print("Error: Password cannot be empty")
        return
    
    name = input("Enter full name: ").strip()
    if not name:
        print("Error: Name cannot be empty")
        return
    
    faculty_id = input("Enter faculty ID (e.g., FAC001): ").strip()
    if not faculty_id:
        print("Error: Faculty ID cannot be empty")
        return
    
    # Check if faculty ID exists
    if Faculty.objects.filter(faculty_id=faculty_id).exists():
        print(f"Error: Faculty with ID '{faculty_id}' already exists")
        return
    
    department = input("Enter department: ").strip()
    if not department:
        print("Error: Department cannot be empty")
        return
    
    phone = input("Enter phone number (optional): ").strip()
    
    try:
        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name.split()[0] if name else "",
            last_name=" ".join(name.split()[1:]) if len(name.split()) > 1 else ""
        )
        
        # Create Faculty profile
        faculty = Faculty.objects.create(
            user=user,
            faculty_id=faculty_id,
            name=name,
            email=email,
            department=department,
            phone=phone if phone else "",
            is_active=True
        )
        
        print("\n" + "=" * 60)
        print("✓ Faculty account created successfully!")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Faculty ID: {faculty_id}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Department: {department}")
        if phone:
            print(f"Phone: {phone}")
        print("=" * 60)
        print("\nFaculty can now login at: http://127.0.0.1:8000/login/")
        print("Select 'Faculty' tab and use the credentials above")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error creating faculty: {str(e)}")
        # Rollback - delete user if created
        if User.objects.filter(username=username).exists():
            User.objects.get(username=username).delete()

if __name__ == '__main__':
    create_faculty()
