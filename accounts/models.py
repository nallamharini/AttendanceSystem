from django.db import models
import pickle

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    face_encoding = models.BinaryField()

    def set_encoding(self, encoding):
        self.face_encoding = pickle.dumps(encoding)

    def get_encoding(self):
        return pickle.loads(self.face_encoding)

    def __str__(self):
        return self.name
