import base64
import numpy as np
import cv2
import json
from django.http import JsonResponse
from django.utils import timezone
from datetime import time
from .utils import get_face_encoding
from accounts.models import Student
from .models import Attendance

LATE_THRESHOLD = time(9, 15)

def mark_attendance(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data['image'].split(',')[1]

        decoded = base64.b64decode(image_data)
        np_arr = np.frombuffer(decoded, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        encoding = get_face_encoding(img)

        students = list(Student.objects.all())
        for student in students:
            if encoding is not None:
                today = timezone.now().date()
                now_time = timezone.now().time()

                record, created = Attendance.objects.get_or_create(
                    student=student,
                    date=today
                )

                if created:
                    record.entry_time = now_time
                    if now_time > LATE_THRESHOLD:
                        record.is_late = True
                    message = "Entry Marked"
                else:
                    record.exit_time = now_time
                    message = "Exit Marked"

                record.save()
                return JsonResponse({"message": message})

        return JsonResponse({"message": "Face Not Recognized"})
