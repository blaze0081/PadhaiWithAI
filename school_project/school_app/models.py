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
        user.is_district_user = False
        user.is_block_user = False
        user.is_school_user = True
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
    is_district_user = models.BooleanField(default=False)
    is_block_user = models.BooleanField(default=False)
    is_school_user = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email

class District(models.Model):
    name_english = models.CharField(max_length=100)
    name_hindi = models.CharField(max_length=100)

    def __str__(self):
        return self.name_english

class Block(models.Model):
    name_english = models.CharField(max_length=100)
    name_hindi = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='block_admin', null=True, blank=True )
   # created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_english
class School(models.Model):
    name = models.CharField(max_length=100)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='administered_school')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_schools', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    #block = models.ForeignKey(Block, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="block_schools")
    #block_name= models.CharField(max_length=50, null=True, blank=True)
    nic_code= models.CharField(max_length=20, null=True, blank=True)
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
    max_marks = models.FloatField()
    def __str__(self):
        return self.test_name
    
# Marks Model
class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    marks = models.DecimalField(max_digits=5, decimal_places=2)  # Example: 100.00
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'test')  # Prevent duplicate marks for a student in the same test

    def __str__(self):
        return f"{self.student.name} - {self.test.test_name}: {self.marks}"
    
    #11012025
# Attendance Model
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    is_present = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'date')
