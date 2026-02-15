from django.contrib.auth.decorators import login_required, user_passes_test
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """Decorator to restrict access to faculty/admin users only (Faculty has full admin access)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        # Allow both faculty and admin users
        if not (request.user.is_staff or hasattr(request.user, 'faculty_profile')):
            messages.error(request, 'Access Denied! Faculty privileges required.')
            return redirect('mark_attendance_view')
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    """Decorator to restrict access to authenticated students"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def faculty_required(view_func):
    """Decorator to restrict access to faculty users only (Faculty has full admin access)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        # Allow both faculty and admin users (staff)
        if not (hasattr(request.user, 'faculty_profile') or request.user.is_staff):
            messages.error(request, 'Access Denied! Faculty privileges required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

def faculty_or_admin_required(view_func):
    """Decorator to allow access to both faculty and admin (same as admin_required)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        # Allow if admin or has faculty profile
        if not (request.user.is_staff or hasattr(request.user, 'faculty_profile')):
            messages.error(request, 'Access Denied! Faculty or Admin privileges required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper
