import base64
import numpy as np
import cv2
import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils import timezone
from django.db.models import Count
from .models import Student, Faculty
from .decorators import admin_required, student_required, faculty_required
from attendance.utils import get_face_encoding
from attendance.models import Attendance

def login_view(request):
    """Login page for admin, faculty, and students"""
    if request.user.is_authenticated:
        # Redirect based on user type
        if request.user.is_staff:
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'faculty_profile'):
            return redirect('faculty_dashboard')
        else:
            return redirect('mark_attendance_view')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'student')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Redirect based on user type
            if user.is_staff:
                messages.success(request, f'Welcome Admin {user.username}!')
                return redirect('admin_dashboard')
            elif hasattr(user, 'faculty_profile'):
                messages.success(request, f'Welcome Faculty {user.faculty_profile.name}!')
                return redirect('faculty_dashboard')
            else:
                messages.success(request, f'Welcome {user.username}!')
                return redirect('mark_attendance_view')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """Logout user"""
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def forgot_password_view(request):
    """Forgot password - Step 1: Enter username/email"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        
        if not identifier:
            messages.error(request, 'Please enter your username or email!')
            return render(request, 'accounts/forgot_password.html')
        
        # Try to find user by username, email, student roll number, or faculty email
        user = None
        
        # Check if it's a username
        if User.objects.filter(username=identifier).exists():
            user = User.objects.get(username=identifier)
        # Check if it's an email
        elif User.objects.filter(email=identifier).exists():
            user = User.objects.get(email=identifier)
        # Check if it's a student email
        elif Student.objects.filter(email=identifier).exists():
            student = Student.objects.get(email=identifier)
            user = User.objects.filter(username=student.roll_number).first()
        # Check if it's a faculty email
        elif Faculty.objects.filter(email=identifier).exists():
            faculty = Faculty.objects.get(email=identifier)
            user = faculty.user
        
        if user:
            # Store username in session and redirect to reset password
            request.session['reset_username'] = user.username
            return redirect('reset_password')
        else:
            messages.error(request, 'No account found with this username or email!')
            return render(request, 'accounts/forgot_password.html')
    
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request):
    """Reset password - Step 2: Enter new password"""
    if request.user.is_authenticated:
        return redirect('home')
    
    # Check if username is in session
    username = request.session.get('reset_username')
    if not username:
        messages.error(request, 'Please submit a password reset request first!')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validate passwords
        if not new_password or not confirm_password:
            messages.error(request, 'Please fill in all fields!')
            return render(request, 'accounts/reset_password.html', {'username': username})
        
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return render(request, 'accounts/reset_password.html', {'username': username})
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'accounts/reset_password.html', {'username': username})
        
        # Update password
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            
            # Verify the password was set correctly by trying to authenticate
            test_user = authenticate(username=username, password=new_password)
            if test_user is None:
                messages.error(request, 'Error: Password update verification failed. Please try again.')
                return render(request, 'accounts/reset_password.html', {'username': username})
            
            # Clear session
            if 'reset_username' in request.session:
                del request.session['reset_username']
            
            # Show success page with username
            return render(request, 'accounts/password_reset_success.html', {'username': username})
            
        except User.DoesNotExist:
            messages.error(request, 'User not found!')
            if 'reset_username' in request.session:
                del request.session['reset_username']
            return redirect('forgot_password')
        except Exception as e:
            messages.error(request, f'Error updating password: {str(e)}')
            return render(request, 'accounts/reset_password.html', {'username': username})
    
    return render(request, 'accounts/reset_password.html', {'username': username})


def signup_view(request):
    """Student self-registration page"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('mark_attendance_view')
    
    return render(request, 'accounts/signup.html')


