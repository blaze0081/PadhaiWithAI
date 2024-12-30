from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, User
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_system_admin', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_system_admin = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    
    # Add related_name to resolve conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email

class School(models.Model):
    name = models.CharField(max_length=100)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='administered_school')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_schools', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Student(models.Model):
    CLASS_CHOICES = [
        ('1', 'Class 1'),
        ('2', 'Class 2'),
        ('3', 'Class 3'),
        ('4', 'Class 4'),
        ('5', 'Class 5'),
        ('6', 'Class 6'),
        ('7', 'Class 7'),
        ('8', 'Class 8'),
        ('9', 'Class 9'),
        ('10', 'Class 10'),
        ('11', 'Class 11'),
        ('12', 'Class 12'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(
        max_length=2,
        choices=CLASS_CHOICES,
        verbose_name='Class'
    )

    def __str__(self):
        return self.name  # Ensure this returns the student's name
    

    
class Book(models.Model):
    name = models.CharField(max_length=100)
    language = models.CharField(max_length=20)
    json_file_path = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.language})"
    
class Test(models.Model):
    test_number = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=255)
    subject_name = models.CharField(max_length=255)
    pdf_file_questions = models.FileField(upload_to='test_pdfs/questions/', null=True, blank=True)  # Uploads question PDFs
    pdf_file_answers = models.FileField(upload_to='test_pdfs/answers/', null=True, blank=True)  # Uploads answer PDFs
    is_active = models.BooleanField(default=False)  # Field to activate/deactivate the test
    test_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)  # Reference to the collector who created the test
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.test_name
    
class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # test = models.ForeignKey(Test, on_delete=models.CASCADE)
    test_number = models.CharField(max_length=50)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.test_number}: {self.marks}"

