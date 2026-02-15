import base64
import numpy as np
import cv2
import json
import csv
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from datetime import time, datetime, timedelta
from .utils import get_face_encoding, compare_faces
from accounts.models import Student
from accounts.decorators import admin_required, student_required
from .models import Attendance, Holiday

# Configuration
LATE_THRESHOLD = time(9, 30)  # 9:30 AM - Late threshold
EARLY_EXIT_THRESHOLD = time(16, 0)  # 4:00 PM - Early exit threshold

@student_required
@ensure_csrf_cookie
def mark_attendance_view(request):
    """Student attendance marking page"""
    today = timezone.now().date()
    is_holiday = Holiday.is_holiday(today)
    holiday_info = None
    
    if is_holiday:
        holiday_info = Holiday.objects.filter(date=today, is_active=True).first()
    
    context = {
        'is_holiday': is_holiday,
        'holiday_info': holiday_info,
        'today': today
    }
    
    return render(request, 'attendance/mark_attendance.html', context)

@csrf_exempt
def mark_attendance(request):
    """API endpoint for marking attendance via face recognition"""
    if request.method == "POST":
        try:
            # Check if today is a holiday
            today = timezone.now().date()
            if Holiday.is_holiday(today):
                holiday = Holiday.objects.filter(date=today, is_active=True).first()
                return JsonResponse({
                    "success": False,
                    "message": f"🎉 Today is {holiday.name}! No attendance required. Enjoy the holiday!"
                })
            
            data = json.loads(request.body)
            image_data = data['image'].split(',')[1]
            
            # Decode image
            decoded = base64.b64decode(image_data)
            np_arr = np.frombuffer(decoded, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            # Get face encoding from captured image
            captured_encoding = get_face_encoding(img)
            
            if captured_encoding is None:
                return JsonResponse({
                    "success": False,
                    "message": "No face detected! Please position your face properly."
                })
            
            # Get all active students
            students = Student.objects.filter(is_active=True, face_encoding__isnull=False)
            
            matched_student = None
            for student in students:
                stored_encoding = student.get_encoding()
                if stored_encoding is not None:
                    if compare_faces(captured_encoding, stored_encoding):
                        matched_student = student
                        break
            
            if matched_student:
                today = timezone.now().date()
                now_time = timezone.now().time()
                
                # Check if attendance record exists for today
                record, created = Attendance.objects.get_or_create(
                    student=matched_student,
                    date=today
                )
                
                if created or record.entry_time is None:
                    # Mark entry
                    record.entry_time = now_time
                    record.is_late = now_time > LATE_THRESHOLD
                    record.status = 'ENTRY'
                    message = f"✓ Entry Marked for {matched_student.name}"
                    if record.is_late:
                        message += " (Late Arrival)"
                else:
                    # Mark exit
                    record.exit_time = now_time
                    record.is_early_exit = now_time < EARLY_EXIT_THRESHOLD
                    record.status = 'EXIT'
                    message = f"✓ Exit Marked for {matched_student.name}"
                    if record.is_early_exit:
                        message += " (Early Exit)"
                
                record.save()
                
                return JsonResponse({
                    "success": True,
                    "message": message,
                    "student": matched_student.name,
                    "roll_number": matched_student.roll_number,
                    "time": now_time.strftime("%I:%M %p"),
                    "status": record.status
                })
            else:
                return JsonResponse({
                    "success": False,
                    "message": "Face Not Recognized! Please register first."
                })
                
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": f"Error: {str(e)}"
            })
    
    return JsonResponse({"success": False, "message": "Invalid request method"})

