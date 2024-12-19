from django.db import models
from django.contrib.auth.models import User

class School(models.Model):
    name = models.CharField(max_length=100)
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    grade = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.name} - {self.roll_number}"

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.subject}: {self.marks}"
