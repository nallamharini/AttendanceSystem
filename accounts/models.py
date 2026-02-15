from django.db import models
from django.contrib.auth.models import User
import pickle

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    department = models.CharField(max_length=100, default='Computer Science')
    phone = models.CharField(max_length=15, blank=True, null=True)
    face_encoding = models.BinaryField(blank=True, null=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_encoding(self, encoding):
        self.face_encoding = pickle.dumps(encoding)

    def get_encoding(self):
        if self.face_encoding:
            return pickle.loads(self.face_encoding)
        return None

    def __str__(self):
        return f"{self.name} ({self.roll_number})"

    class Meta:
        ordering = ['roll_number']


class Faculty(models.Model):
    """Faculty/Teacher model for monitoring attendance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.faculty_id})"

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Faculty'
