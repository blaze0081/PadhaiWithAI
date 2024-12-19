from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import School, Student, Marks
from .forms import StudentForm, MarksForm, SchoolForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Check if user has a school
            if School.objects.filter(admin=user).exists():
                return redirect('dashboard')
            # else:
            #     return redirect('school_add')
        messages.error(request, 'Invalid credentials')
        
    return render(request, 'school_app/login.html')

@login_required
def dashboard(request):
    try:
        school = School.objects.get(admin=request.user)
        context = {
            'school': school,
            'student_count': Student.objects.filter(school=school).count(),
        }
    except School.DoesNotExist:
        messages.error(request, "No school found for the current user.")
        return redirect('login')  # Redirect to login page instead

    return render(request, 'school_app/dashboard.html', context)

@login_required
def student_list(request):
    school = School.objects.get(admin=request.user)
    students = Student.objects.filter(school=school)
    return render(request, 'school_app/student_list.html', {'students': students})

@login_required
def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = School.objects.get(admin=request.user)
            student.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'school_app/student_add.html', {'form': form})

@login_required
def marks_add(request):
    if request.method == 'POST':
        form = MarksForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('marks_list')
    else:
        school = School.objects.get(admin=request.user)
        form = MarksForm()
        form.fields['student'].queryset = Student.objects.filter(school=school)
    return render(request, 'school_app/marks_add.html', {'form': form})

@login_required
def marks_list(request):
    school = School.objects.get(admin=request.user)
    marks = Marks.objects.filter(student__school=school)
    return render(request, 'school_app/marks_list.html', {'marks': marks})

@login_required
def school_add(request):
    # Check if user already has a school
    if School.objects.filter(admin=request.user).exists():
        messages.warning(request, "You already have a school registered.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        if form.is_valid():
            school = form.save(commit=False)
            school.admin = request.user
            school.save()
            messages.success(request, "School created successfully!")
            return redirect('dashboard')
    else:
        form = SchoolForm()
    
    return render(request, 'school_app/school_add.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')