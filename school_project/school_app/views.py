from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import School, Student, Marks
from .forms import StudentForm, MarksForm, SchoolForm, SchoolAdminRegistrationForm, TestForm, Test
from django.db.models import Count 
from .math_utils import async_solve_math_problem, async_generate_similar_questions
import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min
from django.http import JsonResponse
from .models import Student, Marks
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .models import Test, Marks, Student, School
from decimal import InvalidOperation
from .models import CustomUser, School,Attendance
from .forms import ExcelFileUploadForm 
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone

@login_required
def test_wise_average_marks(request):
    from django.db.models import Avg, F, ExpressionWrapper, FloatField

    # Assuming max_marks is a field in the Test model for maximum marks of the test
     #F('avg_marks') * 100 / F('max_marks'),
    data = (
        Test.objects.annotate(
            avg_marks=Avg('marks__marks'),
            percentage=ExpressionWrapper(
                F('avg_marks') * 100 / 45,               
                output_field=FloatField()
            )
        )
        .values('test_name', 'avg_marks', 'percentage')
        .order_by('-percentage')
    )

    context = {'data': data}
    return render(request, 'test_wise_average.html', context)

@login_required
def submit_attendance(request):
    if request.user.is_school_admin:
        students = request.user.school.students.all()
        if request.method == 'POST':
            selected_students = request.POST.getlist('absent_students')
            for student in students:
                is_present = str(student.id) not in selected_students
                Attendance.objects.update_or_create(
                    student=student,
                    date=timezone.now().date(),
                    defaults={'is_present': is_present}
                )
            return redirect('attendance_summary')

        context = {'students': students}
        return render(request, 'attendance/submit.html', context)
    return redirect('home')
@login_required
def attendance_summary(request):
    if request.user.is_system_admin:
        total_schools = School.objects.count()
        schools_logged_in = CustomUser.objects.filter(
            last_login__date=timezone.now().date(),
            is_school_admin=True
        ).count()

        attendance_data = Attendance.objects.filter(
            date=timezone.now()
        ).values('student__school__name').annotate(
            present_count=Count('id', filter=Q(is_present=True)),
            total_students=Count('id'),
        )

        context = {
            'attendance_data': attendance_data,
            'schools_logged_in': schools_logged_in,
            'total_schools': total_schools,
        }
        return render(request, 'attendance/summary.html', context)
    return redirect('home')
