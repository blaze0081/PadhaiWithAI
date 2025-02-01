from django import forms
from .models import Student, Marks, School, CustomUser, Test
from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Login email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    captcha = CaptchaField()

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'class_name']

class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        #fields = ['student', 'test_number', 'marks']
        fields = ['student','marks','test']
    # Optional: you can specify custom labels for better clarity if needed
    #student = forms.ModelChoiceField(queryset=Student.objects.all(), label="Select Student")


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
     # Test Name Field
    test_name = forms.CharField(
        required=True,
        max_length=100,  # Set max_length or customize as needed
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Bootstrap class for styling
            'placeholder': 'Enter Test Name',  # Placeholder text for guidance
            'style': 'font-size: 1.1em; padding: 10px; text-transform: capitalize;',  # Custom style
        })
    )

    # Subject Name Field
    subject_name = forms.CharField(
        required=True,
        max_length=100,  # Set max_length or customize as needed
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Bootstrap class for styling
            'placeholder': 'Enter Subject Name',  # Placeholder text for guidance
            'style': 'font-size: 1.1em; padding: 10px; text-transform: capitalize;',  # Custom style
        })
    )
    test_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',  # This enables the HTML5 date picker
            'class': 'form-control',  # Bootstrap class for styling (optional)
            'placeholder': 'Select Test date',  # Placeholder text for guidance
        }),
    )
    pdf_file_questions = forms.FileField(
        required=True,  # Optional field (doesn't need to be filled)
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',  # Apply Bootstrap class for styling
            'accept': '.pdf',  # Limit to PDF file selection (optional)
            'placeholder': 'Select Questions file',  # Placeholder text for guidance
        })
    )
    pdf_file_answers = forms.FileField(
        required=True,  # Optional field (doesn't need to be filled)
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',  # Apply Bootstrap class for styling
            'accept': '.pdf',  # Limit to PDF file selection (optional)
            'placeholder': 'Select Answer file',  # Placeholder text for guidance
        })
    )
    max_marks = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max marks of the test'}),
        label="Max Marks"
    )


    class Meta:
        model = Test
        fields = ['test_name', 'subject_name', 'pdf_file_questions', 'pdf_file_answers',  'test_date','max_marks']
 
class ExcelFileUploadForm(forms.Form):
       excel_file = forms.FileField()  # Ensure the field is named 'excel_file'
    