@admin_required
def admin_dashboard(request):
    """Admin dashboard with analytics"""
    today = timezone.now().date()
    
    # Today's statistics
    total_students = Student.objects.filter(is_active=True).count()
    today_attendance = Attendance.objects.filter(date=today)
    present_today = today_attendance.count()
    absent_today = total_students - present_today
    late_arrivals = today_attendance.filter(is_late=True).count()
    
    # Recent attendance records
    recent_records = Attendance.objects.select_related('student').all()[:10]
    
    # Get weekly statistics
    week_ago = today - timedelta(days=7)
    weekly_attendance = Attendance.objects.filter(
        date__gte=week_ago,
        date__lte=today
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    context = {
        'total_students': total_students,
        'present_today': present_today,
        'absent_today': absent_today,
        'late_arrivals': late_arrivals,
        'recent_records': recent_records,
        'weekly_attendance': list(weekly_attendance),
        'today': today,
    }
    
    return render(request, 'attendance/admin_dashboard.html', context)

@admin_required
def attendance_records(request):
    """View all attendance records with filters"""
    records = Attendance.objects.select_related('student').all()
    
    # Filters
    date_filter = request.GET.get('date')
    student_filter = request.GET.get('student')
    status_filter = request.GET.get('status')
    
    if date_filter:
        records = records.filter(date=date_filter)
    if student_filter:
        records = records.filter(student__roll_number__icontains=student_filter)
    if status_filter:
        if status_filter == 'late':
            records = records.filter(is_late=True)
        elif status_filter == 'early_exit':
            records = records.filter(is_early_exit=True)
    
    students = Student.objects.filter(is_active=True)
    
    context = {
        'records': records,
        'students': students,
        'date_filter': date_filter or '',
        'student_filter': student_filter or '',
        'status_filter': status_filter or '',
    }
    
    return render(request, 'attendance/records.html', context)

@admin_required
def export_csv(request):
    """Export attendance records to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Roll Number', 'Date', 'Entry Time', 'Exit Time', 'Late', 'Early Exit', 'Status'])
    
    # Filters
    records = Attendance.objects.select_related('student').all()
    date_filter = request.GET.get('date')
    student_filter = request.GET.get('student')
    
    if date_filter:
        records = records.filter(date=date_filter)
    if student_filter:
        records = records.filter(student__roll_number__icontains=student_filter)
    
    for record in records:
        writer.writerow([
            record.student.name,
            record.student.roll_number,
            record.date,
            record.entry_time.strftime("%I:%M %p") if record.entry_time else 'N/A',
            record.exit_time.strftime("%I:%M %p") if record.exit_time else 'N/A',
            'Yes' if record.is_late else 'No',
            'Yes' if record.is_early_exit else 'No',
            record.status
        ])
    
    return response

@admin_required
def student_analytics(request):
    """Individual student attendance analytics"""
    students = Student.objects.filter(is_active=True)
    student_stats = []
    
    for student in students:
        total_days = Attendance.objects.filter(student=student).count()
        late_count = Attendance.objects.filter(student=student, is_late=True).count()
        early_exit_count = Attendance.objects.filter(student=student, is_early_exit=True).count()
        
        student_stats.append({
            'student': student,
            'total_days': total_days,
            'late_count': late_count,
            'early_exit_count': early_exit_count,
            'attendance_percentage': round((total_days / 30) * 100, 2) if total_days > 0 else 0
        })
    
    context = {
        'student_stats': student_stats
    }
    
    return render(request, 'attendance/analytics.html', context)


# ============== Holiday Management Views ==============

@admin_required
def holiday_list(request):
    """View and manage holidays - Admin only"""
    holidays = Holiday.objects.all().order_by('-date')
    upcoming_holidays = Holiday.objects.filter(date__gte=timezone.now().date(), is_active=True).order_by('date')
    past_holidays = Holiday.objects.filter(date__lt=timezone.now().date()).order_by('-date')[:10]
    
    context = {
        'holidays': holidays,
        'upcoming_holidays': upcoming_holidays,
        'past_holidays': past_holidays
    }
    
    return render(request, 'attendance/holidays.html', context)


@admin_required
@csrf_exempt
def add_holiday(request):
    """Add a new holiday - Admin only"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            date_str = data.get('date', '').strip()
            description = data.get('description', '').strip()
            
            if not all([name, date_str]):
                return JsonResponse({
                    'success': False,
                    'message': 'Name and date are required!'
                })
            
            # Parse date
            from datetime import datetime as dt
            holiday_date = dt.strptime(date_str, '%Y-%m-%d').date()
            
            # Check if holiday already exists
            if Holiday.objects.filter(date=holiday_date).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'A holiday already exists on {holiday_date}!'
                })
            
            # Create holiday
            holiday = Holiday.objects.create(
                name=name,
                date=holiday_date,
                description=description
            )
            
            return JsonResponse({
                'success': True,
                'message': f'✓ Holiday "{name}" added successfully!',
                'holiday_id': holiday.id
            })
            
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid date format! Use YYYY-MM-DD'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@admin_required
def delete_holiday(request, pk):
    """Delete a holiday - Admin only"""
    holiday = get_object_or_404(Holiday, pk=pk)
    holiday_name = holiday.name
    holiday.delete()
    messages.success(request, f'Holiday "{holiday_name}" has been deleted.')
    return redirect('holiday_list')


@admin_required
def calendar_view(request):
    """Calendar view showing attendance and holidays"""
    today = timezone.now().date()
    
    # Get current month's data
    year = request.GET.get('year', today.year)
    month = request.GET.get('month', today.month)
    
    # Get holidays for the month
    holidays_queryset = Holiday.objects.filter(
        date__year=year,
        date__month=month,
        is_active=True
    )
    
    # Serialize holidays for JavaScript
    holidays_json = json.dumps([{
        'fields': {
            'name': h.name,
            'date': h.date.strftime('%Y-%m-%d'),
            'description': h.description
        }
    } for h in holidays_queryset])
    
    # Get attendance data for the month
    attendance_data = Attendance.objects.filter(
        date__year=year,
        date__month=month
    ).values('date').annotate(
        total=Count('id'),
        late=Count('id', filter=Q(is_late=True))
    )
    
    # Serialize attendance data for JavaScript
    attendance_json = json.dumps([{
        'date': item['date'].strftime('%Y-%m-%d'),
        'total': item['total'],
        'late': item['late']
    } for item in attendance_data])
    
    context = {
        'today': today,
        'year': int(year),
        'month': int(month),
        'holidays': holidays_queryset,  # For display in sidebar
        'holidays_json': holidays_json,  # For JavaScript calendar
        'attendance_data': attendance_json  # For JavaScript calendar
    }
    
    return render(request, 'attendance/calendar.html', context)