#11/01/2025
@login_required
def update_block_name_from_excel(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        
        try:
            # Read the Excel file using pandas
            df = pd.read_excel(excel_file)

            updates = []
            # Iterate over rows in the DataFrame
            for _, row in df.iterrows():
                school_name = row['School Name']
                block_name = row['Block Name']

                try:
                    # Find the school by name
                    school = School.objects.get(name=school_name)
                    school.Block_Name = block_name  # Update Block Name
                    school.save()  # Save the updated School object
                    updates.append(f'Updated {school_name}')
                except School.DoesNotExist:
                    updates.append(f'{school_name} not found')
            
            return JsonResponse({'updates': updates})

        except Exception as e:
            return JsonResponse({'error': f'Error processing file: {str(e)}'}, status=400)

    return render(request, 'update_block_name_form.html')

#10012025
@login_required
def get_active_users_count():
    sessions = Session.objects.filter(expire_date__gte=timezone.now())

    active_users_count = 0

    for session in sessions:
        session_data = session.get_decoded()

        if 'user_id' in session_data:
            user_id = session_data['user_id']           
            try:
                User.objects.get(id=user_id)
                active_users_count += 1
            except User.DoesNotExist:
                continue

    return active_users_count
#08/01/2025
#1
@login_required
def schools_without_students(request):
    schools = School.objects.annotate(student_count=Count('student')).filter(student_count=0)
    context = {'schools': schools}
    return render(request, 'schools_without_students.html', context)
#2
@login_required
def inactive_schools(request):
    schools = School.objects.filter(
        admin__last_login__isnull=True
    ).values('id','name', 'admin__email')
    context = {'schools': schools}
    return render(request, 'inactive_schools.html', context)

#3
@login_required
def schools_with_test_counts(request):
    schools = School.objects.annotate(test_count=Count('student__marks__test')).order_by('-test_count')
    context = {'schools': schools}
    return render(request, 'schools_with_test_counts.html', context)
#4
@login_required
def schools_without_tests(request):
    schools = School.objects.annotate(test_count=Count('student__marks__test')).filter(test_count=0)
    context = {'schools': schools}
    return render(request, 'schools_without_tests.html', context)
#5
@login_required
def schools_with_student_counts(request):
    schools = School.objects.annotate(student_count=Count('student')).order_by('-student_count')
    context = {'schools': schools}
    return render(request, 'schools_with_student_counts.html', context)

@login_required
def report_dashboard(request):
    return render(request,'report_dashboard.html')

@login_required
def school_report(request):
    # 1. Schools without student entries
    schools_without_students = School.objects.annotate(student_count=Count('student')).filter(student_count=0)
    
    # 2. Schools that haven’t logged in (Assuming each school has a User associated)
    
    #inactive_schools = CustomUser.objects.filter(last_login__isnull=True, groups__name='School')
    inactive_schools = CustomUser.objects.filter(
          # Users linked to a School
        last_login__isnull=True
    )
    inactive_schools = School.objects.filter(
        admin__last_login__isnull=True
    ).values('name', 'admin__email')
    
    # 3. Count of test entries per school
    schools_with_test_counts = School.objects.annotate(test_count=Count('student__marks__test')).order_by('-test_count')
    
    # 4. Schools without test entries
    schools_without_tests = School.objects.annotate(test_count=Count('student__marks__test')).filter(test_count=0)
    
    # 5. Schools with student count
    schools_with_student_counts = School.objects.annotate(student_count=Count('student')).order_by('-student_count')
    
    context = {
        'schools_without_students': schools_without_students,
        'inactive_schools': inactive_schools,
        'schools_with_test_counts': schools_with_test_counts,
        'schools_without_tests': schools_without_tests,
        'schools_with_student_counts': schools_with_student_counts,
    }
    return render(request, 'school_report.html', context)
#02/01/2025
@login_required
def upload_student_data(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']        
        try:
            # Load the Excel file into a pandas DataFrame
            df = pd.read_excel(excel_file, engine='openpyxl')
            
            successfully_created = 0  # Counter for successfully created students
            roll_number_errors = []  # Store errors related to duplicate roll numbers
            
            for index, row in df.iterrows():
                name = row['name']
                roll_number = row['roll_number']
                class_name = row['class_name']
                #school_name = row['school_name']
                school_name =""
                # Check if roll_number is unique
                if Student.objects.filter(roll_number=roll_number).exists():
                    roll_number_errors.append(f"Roll number {roll_number} already exists. Skipping this student.")
                    continue  # Skip to the next student if roll number is duplicate
                
                try:
                    # Get the School instance (assuming school_name exists in the DataFrame)
                    #school = School.objects.get(name=school_name)
                    
                    # Create the student object
                    student = Student.objects.create(
                        school_id=request.user.administered_school.id,
                        name=name,
                        roll_number=roll_number,
                        class_name=class_name
                    )
                    successfully_created += 1
                except Exception as e:    
                    messages.error(request, f"Error processing the file: {str(e)}")
                    continue
                #except School.DoesNotExist:
                #     messages.error(request, f"School '{school_name}' not found for student {name}.")
                #     continue  # Skip this student if the school doesn't exist
                
            # Display success or error messages
            if successfully_created > 0:
                messages.success(request, f"{successfully_created} students uploaded successfully.")
            if roll_number_errors:
                for error in roll_number_errors:
                    messages.warning(request, error)
                
            return redirect('student_list')  # Redirect to the page displaying student list or another view
            
        except Exception as e:
            messages.error(request, f"Error processing the file: {str(e)}")
            return redirect('upload_student_data')  # Redirect back to the upload form if any error occurs
    
    else:
        form = ExcelFileUploadForm()
    
    return render(request, 'upload_student_data.html', {'form': form})
# 01/01/2025  For test Analsis
# Forms

# Views
@login_required
def school_average_marks(request):
    from django.db.models import Avg
    data = School.objects.annotate(avg_marks=Avg('student__marks__marks')).order_by('-avg_marks')
    context = {'data': data}
    return render(request, 'school_average.html', context)

@login_required
def top_students(request):
    from django.db.models import F, ExpressionWrapper, FloatField
    number_of_toppers = int(request.GET.get('toppers', 5))

    # Calculate average marks and percentage
    data = (
        Marks.objects.values('student__name', 'student__school__name')
        .annotate(
            avg_marks=Avg('marks'),
            percentage= ExpressionWrapper(
                    Avg('marks') * 100 / 45.00,
                    output_field=FloatField()
                )
        )
        .order_by('-avg_marks')[:number_of_toppers]
    )

    context = {'data': data, 'number_of_toppers': number_of_toppers}
    return render(request, 'top_students.html', context)

@login_required
def weakest_students(request):
    number_of_weakest = int(request.GET.get('weakest', 5))
    from django.db.models import Avg
    data = Marks.objects.values('student__name', 'student__school__name').annotate(avg_marks=Avg('marks')).order_by('avg_marks')[:number_of_weakest]
    context = {'data': data, 'number_of_weakest': number_of_weakest}
    return render(request, 'weakest_students.html', context)

@login_required
def upload_school_users(request):
    if request.user.groups.filter(name='Collector').exists():      
    
        if request.method == 'POST' and request.FILES['excel_file']:
            excel_file = request.FILES['excel_file']
            successfully_created = 0  # Counter to track how many users are successfully created
            try:
                # Load Excel data into pandas DataFrame
                df = pd.read_excel(excel_file, engine='openpyxl')
                
                # Iterate through each row and create users
                for index, row in df.iterrows():
                    email = row['email']
                    username = row['username']
                    password = row['password']
                    is_admin =  0  # Default to False if not specified

                    try:
                        if CustomUser.objects.filter(email=email).exists():
                            user1 = CustomUser.objects.get(email=email)
                        else:
                            user1 = CustomUser.objects.create_user(
                                email=email,
                                username=username,
                                password=password,
                                is_system_admin=is_admin
                            )
                        user1.save()
                        admin_user = CustomUser.objects.get(email=email)
                    # Create or update the School instance
                        school = School.objects.create(
                                name=row['school_name'],
                                admin=admin_user,  # Assign the CustomUser instance to the admin field
                                created_by = request.user # Example if you want to set 'created_by' as the admin
                            )

                        school.save()
                        # Increment the successful creation counter
                        successfully_created += 1
                    except IntegrityError as e:
                        messages.error(request, f"Error creating user {email}: {e}")
                        continue  # Skip to the next user if error occurs
                    
                # Show a success message with the number of successfully created users
                if successfully_created > 0:
                    messages.success(request, f"{successfully_created} users uploaded and created successfully.")
                else:
                    messages.warning(request, "No users were created. Please check the file and try again.")
                return redirect('collector_dashboard')  # Replace with appropriate redirect path

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return redirect('upload_school_users')  # Redirect back to upload form if error occurs
        
        else:
            form = ExcelFileUploadForm()
        
        return render(request, 'upload_users.html', {'form': form})
    else:
        # If the user is not a collector, return an error message or redirect
        return HttpResponseForbidden("You are not authorized to access this page.")


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Important: Keeps the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password_change')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def is_system_admin(user):
    return user.is_authenticated and user.is_system_admin

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)

            # Check if the user is in the "Collector" group
            if user.groups.filter(name='Collector').exists():
                return redirect('collector_dashboard')

            # Redirect based on other roles
            if user.is_system_admin:
                return redirect('system_admin_dashboard')
            elif School.objects.filter(admin=user).exists():
                return redirect('dashboard')
            else:
                return redirect('school_add')

        messages.error(request, 'Invalid credentials')
    return render(request, 'school_app/login.html')

# Writtern by Sushil
@login_required
def collector_dashboard(request):
    # Fetch tests created by the collector
    if not request.user.groups.filter(name='Collector').exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    tests = Test.objects.all()
    # tests = Test.objects.filter(created_by=request.user)

    # Fetch all schools (You can add filters here if necessary)
    schools = School.objects.all()
    live_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    return render(request, 'school_app/collector_dashboard.html', {
        'tests': tests,
        'schools': schools,
        'total_schools': School.objects.count(),
        'total_students': Student.objects.count(),
        'total_tests': Test.objects.count(),
        'get_active_users': live_sessions.count()
    })

@login_required
def view_test_results(request, test_number):
    test = get_object_or_404(Test, test_number=test_number)
    results = Marks.objects.filter(test_id=test_number).select_related('student')

    # Get sorting parameters
    sort_by = request.GET.get('sort_by', 'student__name')  # Default sorting by student name
    order = request.GET.get('order', 'asc')  # Default order is ascending

    # Adjust the ordering
    if order == 'desc':
        sort_by = f"-{sort_by}"
    
    results = results.order_by(sort_by)

    context = {
        'test': test,
        'results': results,
        'current_sort_by': request.GET.get('sort_by', 'student__name'),
        'current_order': request.GET.get('order', 'asc'),
    }
    return render(request, 'school_app/test_results.html', context)

# Written by Sushil
@login_required
def add_test(request):
    if request.method == 'POST':
        form = TestForm(request.POST, request.FILES)
        if form.is_valid():
            test = form.save(commit=False)
            test.created_by = request.user  # Set the collector as the creator of the test
            test.save()
            messages.success(request, 'Test details have been successfully added!')
            return redirect('collector_dashboard')  # Redirect to collector dashboard or wherever appropriate
    else:
        form = TestForm()

    return render(request, 'school_app/add_test.html', {'form': form})

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Test

@login_required
def activate_test(request, test_id):
    # Change `id` to `test_number`, since that is your primary key
    test = get_object_or_404(Test, test_number=test_id)
    test.is_active = True
    test.save()
    messages.success(request, 'Test has been activated successfully!')
    # if request.user == test.created_by:  # Ensure only the creator can activate the test
    #     test.is_active = True
    #     test.save()

    #     messages.success(request, 'Test has been activated successfully!')
    # else:
    #     messages.error(request, 'You do not have permission to activate this test.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
@login_required
def deactivate_test(request, test_id):
    test = get_object_or_404(Test, test_number=test_id)
    test.is_active = False
    test.save()
    messages.success(request, 'Test has been activated successfully!')
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
@login_required
# def student_ranking(request):
#     # Student ranking
#      if not request.user.groups.filter(name='Collector').exists():
#         return HttpResponseForbidden("You are not authorized to access this page.")
#      rankings = Marks.objects.select_related('student', 'student__school').order_by('-marks')
#      return render(request, 'student_ranking.html', {'rankings': rankings})
def student_ranking(request):
    from django.db.models import F, ExpressionWrapper, FloatField

    # Check if the user has the 'Collector' group
    if not request.user.groups.filter(name='Collector').exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    #F('test__max_marks')
    # Retrieve rankings with percentage calculation
    rankings = (
        Marks.objects.select_related('student', 'student__school')
        .annotate(
            percentage=ExpressionWrapper(
                F('marks') * 100 / 45.00 ,
                output_field=FloatField()
            )
        )
        .order_by('-marks')
    )

    return render(request, 'student_ranking.html', {'rankings': rankings})
@login_required
def student_report(request):
   
    if not request.user.groups.filter(name='Collector').exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    total_students = Student.objects.count()
    return render(request, 'student_report.html', {'total_students': total_students})


@login_required
def edit_student(request, student_id):
    
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.name = request.POST['name']
        student.roll_number = request.POST['roll_number']
        student.save()
        return redirect('dashboard')
    return render(request, 'edit_student.html', {'student': student})


@login_required
def delete_student(request, student_id):
   
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('dashboard')

@login_required
def delete_student_mark(request, mark_id):
    mark = get_object_or_404(Marks, id=mark_id)
    mark.delete()
    return redirect('add_marks')

@login_required
def dashboard(request):
    if request.user.is_system_admin:
        return redirect('system_admin_dashboard')
    
    try:
        school = School.objects.get(admin=request.user)
        active_tests = Test.objects.filter(is_active=True)  # Fetch only active tests
        context = {
            'school': school,
            'student_count': Student.objects.filter(school=school).count(),
            'active_tests': active_tests,  # Pass active tests to the template
        }
    except School.DoesNotExist:
        messages.error(request, "No school found for the current user.")
        return redirect('login')

    return render(request, 'school_app/system_admin_dashboard.html', context)


@user_passes_test(is_system_admin)
def system_admin_dashboard(request):
    schools = School.objects.all().annotate(
        student_count=Count('student')
    )
    context = {
        'schools': schools,
        'total_schools': schools.count(),
        'total_students': Student.objects.count(),
    }
    return render(request, 'school_app/system_admin_dashboard.html', context)

@user_passes_test(is_system_admin)
def system_admin_school_list(request):
    schools = School.objects.all().annotate(
        student_count=Count('student')
    )
    return render(request, 'school_app/school_list.html', {'schools': schools})

@user_passes_test(is_system_admin)
def system_admin_school_add(request):
    if request.method == 'POST':
        form = SchoolAdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save(created_by=request.user)
            messages.success(request, "School and admin account created successfully!")
            return redirect('system_admin_school_list')
    else:
        form = SchoolAdminRegistrationForm()
    return render(request, 'school_app/school_add.html', {'form': form})

@user_passes_test(is_system_admin)
def system_admin_student_list(request, school_id=None):
    if school_id:
        students = Student.objects.filter(school_id=school_id)
    else:
        students = Student.objects.all()
    return render(request, 'school_app/student_list.html', {'students': students})

@user_passes_test(is_system_admin)
def system_admin_marks_list(request, school_id=None):
    if school_id:
        marks = Marks.objects.filter(student__school_id=school_id)
    else:
        marks = Marks.objects.all()
    return render(request, 'school_app/marks_list.html', {'marks': marks})

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
    marks = Marks.objects.filter(student__school=school).select_related('test', 'student')  # Use select_related to reduce queries
    return render(request, 'school_app/marks_list.html', {'marks': marks})


@login_required
def school_add(request):
    if request.user.is_system_admin:
        return redirect('system_admin_school_add')
        
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

from django.http import JsonResponse
from .models import Marks

@login_required
def update_marks(request, mark_id):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            new_marks = data.get('marks')

            mark = Marks.objects.get(id=mark_id)
            mark.marks = new_marks
            mark.save()

            return JsonResponse({'success': True, 'message': 'Marks updated successfully'})
        except Marks.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Mark record not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
from decimal import Decimal, InvalidOperation
@login_required
# Display and Edit Marks for a Selected Test
def test_marks_entry(request, test_id):
    test = get_object_or_404(Test, test_number=test_id)
    # Fetch the school associated with the logged-in user
    school = School.objects.get(admin=request.user)
    
    # Get all students from the logged-in user's school
    students = Student.objects.filter(school=school)

    if request.method == 'POST':
        # To store error messages
        error_messages = []
        
        for student in students:
            marks_value = request.POST.get(f'marks_{student.id}', '').strip()
            
            if marks_value:  # If marks are provided
                try:
                    # Validate numeric marks and convert them
                    marks_value = float(marks_value)
                    
                    # Try to get or create a Marks record for the student and test
                    mark, created = Marks.objects.update_or_create(
                        student=student,
                        test=test,
                        defaults={'marks': marks_value}
                    )
                    
                    # Optionally, you can check if the record was updated
                    if created:
                        print(f"Created new marks record for {student.name}")
                    else:
                        print(f"Updated marks record for {student.name}")

                except InvalidOperation:
                    error_messages.append(f"Invalid marks entered for {student.name}. Please enter a valid number.")
                except ValueError:
                    error_messages.append(f"Invalid marks entered for {student.name}. Please enter a valid number.")
                except IntegrityError as e:
                    # Log the error message for debugging
                    print(f"IntegrityError for {student.name}: {e}")
                    error_messages.append(f"Failed to save marks for {student.name}. Please try again.")
                except Exception as e:
                    # Log any unexpected errors
                    print(f"Unexpected error for {student.name}: {e}")
                    error_messages.append(f"An unexpected error occurred while saving marks for {student.name}. Please try again.")
        
        # If there are errors, return to the form with those errors
        if error_messages:
            # Fetch the marks again, so it persists after form submission
            student_marks = [
                {
                    'student': student,
                    'marks': Marks.objects.filter(student=student, test=test).first().marks if Marks.objects.filter(student=student, test=test).first() else ''
                }
                for student in students
            ]
            return render(request, 'test_marks_entry.html', {
                'test': test,
                'student_marks': student_marks,
                'error_messages': error_messages,
            })

        # After successfully saving marks, redirect back to the same page
        return redirect('test_marks_entry', test_id=test_id)

    # Fetch marks for all students for this test
    student_marks = [
        {
            'student': student,
            'marks': Marks.objects.filter(student=student, test=test).first().marks if Marks.objects.filter(student=student, test=test).first() else ''
        }
        for student in students
    ]

    return render(request, 'test_marks_entry.html', {
        'test': test,
        'student_marks': student_marks,
    })
@login_required
# Delete Marks Entry
def delete_marks(request, student_id, test_id):
    print(f"Attempting to delete marks for student_id={student_id}, test_id={test_id}")
    try:
        mark = get_object_or_404(Marks, student_id=student_id, test_id=test_id)
        mark.delete()
        return redirect('test_marks_entry', test_id=test_id)
    except Marks.DoesNotExist:
        print("No matching record found in Marks table.")
        return redirect('test_marks_entry', test_id=test_id)

@login_required
def active_test_list(request):
    tests = Test.objects.all()
    return render(request, 'active_test_list.html', {'tests': tests})

def logout_view(request):
    logout(request)
    return redirect('login')

#31/12/2024
@login_required
def school_student_list(request):
    schools = School.objects.all()
    school_students = {}

    # Get students for each school
    for school in schools:
        school_students[school] = school.student_set.all()

    return render(request, 'school_student_list.html', {'school_students': school_students})



# Math Tools Functions
def get_available_books():
    """Return a list of available books from the content directory"""
    content_dir = os.path.join(settings.BASE_DIR, 'school_app', 'content')
    books = []
    
    try:
        # List all directories (books) in content folder
        book_dirs = [d for d in os.listdir(content_dir) 
                    if os.path.isdir(os.path.join(content_dir, d))]
        
        for book_dir in book_dirs:
            content_file = os.path.join(content_dir, book_dir, 'content.json')
            if os.path.exists(content_file):
                with open(content_file, 'r', encoding='utf-8') as f:
                    book_info = json.load(f)
                    books.append({
                        'id': book_dir,  # Use directory name as ID
                        'name': book_info['book_name'],
                        'language': book_info['language'],
                        'class': book_info['class']
                    })
    except Exception as e:
        print(f"Error loading books: {e}")
    
    return books

def load_chapter_content(book_id, chapter_id):
    """Load the content of a specific chapter from a book"""
    try:
        chapter_file = os.path.join(
            settings.BASE_DIR, 
            'school_app', 
            'content', 
            book_id, 
            f'chapter{chapter_id}.json'
        )
        
        with open(chapter_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading chapter content: {e}")
        return None
    
def get_book_chapters(book_id):
    """Return a list of chapters for a given book ID"""
    try:
        content_file = os.path.join(
            settings.BASE_DIR,
            'school_app',
            'content',
            book_id,
            'content.json'
        )
        
        if os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8') as f:
                book_info = json.load(f)
                return book_info.get('chapters', [])
        return []
        
    except Exception as e:
        print(f"Error loading chapters for book {book_id}: {e}")
        return []

@login_required
def math_tools(request):
    context = {
        'books': get_available_books(),
        'selected_book': request.session.get('selected_book'),
        'selected_chapter': request.session.get('selected_chapter')
    }
    
    # If a book is selected, load its chapters
    if context['selected_book']:
        context['chapters'] = get_book_chapters(context['selected_book'])
    
    return render(request, 'school_app/math_tools.html', context)

@login_required
def load_questions(request):
    if request.method == 'POST':
        book_id = request.POST.get('book')
        chapter_id = request.POST.get('chapter')
        
        if not book_id or not chapter_id:
            messages.error(request, 'Please select both book and chapter')
            return redirect('math_tools')
        
        # Store selections in session
        request.session['selected_book'] = book_id
        request.session['selected_chapter'] = chapter_id
        
        # Load chapter content
        content = load_chapter_content(book_id, chapter_id)
        
        context = {
            'books': get_available_books(),
            'selected_book': book_id,
            'chapters': get_book_chapters(book_id),
            'selected_chapter': chapter_id,
        }
        
        if content:
            context['questions'] = content.get('exercises', [])
            # Get chapter name for display
            for chapter in context['chapters']:
                if str(chapter['id']) == str(chapter_id):
                    context['chapter_name'] = chapter['name']
                    break
        else:
            messages.warning(
                request, 
                f'No content found for Chapter {chapter_id} in selected book'
            )
        
        return render(request, 'school_app/math_tools.html', context)
    
    return redirect('math_tools')

def get_book_language(book_id):
    """Determine the language of a book based on its content.json file"""
    try:
        content_file = os.path.join(
            settings.BASE_DIR,
            'school_app',
            'content',
            book_id,
            'content.json'
        )
        
        if os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8') as f:
                book_info = json.load(f)
                return book_info.get('language', 'English')  # Default to English if not specified
        return 'English'  # Default to English if file doesn't exist
        
    except Exception as e:
        print(f"Error determining book language for {book_id}: {e}")
        return 'English'  # Default to English on error

from .solution_formatter import SolutionFormatter
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from asgiref.sync import async_to_sync



@login_required
@require_http_methods(["POST"])

def solve_math(request):
    if request.method == 'POST':
        try:
            # Get questions and book ID from POST data
            questions_json = request.POST.get('questions')
            book_id = request.session.get('selected_book')
            
            if not questions_json:
                messages.error(request, 'No questions selected')
                return redirect('math_tools')

            # Get the book's language
            language = get_book_language(book_id)

            # Parse the JSON string to get list of questions
            questions = json.loads(questions_json)
            
            # If questions is a string, try to parse it again
            if isinstance(questions, str):
                try:
                    questions = json.loads(questions)
                except json.JSONDecodeError:
                    pass

            solutions = []

            # Convert questions to list if it's not already
            if not isinstance(questions, list):
                questions = [questions]

            # Solve each question in the appropriate language
            for question_data in questions:
                # If question_data is a string, try to parse it as JSON
                if isinstance(question_data, str):
                    try:
                        question_data = json.loads(question_data)
                    except json.JSONDecodeError:
                        pass

                if isinstance(question_data, dict):
                    question = question_data.get('question', '')
                    img_filename = question_data.get('img', '')
                    
                    # Construct absolute path to image
                    if img_filename:
                        img_path = os.path.join(
                            settings.BASE_DIR,
                            'school_app',
                            'static',
                            'school_app',
                            'images',
                            img_filename
                        )
                        
                        if os.path.exists(img_path):
                            raw_solution = async_to_sync(async_solve_math_problem)(
                                question=question,
                                image_path=img_path,
                                language=language
                            )
                        else:
                            raw_solution = async_to_sync(async_solve_math_problem)(question=question, language=language)
                    else:
                        raw_solution = async_to_sync(async_solve_math_problem)(question=question, language=language)
                else:
                    question = question_data
                    raw_solution = async_to_sync(async_solve_math_problem)(question=question, language=language)
                
                # Format the solution using the SolutionFormatter
                formatted_solution = SolutionFormatter.format_solution(raw_solution)
                # formatted_question = SolutionFormatter.format_question(
                #     question if 'question' in locals() else question_data
                # )
                
                # For template display, use the static URL path for images
                static_img_url = img_filename if 'img_filename' in locals() else None
                
                solutions.append({
                    'question': question,
                    'img': static_img_url,
                    'solution': formatted_solution
                })

            context = {
                'solutions': solutions,
                'language': language,
                'original_book': book_id,
                'original_chapter': request.session.get('selected_chapter')
            }

            return render(request, 'school_app/solutions.html', context)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")  # Debug print
            error_msg = 'Invalid question data received' if language == 'English' else 'अमान्य प्रश्न डेटा प्राप्त हुआ'
            messages.error(request, error_msg)
        except Exception as e:
            print(f"Error processing request: {e}")  # Debug print
            error_msg = f'Error solving questions: {str(e)}' if language == 'English' else f'प्रश्नों को हल करने में त्रुटि: {str(e)}'
            messages.error(request, error_msg)
    
    return redirect('math_tools')


@login_required
def generate_math(request):
    """
    View function to handle math question generation with language support.
    """
    try:
        # Get questions from POST data
        questions_json = request.POST.get('questions')
        book_id = request.session.get('selected_book')
        
        if not questions_json:
            messages.error(request, 'No questions selected')
            return redirect('math_tools')

        # Get the book's language
        language = get_book_language(book_id)

        # Error messages based on language
        error_messages = {
            'Hindi': {
                'no_questions': 'कोई प्रश्न नहीं चुना गया है। कृपया मुख्य पृष्ठ से प्रश्न चुनें।',
                'generating': 'प्रश्न उत्पन्न किए जा रहे हैं... कृपया प्रतीक्षा करें',
                'error': 'प्रश्न उत्पन्न करने में त्रुटि:',
                'invalid_data': 'अमान्य प्रश्न डेटा प्राप्त हुआ'
            },
            'English': {
                'no_questions': 'No questions selected. Please select questions from the main page.',
                'generating': 'Generating questions... please wait',
                'error': 'Error generating questions:',
                'invalid_data': 'Invalid question data received'
            }
        }

        # Parse the JSON string to get list of questions
        questions = json.loads(questions_json)
        
        if request.method == 'POST':
            difficulty = request.POST.get('difficulty', 'Same Level')
            num_questions = int(request.POST.get('num_questions', 5))
            question_type = request.POST.get('question_type', 'Same as Original')

            # Calculate distribution of questions
            num_selected = len(questions)
            base_count = num_questions // num_selected
            remainder = num_questions % num_selected
            distribution = [base_count] * num_selected
            for i in range(remainder):
                distribution[i] += 1

            all_generated_questions = []

            # Generate questions using the book's language
            for i, (question, count) in enumerate(zip(questions, distribution)):
                try:
                    generated_content = async_to_sync(async_generate_similar_questions)(
                        question=question,
                        difficulty=difficulty,
                        num_questions=count,
                        language=language,  # Use book's language
                        question_type=question_type
                    )
                    all_generated_questions.append(generated_content)
                    
                except Exception as e:
                    error_msg = f"{error_messages[language]['error']} {str(e)}"
                    messages.error(request, error_msg)
                    continue

            # Combine all generated questions
            combined_content = "\n\n".join(all_generated_questions)
            formatted_content = SolutionFormatter.format_solution(combined_content)

            context = {
                'generated_questions': formatted_content,
                'original_questions': questions,
                'language': language,
                'question_type': question_type,
                'difficulty': difficulty,
                'num_questions': num_questions,
                'questions_json': questions_json
            }

            return render(request, 'school_app/math_tools.html', context)

    except json.JSONDecodeError:
        messages.error(request, error_messages[language]['invalid_data'])
    except Exception as e:
        error_msg = f"{error_messages[language]['error']} {str(e)}"
        messages.error(request, error_msg)

    return redirect('math_tools')

@login_required
def get_chapters(request, book_id):
    try:
        chapters = get_book_chapters(book_id)
        return JsonResponse({'chapters': chapters})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def generate_form(request):
    if request.method == 'POST':
        questions = json.loads(request.POST.get('questions', '[]'))
        context = {
            'questions': questions,
            'questions_json': request.POST.get('questions')
        }
        return render(request, 'school_app/generate_form.html', context)
    return redirect('math_tools')

@login_required
def student_edit(request, student_id):
    school = School.objects.get(admin=request.user)
    student = get_object_or_404(Student, id=student_id, school=school)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'school_app/student_edit.html', {'form': form})

@login_required
def marks_edit(request, marks_id):
    school = School.objects.get(admin=request.user)
    marks = get_object_or_404(Marks, id=marks_id, student__school=school)
    
    if request.method == 'POST':
        form = MarksForm(request.POST, instance=marks)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marks updated successfully!')
            return redirect('marks_list')
    else:
        form = MarksForm(instance=marks)
        # Limit student choices to only those in the current school
        form.fields['student'].queryset = Student.objects.filter(school=school)
    
    return render(request, 'school_app/marks_edit.html', {'form': form})

@login_required
def analysis_dashboard(request):
    """Render the analysis dashboard page"""
    return render(request, 'school_app/analysis_dashboard.html')

@login_required
def analysis_dashboard(request):
    """Render the analysis dashboard page"""
    return render(request, 'school_app/analysis_dashboard.html')

@login_required
def get_students(request):
    """API endpoint to get list of students"""
    try:
        # If user is a school admin, get only their school's students
        if hasattr(request.user, 'administered_school'):
            school = School.objects.get(admin=request.user)
            students = Student.objects.filter(school=school)
            print(f"Found {students.count()} students for school {school.name}")  # Debug print
        else:
            # For system admin or collector, get all students
            students = Student.objects.all()
            print(f"Found {students.count()} students total")  # Debug print
        
        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'name': student.name,
                'roll_number': student.roll_number,
                'class_name': student.class_name
            })
        
        print("Students data:", students_data)  # Debug print
        return JsonResponse({'students': students_data})
    except Exception as e:
        print(f"Error in get_students: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=500)


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Student, Marks

@login_required
def get_student_analysis(request, student_id):
    """API endpoint to get detailed analysis for a specific student"""
    try:
        # Get the student
        if hasattr(request.user, 'administered_school'):
            # School admin can only see their school's students
            student = get_object_or_404(Student, id=student_id, school=request.user.administered_school)
        else:
            # System admin or collector can see all students
            student = get_object_or_404(Student, id=student_id)
        
        # Get all marks for the student
        marks = Marks.objects.filter(student=student).select_related('test')
        
        # Calculate class averages for each test
        test_performance = []
        for mark in marks:
            # Get class average for this test
            class_average = Marks.objects.filter(
                test=mark.test,
                student__class_name=student.class_name,
                student__school=student.school  # Only compare with students from same school
            ).aggregate(Avg('marks'))['marks__avg']
            
            test_performance.append({
                'test_id': mark.test.test_number,
                'test_name': mark.test.test_name,
                'subject': mark.test.subject_name,
                'date': mark.test.test_date.strftime('%Y-%m-%d') if mark.test.test_date else None,
                'marks': float(mark.marks),
                'class_average': round(float(class_average), 2) if class_average else None
            })
        
        # Sort by test date
        test_performance.sort(key=lambda x: x['date'] if x['date'] else '')
        
        # Calculate overall statistics
        all_marks = [mark.marks for mark in marks]
        average_marks = sum(all_marks) / len(all_marks) if all_marks else 0
        highest_mark = max(all_marks) if all_marks else 0
        lowest_mark = min(all_marks) if all_marks else 0
        
        response_data = {
            'name': student.name,
            'roll_number': student.roll_number,
            'class_name': student.class_name,
            'test_performance': test_performance,
            'statistics': {
                'average_marks': round(average_marks, 2),
                'highest_mark': round(highest_mark, 2),
                'lowest_mark': round(lowest_mark, 2),
                'total_tests': len(all_marks)
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Error in get_student_analysis: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=500)