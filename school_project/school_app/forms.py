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
    class Meta:
        model = Test
        fields = ['test_name', 'subject_name', 'pdf_file', 'test_date']  # Added 'test_date'

    # Optional: You can customize the form field's appearance if necessary
    test_date = forms.DateField(
        required=False,  # Makes the test_date field optional in the form
        widget=forms.SelectDateWidget(years=range(2000, 2101))  # This gives a date picker for test_date
    )
    
