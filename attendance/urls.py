from django.urls import path
from . import views

urlpatterns = [
    path('mark-page/', views.mark_attendance_view, name='mark_attendance_view'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('records/', views.attendance_records, name='attendance_records'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('analytics/', views.student_analytics, name='student_analytics'),
    path('holidays/', views.holiday_list, name='holiday_list'),
    path('holidays/add/', views.add_holiday, name='add_holiday'),
    path('holidays/<int:pk>/delete/', views.delete_holiday, name='delete_holiday'),
    path('calendar/', views.calendar_view, name='calendar_view'),
]