@csrf_exempt
def student_signup(request):
    """Student self-registration endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            name = data.get('name', '').strip()
            roll_number = data.get('roll_number', '').strip()
            email = data.get('email', '').strip().lower()
            department = data.get('department', 'Computer Science')
            phone = data.get('phone', '').strip()
            password = data.get('password', '').strip()
            confirm_password = data.get('confirm_password', '').strip()
            image_data = data.get('image', '').split(',')[1] if data.get('image') else None
            
            # Validate required fields
            if not all([name, roll_number, email, password, confirm_password, image_data]):
                return JsonResponse({
                    'success': False,
                    'message': 'All fields are required!'
                })
            
            # Validate passwords match
            if password != confirm_password:
                return JsonResponse({
                    'success': False,
                    'message': 'Passwords do not match!'
                })
            
            # Validate password length
            if len(password) < 6:
                return JsonResponse({
                    'success': False,
                    'message': 'Password must be at least 6 characters long!'
                })
            
            # Validate name (at least 3 characters, letters and spaces only)
            if len(name) < 3:
                return JsonResponse({
                    'success': False,
                    'message': 'Name must be at least 3 characters long!'
                })
            
            if not re.match(r'^[a-zA-Z\s]+$', name):
                return JsonResponse({
                    'success': False,
                    'message': 'Name should contain only letters and spaces!'
                })
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid email format!'
                })
            
            # Validate phone number (if provided)
            if phone:
                phone_pattern = r'^[0-9]{10}$'
                if not re.match(phone_pattern, phone):
                    return JsonResponse({
                        'success': False,
                        'message': 'Phone number must be exactly 10 digits!'
                    })
            
            # Check for duplicate roll number
            if Student.objects.filter(roll_number=roll_number).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Roll number "{roll_number}" already exists!'
                })
            
            # Check if username (roll_number) already exists in User table
            if User.objects.filter(username=roll_number).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Roll number "{roll_number}" is already registered!'
                })
            
            # Check for duplicate email
            if Student.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Email "{email}" is already registered!'
                })
            
            # Check for duplicate phone (if provided)
            if phone and Student.objects.filter(phone=phone).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Phone number "{phone}" is already registered!'
                })
            
            # Check for duplicate name (case-insensitive)
            if Student.objects.filter(name__iexact=name).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'A student with name "{name}" is already registered!'
                })
            
            # Decode and process image
            decoded = base64.b64decode(image_data)
            np_arr = np.frombuffer(decoded, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            # Get face encoding
            encoding = get_face_encoding(img)
            
            if encoding is None:
                return JsonResponse({
                    'success': False,
                    'message': 'No face detected! Please capture a clear photo with proper lighting.'
                })
            
            # Create user account first
            try:
                user = User.objects.create_user(
                    username=roll_number,
                    email=email,
                    password=password,  # Use the password provided by student
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                )
                user.is_staff = False
                user.save()
            except Exception as user_error:
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating user account: {str(user_error)}'
                })
            
            # Create student profile
            try:
                student = Student.objects.create(
                    name=name,
                    roll_number=roll_number,
                    email=email,
                    department=department,
                    phone=phone if phone else None
                )
                
                # Save face encoding
                student.set_encoding(encoding)
                student.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'✓ Registration successful! You can now login with Roll Number: {roll_number}',
                    'student_id': student.id
                })
                
            except Exception as student_error:
                # If student creation fails, delete the user to maintain consistency
                user.delete()
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating student profile: {str(student_error)}'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def faculty_signup_view(request):
    """Faculty self-registration page"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'faculty_profile'):
            return redirect('faculty_dashboard')
        return redirect('mark_attendance_view')
    
    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            name = request.POST.get('name', '').strip()
            faculty_id = request.POST.get('faculty_id', '').strip()
            email = request.POST.get('email', '').strip().lower()
            phone = request.POST.get('phone', '').strip()
            department = request.POST.get('department', '').strip()
            
            # Validate required fields
            if not all([username, password, name, faculty_id, email, phone, department]):
                messages.error(request, 'All fields are required!')
                return render(request, 'accounts/faculty_signup.html')
            
            # Validate password length
            if len(password) < 6:
                messages.error(request, 'Password must be at least 6 characters long!')
                return render(request, 'accounts/faculty_signup.html')
            
            # Validate name
            if len(name) < 3:
                messages.error(request, 'Name must be at least 3 characters long!')
                return render(request, 'accounts/faculty_signup.html')
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                messages.error(request, 'Invalid email format!')
                return render(request, 'accounts/faculty_signup.html')
            
            # Validate phone number
            phone_pattern = r'^[0-9]{10}$'
            if not re.match(phone_pattern, phone):
                messages.error(request, 'Phone number must be exactly 10 digits!')
                return render(request, 'accounts/faculty_signup.html')
            
            # Check for duplicate username
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" already exists!')
                return render(request, 'accounts/faculty_signup.html')
            
            # Check for duplicate faculty_id
            if Faculty.objects.filter(faculty_id=faculty_id).exists():
                messages.error(request, f'Faculty ID "{faculty_id}" already exists!')
                return render(request, 'accounts/faculty_signup.html')
            
            # Check for duplicate email
            if Faculty.objects.filter(email=email).exists():
                messages.error(request, f'Email "{email}" is already registered!')
                return render(request, 'accounts/faculty_signup.html')
            
            # Check for duplicate phone
            if Faculty.objects.filter(phone=phone).exists():
                messages.error(request, f'Phone number "{phone}" is already registered!')
                return render(request, 'accounts/faculty_signup.html')
            
            # Create user account
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                )
                user.is_staff = False
                user.save()
            except Exception as user_error:
                messages.error(request, f'Error creating user account: {str(user_error)}')
                return render(request, 'accounts/faculty_signup.html')
            
            # Create faculty profile
            try:
                Faculty.objects.create(
                    user=user,
                    faculty_id=faculty_id,
                    name=name,
                    email=email,
                    department=department,
                    phone=phone,
                    is_active=True
                )
                
                messages.success(request, f'✓ Registration successful! You can now login with username: {username}')
                return redirect('login')
                
            except Exception as faculty_error:
                # If faculty creation fails, delete the user
                user.delete()
                messages.error(request, f'Error creating faculty profile: {str(faculty_error)}')
                return render(request, 'accounts/faculty_signup.html')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'accounts/faculty_signup.html')
    
    return render(request, 'accounts/faculty_signup.html')


