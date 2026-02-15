from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/register/', views.student_signup, name='student_signup'),
    path('faculty/signup/', views.faculty_signup_view, name='faculty_signup'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/register/', views.student_register, name='student_register'),
    path('students/save/', views.save_student, name='save_student'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
]
