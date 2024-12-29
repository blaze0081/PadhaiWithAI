from django import forms
from .models import Student, Marks, School, CustomUser, Test

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'class_name']

class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ['student', 'test_number', 'marks']

    # Optional: you can specify custom labels for better clarity if needed
    student = forms.ModelChoiceField(queryset=Student.objects.all(), label="Select Student")


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['name']

class SchoolAdminRegistrationForm(forms.ModelForm):
    admin_email = forms.EmailField()
    admin_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = School
        fields = ['name', 'admin_email', 'admin_password']

    def save(self, commit=True, created_by=None):
        school = super().save(commit=False)
        
        # Create school admin user
        admin_user = CustomUser.objects.create_user(
            email=self.cleaned_data['admin_email'],
            password=self.cleaned_data['admin_password'],
        )
        
        school.admin = admin_user
        school.created_by = created_by
        
        if commit:
            school.save()
        return school

class TestForm(forms.ModelForm):
    test_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',  # This enables the HTML5 date picker
            'class': 'form-control',  # Bootstrap class for styling (optional)
        }),
    )

    class Meta:
        model = Test
        fields = ['test_name', 'subject_name', 'pdf_file', 'test_date']

    
