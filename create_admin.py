"""
Script to create a superuser for SmartSense system
Run this script to create an admin account
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsense.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser
username = 'admin'
email = 'admin@smartsense.com'
password = 'admin123'  # Change this password after first login!

if User.objects.filter(username=username).exists():
    print(f'❌ Admin user "{username}" already exists!')
else:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print('✅ Superuser created successfully!')
    print(f'   Username: {username}')
    print(f'   Email: {email}')
    print(f'   Password: {password}')
    print('\n⚠️  IMPORTANT: Change the password after first login!')
