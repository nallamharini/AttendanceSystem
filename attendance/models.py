from django.db import models
from accounts.models import Student

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('ENTRY', 'Entry'),
        ('EXIT', 'Exit'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    entry_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    is_early_exit = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ENTRY')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.date}"
    
    class Meta:
        ordering = ['-date', '-entry_time']
        unique_together = ['student', 'date']


class Holiday(models.Model):
    """Model to store public holidays and campus closed days"""
    name = models.CharField(max_length=100, help_text="Holiday name (e.g., Republic Day)")
    date = models.DateField(unique=True, help_text="Date of the holiday")
    description = models.TextField(blank=True, null=True, help_text="Additional details about the holiday")
    is_active = models.BooleanField(default=True, help_text="Whether this holiday is active")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    class Meta:
        ordering = ['date']
        
    @staticmethod
    def is_holiday(date):
        """Check if a given date is a holiday"""
        return Holiday.objects.filter(date=date, is_active=True).exists()