def home(request):
    """Home page"""
    return render(request, 'home.html')


@faculty_required
def faculty_dashboard(request):
    """Faculty dashboard for monitoring attendance"""
    today = timezone.now().date()
    
    # Today's statistics
    total_students = Student.objects.filter(is_active=True).count()
    today_attendance = Attendance.objects.filter(date=today)
    present_today = today_attendance.count()
    absent_today = total_students - present_today
    late_arrivals = today_attendance.filter(is_late=True).count()
    
    # Recent attendance records
    recent_records = Attendance.objects.select_related('student').all()[:20]
    
    # Faculty info
    faculty = request.user.faculty_profile
    
    context = {
        'faculty': faculty,
        'total_students': total_students,
        'present_today': present_today,
        'absent_today': absent_today,
        'late_arrivals': late_arrivals,
        'recent_records': recent_records,
        'today': today
    }
    
    return render(request, 'accounts/faculty_dashboard.html', context)


@admin_required
def student_list(request):
    """List all students - Admin only"""
    students = Student.objects.filter(is_active=True).order_by('roll_number')
    context = {'students': students}
    return render(request, 'accounts/student_list.html', context)

@admin_required
@ensure_csrf_cookie
def student_register(request):
    """Register new student with face encoding - Admin only"""
    return render(request, 'accounts/student_register.html')

@admin_required
@csrf_exempt
def save_student(request):
    """Save student data with face encoding - Admin only"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            name = data.get('name', '').strip()
            roll_number = data.get('roll_number', '').strip()
            email = data.get('email', '').strip().lower()
            department = data.get('department', 'Computer Science')
            phone = data.get('phone', '').strip()
            image_data = data.get('image', '').split(',')[1] if data.get('image') else None
            
            # Validate required fields
            if not all([name, roll_number, email, image_data]):
                return JsonResponse({
                    'success': False,
                    'message': 'All required fields must be filled!'
                })
            
            # Validate name (at least 3 characters, letters and spaces only)
            if len(name) < 3:
                return JsonResponse({
                    'success': False,
                    'message': 'Name must be at least 3 characters long!'
                })
            
            if not re.match(r'^[a-zA-Z\s]+$', name):
                return JsonResponse({
                    'success': False,
                    'message': 'Name should contain only letters and spaces!'
                })
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid email format!'
                })
            
            # Validate phone number (if provided)
            if phone:
                phone_pattern = r'^[0-9]{10}$'
                if not re.match(phone_pattern, phone):
                    return JsonResponse({
                        'success': False,
                        'message': 'Phone number must be exactly 10 digits!'
                    })
            
            # Check for duplicate roll number
            if Student.objects.filter(roll_number=roll_number).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Roll number "{roll_number}" already exists!'
                })
            
            # Check if username (roll_number) already exists in User table
            if User.objects.filter(username=roll_number).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Roll number "{roll_number}" is already registered as a user!'
                })
            
            # Check for duplicate email
            if Student.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Email "{email}" is already registered!'
                })
            
            # Check for duplicate phone (if provided)
            if phone and Student.objects.filter(phone=phone).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Phone number "{phone}" is already registered!'
                })
            
            # Check for duplicate name (case-insensitive)
            if Student.objects.filter(name__iexact=name).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'A student with name "{name}" is already registered!'
                })
            
            # Decode and process image
            decoded = base64.b64decode(image_data)
            np_arr = np.frombuffer(decoded, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            # Get face encoding
            encoding = get_face_encoding(img)
            
            if encoding is None:
                return JsonResponse({
                    'success': False,
                    'message': 'No face detected! Please capture a clear photo with proper lighting.'
                })
            
            # Create student
            student = Student.objects.create(
                name=name,
                roll_number=roll_number,
                email=email,
                department=department,
                phone=phone if phone else None
            )
            
            # Create user account for student login
            # Username: roll_number, Password: roll_number (default)
            try:
                user = User.objects.create_user(
                    username=roll_number,
                    email=email,
                    password=roll_number,  # Default password same as roll number
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                )
                user.is_staff = False  # Students are not admin
                user.save()
            except Exception as user_error:
                # If user creation fails, delete the student to maintain consistency
                student.delete()
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating user account: {str(user_error)}'
                })
            
            # Save face encoding
            student.set_encoding(encoding)
            student.save()
            
            return JsonResponse({
                'success': True,
                'message': f'✓ Student {name} registered successfully! Login credentials - Username: {roll_number}, Password: {roll_number}',
                'student_id': student.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@admin_required
def student_detail(request, pk):
    """View student details - Admin only"""
    student = get_object_or_404(Student, pk=pk)
    attendances = student.attendances.all()[:10]
    
    context = {
        'student': student,
        'attendances': attendances
    }
    return render(request, 'accounts/student_detail.html', context)

@admin_required
def student_delete(request, pk):
    """Delete (deactivate) student - Admin only"""
    student = get_object_or_404(Student, pk=pk)
    student.is_active = False
    student.save()
    messages.success(request, f'Student {student.name} has been deactivated.')
    return redirect('student_list')
