from django.shortcuts import render

def home(request):
    return render(request, 'mark_attendance.html')
