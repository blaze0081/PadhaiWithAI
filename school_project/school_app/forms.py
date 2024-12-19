from django import forms
from .models import Student, Marks, School

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'grade']

class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ['student', 'subject', 'marks']

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name', 'id']