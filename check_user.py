"""
Script to check user authentication
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsense.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Check for user with username '2'
username = '2'
print(f'Checking user: {username}\n')

if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f'✅ User found!')
    print(f'   Username: {user.username}')
    print(f'   Email: {user.email}')
    print(f'   Is active: {user.is_active}')
    print(f'   Is staff: {user.is_staff}')
    print(f'   Password hash: {user.password[:50]}...')
    
    # Try to authenticate with different passwords
    print(f'\n🔐 Testing authentication:')
    
    # Test with roll number as password
    test_user = authenticate(username=username, password='2')
    if test_user:
        print(f'   ✅ Password "2" works!')
    else:
        print(f'   ❌ Password "2" does NOT work')
    
    # Ask for the password they're trying
    print('\n💡 Please enter the password you reset to (or press Enter to skip):')
    try:
        test_password = input('Password: ')
        if test_password:
            test_user = authenticate(username=username, password=test_password)
            if test_user:
                print(f'   ✅ Password "{test_password}" works!')
            else:
                print(f'   ❌ Password "{test_password}" does NOT work')
                
                # Check if user has a usable password
                print(f'\n   Has usable password: {user.has_usable_password()}')
                
                # Try to manually set and test
                print(f'\n   Setting password to "{test_password}" and testing...')
                user.set_password(test_password)
                user.save()
                
                test_user = authenticate(username=username, password=test_password)
                if test_user:
                    print(f'   ✅ After manual set, password works!')
                else:
                    print(f'   ❌ After manual set, password STILL does not work')
    except:
        pass
else:
    print(f'❌ User not found!')
