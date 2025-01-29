from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import School, Student, Marks,Block,Attendance
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
from .models import CustomUser
from .forms import ExcelFileUploadForm 
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count, Q, F
from datetime import date
from django.utils.dateparse import parse_date
from django.db.models import Avg, F, ExpressionWrapper, FloatField,Sum
from django.db.models import Count, Case, When, IntegerField,Value
from django.db import connection
#21012025

@login_required
def block_attendance_report(request):
    
    if request.user.is_district_user:
     blocks = Block.objects.all()
    elif request.user.is_block_user:
     blocks = Block.objects.get(admin=request.user)
    report = []

    for block in blocks:
        #schools = School.objects.get(block=block)
        schools = block.schools.all()
        total_students = 0
        total_present = 0
        total_absent = 0

        for school in schools:
            total_students += school.student_set.count()
            attendance_records = Attendance.objects.filter(student__school=school)
            total_present += attendance_records.filter(is_present=True).count()
            total_absent += attendance_records.filter(is_present=False).count()

        # Calculate attendance percentage
        percentage = (total_present / total_students * 100) if total_students > 0 else 0

        # Append block data to the report
        report.append({
            "block_name": block.name_english,
            "total_students": total_students,
            "total_present": total_present,
            "total_absent": total_absent,
            "percentage": f"{percentage:.2f}%",
        })

    return render(request, "block_attendance_report.html", {"report": report})

@login_required
def school_daily_attendance_summary(request):
    # Fetch attendance data grouped by school and date
    attendance_summary = (
        Attendance.objects.values('student__school__name', 'date')
        .annotate(
            total_students=Count('student'),
            present_students=Count('student', filter=Q(is_present=True)),
            absent_students=Count('student', filter=Q(is_present=False)),
        )
        .order_by('date', 'student__school__name')
    )

    # Restructure data for the template
    summary_by_school_and_date = {}
    for record in attendance_summary:
        school_name = record['student__school__name']
        date = record['date']
        if date not in summary_by_school_and_date:
            summary_by_school_and_date[date] = []
        summary_by_school_and_date[date].append({
            'school_name': school_name,
            'total_students': record['total_students'],
            'present_students': record['present_students'],
            'absent_students': record['absent_students'],
        })

    return render(request, 'school_daily_attendance_summary.html', {
        'summary_by_school_and_date': summary_by_school_and_date
    })
#1401025 Sushil Agrawal
@login_required
def block_wise_attendance_summary(request):
    # Get filter inputs
    start_date = parse_date(request.GET.get('start_date', ''))
    end_date = parse_date(request.GET.get('end_date', ''))

    # Fetch attendance data with optional date filtering
    attendance_queryset = Attendance.objects.all()
    if start_date and end_date:
        attendance_queryset = attendance_queryset.filter(date__range=(start_date, end_date))

    attendance_summary = (
        attendance_queryset.values('student__school__block__name_english', 'date')
        .annotate(
            total_students=Count('student'),
            present_students=Count('student', filter=Q(is_present=True)),
            absent_students=Count('student', filter=Q(is_present=False)),
        )
        .order_by('date', 'student__school__block__name_english')
    )

    # Restructure data for the template
    summary_by_block_and_date = {}
    for record in attendance_summary:
        block_name = record['student__school__block__name_english']
        date = record['date']
        if date not in summary_by_block_and_date:
            summary_by_block_and_date[date] = []
        summary_by_block_and_date[date].append({
            'block_name': block_name,
            'total_students': record['total_students'],
            'present_students': record['present_students'],
            'absent_students': record['absent_students'],
        })

    return render(request, 'block_wise_attendance_summary.html', {
        'summary_by_block_and_date': summary_by_block_and_date,
        'start_date': start_date,
        'end_date': end_date
    })
@login_required
def district_wise_attendance_summary(request):
    # Fetch attendance data grouped by district and date
    attendance_summary = (
        Attendance.objects.values('student__school__block__name_english', 'date')
        .annotate(
            total_students=Count('student'),
            present_students=Count('student', filter=Q(is_present=True)),
            absent_students=Count('student', filter=Q(is_present=False)),
        )
        .order_by('date', 'student__school__block__name_english')
    )

    # Restructure data for template
    summary_by_district_and_date = {}
    for record in attendance_summary:
        district_name = record['student__school__block__name_english']
        date = record['date']
        if date not in summary_by_district_and_date:
            summary_by_district_and_date[date] = []
        summary_by_district_and_date[date].append({
            'district_name': district_name,
            'total_students': record['total_students'],
            'present_students': record['present_students'],
            'absent_students': record['absent_students'],
        })

    return render(request, 'district_wise_attendance_summary.html', {
        'summary_by_district_and_date': summary_by_district_and_date
    })
@login_required
def date_wise_attendance_summary(request):
    # Fetch attendance data grouped by school and date
    attendance_summary = (
        Attendance.objects.values('student__school__name', 'date')
        .annotate(
            total_students=Count('student'),
            present_students=Count('student', filter=Q(is_present=True)),
            absent_students=Count('student', filter=Q(is_present=False)),
        )
        .order_by('date', 'student__school__name')
    )

    # Restructure data for easy use in the template
    summary_by_date = {}
    for record in attendance_summary:
        school_name = record['student__school__name']
        date = record['date']
        if date not in summary_by_date:
            summary_by_date[date] = []
        summary_by_date[date].append({
            'school_name': school_name,
            'total_students': record['total_students'],
            'present_students': record['present_students'],
            'absent_students': record['absent_students'],
        })

    return render(request, 'date_wise_attendance_summary.html', {'summary_by_date': summary_by_date})
#1201025 Sushil Agrawal
# View to calculate test results by percentage ranges

@login_required
def test_results_analysis(request):
    # Determine filter based on user type
    if request.user.is_district_user:
        # District user: View all schools
        schools = School.objects.all()
    elif request.user.is_block_user:
        # Block user: View schools in the same block
        block = Block.objects.get(admin=request.user)
        schools = School.objects.filter(block=block)
    else:
        # School user: View only their own school
        school = School.objects.get(admin=request.user)
        schools = [school]

    # Optional: Filter by selected block
    selected_block_id = request.GET.get('block', None)
    if selected_block_id:
        schools = schools.filter(block_id=selected_block_id)

    # Check if specific tests are selected, and filter accordingly
    selected_test_numbers = request.GET.getlist('test', [])
    selected_test_numbers = [test for test in selected_test_numbers if test]

    if not selected_test_numbers:
        # If no tests are selected, show results for all tests
        school_tests = Test.objects.filter(marks__student__school__in=schools).distinct().order_by('test_name')
    else:
        # If specific tests are selected, show results only for those tests
        school_tests = Test.objects.filter(test_number__in=selected_test_numbers).distinct().order_by('test_name')

    results = []
    
    for school in schools:
        school_data = {
            'school_name': school.name,
            'block_name': school.block.name_english if school.block else "N/A",
            'tests': []
        }

        for test in school_tests:
            total_students = Student.objects.filter(school=school).count()

            # Fetch marks for this test and school
            marks = Marks.objects.filter(test=test, student__school=school)
            max_marks = test.max_marks
            
            # Calculate the number of students in each percentage range
            category_0_33 = marks.filter(marks__lt=(0.33 * max_marks)).count()
            category_33_60 = marks.filter(marks__gte=(0.33 * max_marks), marks__lt=(0.60 * max_marks)).count()
            category_60_80 = marks.filter(marks__gte=(0.60 * max_marks), marks__lt=(0.80 * max_marks)).count()
            category_80_90 = marks.filter(marks__gte=(0.80 * max_marks), marks__lt=(0.90 * max_marks)).count()
            category_90_100 = marks.filter(marks__gte=(0.90 * max_marks), marks__lt=max_marks).count()
            category_100 = marks.filter(marks=max_marks).count()

            # Avoid division by zero
            if total_students > 0:
                test_data = {
                    'test_name': test.test_name,
                    'total_students': total_students,
                    'category_0_33': f"{category_0_33}/{total_students} ({(category_0_33 / total_students * 100):.2f}%)",
                    'category_33_60': f"{category_33_60}/{total_students} ({(category_33_60 / total_students * 100):.2f}%)",
                    'category_60_80': f"{category_60_80}/{total_students} ({(category_60_80 / total_students * 100):.2f}%)",
                    'category_80_90': f"{category_80_90}/{total_students} ({(category_80_90 / total_students * 100):.2f}%)",
                    'category_90_100': f"{category_90_100}/{total_students} ({(category_90_100 / total_students * 100):.2f}%)",
                    'category_100': f"{category_100}/{total_students} ({(category_100 / total_students * 100):.2f}%)",
                }
            else:
                test_data = {
                    'test_name': test.test_name,
                    'total_students': total_students,
                    'category_0_33': "N/A",
                    'category_33_60': "N/A",
                    'category_60_80': "N/A",
                    'category_80_90': "N/A",
                    'category_90_100': "N/A",
                    'category_100': "N/A",
                }

            school_data['tests'].append(test_data)

        results.append(school_data)

    # Get all blocks for filtering purposes (to select block in dropdown)
    blocks = Block.objects.all()
 # Get all tests for dropdown selection
    tests = Test.objects.all()
    context = {
        'results': results,
        'blocks': blocks,
        'tests':tests,
        'selected_block_id': selected_block_id,
        'selected_test_numbers': selected_test_numbers,
    }

    return render(request, 'test_results_analysis.html', context)

@login_required
def test_wise_average_marks(request):
    from django.db.models import Avg, F, ExpressionWrapper, FloatField
    from django.db.models import Count, Case, When, IntegerField
    
    if request.user.is_district_user:
     data = (
        Test.objects.annotate(
            avg_marks=Avg('marks__marks'),
            percentage=ExpressionWrapper(
                F('avg_marks') * 100 / F('max_marks'),               
                output_field=FloatField()),
            # Count the total number of students for each test
            total_students=Count('marks', distinct=True),  # Total number of students
            # Count the number of students with marks less than 0 (invalid or missing)
            category_0_and_less=Count(Case(When(marks__marks__lte=0, then=1), output_field=IntegerField())),
            category_0_33=Count(Case(When(marks__marks__gte=F('max_marks') * 0.01,marks__marks__lt=F('max_marks') * 0.33, then=1), output_field=IntegerField())),
            category_33_60=Count(Case(When(marks__marks__gte=F('max_marks') * 0.33, marks__marks__lt=F('max_marks') * 0.60, then=1), output_field=IntegerField())),
            category_60_80=Count(Case(When(marks__marks__gte=F('max_marks') * 0.60, marks__marks__lt=F('max_marks') * 0.80, then=1), output_field=IntegerField())),
            category_80_90=Count(Case(When(marks__marks__gte=F('max_marks') * 0.80, marks__marks__lt=F('max_marks') * 0.90, then=1), output_field=IntegerField())),
            category_90_100=Count(Case(When(marks__marks__gte=F('max_marks') * 0.90, marks__marks__lt=F('max_marks'), then=1), output_field=IntegerField())),
            category_100=Count(Case(When(marks__marks=F('max_marks') , then=1), output_field=IntegerField()))
        )
        .values('test_name', 'avg_marks', 'percentage', 'total_students', 'category_0_and_less', 
                'category_0_33', 'category_33_60', 'category_60_80', 'category_80_90', 'category_90_100', 'category_100')
        .order_by('-percentage')
    )
    elif request.user.is_block_user:
       block = Block.objects.get(admin=request.user)
       data = (
        Test.objects.filter(marks__student__school__block_id=block.id).annotate(
            avg_marks=Avg('marks__marks'),
            percentage=ExpressionWrapper(
                F('avg_marks') * 100 / F('max_marks'),               
                output_field=FloatField()),
            # Count the total number of students for each test
            total_students=Count('marks', distinct=True),  # Total number of students
            # Count the number of students with marks less than 0 (invalid or missing)
            category_0_and_less=Count(Case(When(marks__marks__lte=0, then=1), output_field=IntegerField())),
            category_0_33=Count(Case(When(marks__marks__gte=F('max_marks') * 0.01,marks__marks__lt=F('max_marks') * 0.33, then=1), output_field=IntegerField())),
            category_33_60=Count(Case(When(marks__marks__gte=F('max_marks') * 0.33, marks__marks__lt=F('max_marks') * 0.60, then=1), output_field=IntegerField())),
            category_60_80=Count(Case(When(marks__marks__gte=F('max_marks') * 0.60, marks__marks__lt=F('max_marks') * 0.80, then=1), output_field=IntegerField())),
            category_80_90=Count(Case(When(marks__marks__gte=F('max_marks') * 0.80, marks__marks__lt=F('max_marks') * 0.90, then=1), output_field=IntegerField())),
            category_90_100=Count(Case(When(marks__marks__gte=F('max_marks') * 0.90, marks__marks__lt=F('max_marks'), then=1), output_field=IntegerField())),
            category_100=Count(Case(When(marks__marks=F('max_marks') , then=1), output_field=IntegerField()))
        )
        .values('test_name', 'avg_marks', 'percentage', 'total_students', 'category_0_and_less', 
                'category_0_33', 'category_33_60', 'category_60_80', 'category_80_90', 'category_90_100', 'category_100')
        .order_by('-percentage')
    )

    elif request.user.is_school_user:
     school = School.objects.get(admin=request.user)
     data = (
        Test.objects.filter(marks__student__school=school).annotate(
            avg_marks=Avg('marks__marks'),
            percentage=ExpressionWrapper(
                F('avg_marks') * 100 / F('max_marks'),               
                output_field=FloatField()),
            # Count the total number of students for each test
            total_students=Count('marks', distinct=True),  # Total number of students
            # Count the number of students with marks less than 0 (invalid or missing)
            category_0_and_less=Count(Case(When(marks__marks__lte=0, then=1), output_field=IntegerField())),
            category_0_33=Count(Case(When(marks__marks__gte=F('max_marks') * 0.01,marks__marks__lt=F('max_marks') * 0.33, then=1), output_field=IntegerField())),
            category_33_60=Count(Case(When(marks__marks__gte=F('max_marks') * 0.33, marks__marks__lt=F('max_marks') * 0.60, then=1), output_field=IntegerField())),
            category_60_80=Count(Case(When(marks__marks__gte=F('max_marks') * 0.60, marks__marks__lt=F('max_marks') * 0.80, then=1), output_field=IntegerField())),
            category_80_90=Count(Case(When(marks__marks__gte=F('max_marks') * 0.80, marks__marks__lt=F('max_marks') * 0.90, then=1), output_field=IntegerField())),
            category_90_100=Count(Case(When(marks__marks__gte=F('max_marks') * 0.90, marks__marks__lt=F('max_marks'), then=1), output_field=IntegerField())),
            category_100=Count(Case(When(marks__marks=F('max_marks') , then=1), output_field=IntegerField()))
        )
        .values('test_name', 'avg_marks', 'percentage', 'total_students', 'category_0_and_less', 
                'category_0_33', 'category_33_60', 'category_60_80', 'category_80_90', 'category_90_100', 'category_100')
        .order_by('-percentage')
    )

    context = {'data': data}
    return render(request, 'test_wise_average.html', context)

@login_required
def submit_attendance(request):
    if request.user.is_school_user:
        try:
            school = School.objects.get(admin=request.user)
            students = Student.objects.filter(school=school)
        except School.DoesNotExist:
            return redirect('error_page')

        if request.method == 'POST':
            selected_students = request.POST.getlist('absent_students')
            for student in students:
                is_present = str(student.id) not in selected_students
                try:
                    # Use filter() and update() instead of update_or_create() to avoid duplicates
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        date=timezone.now().date(),
                        defaults={'is_present': is_present}
                    )
                    if not created:
                        attendance.is_present = is_present
                        attendance.save()
                except IntegrityError:
                    # Log error and handle it gracefully
                    print(f"Duplicate attendance record for student {student.id} on {timezone.now().date()}")
            return redirect('attendance_summary')

        context = {'students': students}
        return render(request, 'attendance_submit.html', context)

    return redirect('system_admin_dashboard')
@login_required
def attendance_summary(request):
    user = request.user
    today = date.today()
    attendance = []

    if user.is_district_user:
        # District-level summary
        attendance = Attendance.objects.filter(date=today).values(
            'student__school__name'
        ).annotate(
            present_count=Count('is_present', filter=F('is_present')),
            total_count=Count('student'),
            Percentage=Count('is_present', filter=F('is_present'))*100/Count('student'),
        )

    elif user.is_block_user:
        # Block-level summary
        attendance = Attendance.objects.filter(
            date=today, student__school__created_by=user
        ).values('student__school__name').annotate(
            present_count=Count('is_present', filter=F('is_present')),
            total_count=Count('student'),
            Percentage=Count('is_present', filter=F('is_present'))*100/Count('student'),
        )

    elif user.is_school_user:
        # School-level summary
        try:
            school = School.objects.get(admin=request.user)
            #students = Student.objects.filter(school=school)
            attendance = Attendance.objects.filter(
                date=today, student__school=school
            ).values('student__school__name').annotate(
                present_count=Count('is_present', filter=F('is_present')),
                total_count=Count('student'),
                Percentage=Count('is_present', filter=F('is_present'))*100/Count('student'),
            )
        except School.DoesNotExist:
            return render(request, 'error_page.html', {'message': 'School not found.'})

    context = {'attendance_summary': attendance,  'attendance_date': today,}
    return render(request, 'attendance_summary.html', context)
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
    # Retrieve the list of available tests
    tests = Test.objects.all()
    
    # Check if a test is selected, and fetch data for that test
    selected_test = request.GET.get('test_id')  # Assume the selected test's ID is sent in the query string
    #print(selected_test)
    # Annotate school data with test counts and students, filtered by the selected test if any
    if selected_test:
        schools = School.objects.filter(
            student__marks__test_id=selected_test
        ).annotate(
            test_count=Count('student__marks__test'),
            total_students=Count('student')
        ).order_by('-total_students')
    else:
        # If no test is selected, show data for all tests
        schools = School.objects.annotate(
            test_count=Count('student__marks__test'),
            total_students=Count('student')
        ).order_by('-total_students')

# Calculate the difference for each school and add it to the context
    for school in schools:
        school.difference = school.total_students - school.test_count
    # Compute totals for all schools if no specific test is selected
    total_students_all = sum(school.total_students for school in schools)
    total_tests_all = sum(school.test_count for school in schools)
    total_difference_all = total_students_all - total_tests_all

    # Add the "All Schools" row
    all_schools_row = {
        'name': 'All Schools',
        'total_students': total_students_all,
        'test_count': total_tests_all,
        'difference': total_difference_all
    }

    # Add this row at the end
    schools = list(schools) + [all_schools_row]

    context = {
        'schools': schools,
        'tests': tests,
        'selected_test': selected_test,
    }
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
    # First, we will fetch schools and aggregate the average marks for each test in each school
    
    if request.user.is_district_user:
        schools = School.objects.all()
    else:
        block = Block.objects.get(admin=request.user)
        schools = School.objects.all().filter(block=block)
    
    results = []

    for school in schools:
        school_data = {
            'school_name': school.name,
            'test_averages': [],
            'school_average': 0
        }

        # Get all tests associated with the school
        tests = Test.objects.filter(marks__student__school=school).distinct()

        # List to hold all test averages for calculating school average later
        test_avg_list = []

        for test in tests:
            # Get the average marks for the school in the current test
            avg_marks = Marks.objects.filter(test=test, student__school=school).aggregate(avg_marks=Avg('marks'))['avg_marks']

            if avg_marks is not None:
                test_avg_list.append(avg_marks)
            else:
                test_avg_list.append(0)

            # Add the test average to the school's data
            school_data['test_averages'].append({
                'test_name': test.subject_name,
                'average_marks': avg_marks if avg_marks is not None else 0
            })

        # Calculate the overall school average by averaging all test averages
        if test_avg_list:
            school_data['school_average'] = sum(test_avg_list) / len(test_avg_list)

        # Add the school data to the results
        results.append(school_data)

    # Sort the schools based on the highest overall school average
    results.sort(key=lambda x: x['school_average'], reverse=True)
    
    context = {'results': results}
    return render(request, 'school_average.html', context)


@login_required
def top_students(request):
    # Get selected test numbers (default: all tests)
    selected_test_numbers = request.GET.getlist('test', [])
    selected_test_numbers = [test for test in selected_test_numbers if test]

    # Determine total available tests
    total_tests_count = Test.objects.count() if not selected_test_numbers else len(selected_test_numbers)

    # Filter students based on user role
    if request.user.is_district_user:
        students_filter = {}
    elif request.user.is_block_user:
        block = Block.objects.get(admin=request.user)
        schools_in_block = School.objects.filter(block=block)
        students_filter = {'student__school__in': schools_in_block}
    else:
        school = School.objects.get(admin=request.user)
        students_filter = {'student__school': school}

    # Base query (filtered by user role)
    queryset = Marks.objects.filter(**students_filter)
    if selected_test_numbers:
        queryset = queryset.filter(test__test_number__in=selected_test_numbers)

    # Aggregate data
    data = (
        queryset
        .values('student__name', 'student__school__name', 'student__school__block__name_english')
        .annotate(
            total_marks=Sum(F('marks')),
            total_max_marks=Sum(F('test__max_marks')),
            test_attempted=Count('test', distinct=True),  # Count distinct tests attempted
            percentage=ExpressionWrapper(
                (Sum(F('marks')) * 100.0) / Sum(F('test__max_marks')),
                output_field=FloatField()
            )
        )
        .filter(
            total_marks=F('total_max_marks'),  # Ensure full marks
            test_attempted=total_tests_count  # Ensure student attempted all tests
        )
        .order_by('-percentage')
    )

    # Get total maximum marks for selected tests (for percentage calculation)
    selected_tests_max_marks = Test.objects.filter(test_number__in=selected_test_numbers).aggregate(
        total_max_marks=Sum('max_marks')
    )['total_max_marks'] if selected_test_numbers else Test.objects.aggregate(
        total_max_marks=Sum('max_marks')
    )['total_max_marks']

    # Get all tests for dropdown selection
    tests = Test.objects.all()

    context = {
        'data': data,
        'tests': tests,
        'selected_test_numbers': selected_test_numbers,
        'selected_tests_max_marks': selected_tests_max_marks
    }

    return render(request, 'top_students.html', context)

@login_required
def weakest_students(request):
    # Get selected test numbers (default: all tests)
    selected_test_numbers = request.GET.getlist('test', [])
    selected_test_numbers = [test for test in selected_test_numbers if test]

    # Determine total available tests
    total_tests_count = Test.objects.count() if not selected_test_numbers else len(selected_test_numbers)

    # Filter students based on user role
    if request.user.is_district_user:
        students_filter = {}
    elif request.user.is_block_user:
        block = Block.objects.get(admin=request.user)
        schools_in_block = School.objects.filter(block=block)
        students_filter = {'student__school__in': schools_in_block}
    else:
        school = School.objects.get(admin=request.user)
        students_filter = {'student__school': school}

    # Base query (filtered by user role)
    queryset = Marks.objects.filter(**students_filter)
    if selected_test_numbers:
        queryset = queryset.filter(test__test_number__in=selected_test_numbers)

    # Aggregate data
    data = (
        queryset
        .values('student__name', 'student__school__name', 'student__school__block__name_english')
        .annotate(
            total_marks=Sum(F('marks')),
            total_max_marks=Sum(F('test__max_marks')),
            test_attempted=Count('test', distinct=True),  # Count distinct tests attempted
            percentage=ExpressionWrapper(
                (Sum(F('marks')) * 100.0) / Sum(F('test__max_marks')),
                output_field=FloatField()
            )
        )
        .filter(
            percentage__lt=33,  # Students scoring less than 33%
            test_attempted=total_tests_count  # Ensure student attempted all tests
        )
        .order_by('student__school__block__name_english','percentage')  # Weakest students first
    )

    # Get total maximum marks for selected tests (for percentage calculation)
    selected_tests_max_marks = Test.objects.filter(test_number__in=selected_test_numbers).aggregate(
        total_max_marks=Sum('max_marks')
    )['total_max_marks'] if selected_test_numbers else Test.objects.aggregate(
        total_max_marks=Sum('max_marks')
    )['total_max_marks']

    # Get all tests for dropdown selection
    tests = Test.objects.all()

    context = {
        'data': data,
        'tests': tests,
        'selected_test_numbers': selected_test_numbers,
        'selected_tests_max_marks': selected_tests_max_marks
    }

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
            
            elif request.user.is_block_user:
               return redirect ('block_dashboard')
            else:
                return redirect('school_add')

        messages.error(request, 'Invalid credentials')
    return render(request, 'school_app/login.html')

def block_dashboard(request):
    if not request.user.is_block_user:
        return render(request, '403.html')
    
    try:
        block = Block.objects.get(admin=request.user)
        schools = School.objects.filter(block=block)
        students = Student.objects.filter(school__in=schools)
        tests = Test.objects.all()
    except Block.DoesNotExist:
        return render(request, '403.html') 
    data = get_block_data(block)  # Assume `block` is an instance of the Block model
    
    # data= (
    #     Test.objects.annotate(
    #         avg_marks=Avg('marks__marks'),
    #         percentage=ExpressionWrapper(
    #             F('avg_marks') * 100 / F('max_marks'),               
    #             output_field=FloatField()),
    #             category_0_33=Count(Case(When(marks__marks__lt=F('max_marks') * 0.33, then=1), output_field=IntegerField())),
    #             category_33_60=Count(Case(When(marks__marks__gte=F('max_marks') * 0.33, marks__marks__lt=F('max_marks')* 0.60, then=1), output_field=IntegerField())),
    #             category_60_80=Count(Case(When(marks__marks__gte=F('max_marks')* 0.60, marks__marks__lt=F('max_marks') * 0.80, then=1), output_field=IntegerField())),
    #             category_80_90=Count(Case(When(marks__marks__gte=F('max_marks')* 0.80, marks__marks__lt=F('max_marks')* 0.90, then=1), output_field=IntegerField())),
    #             category_90_100=Count(Case(When(marks__marks__gte=F('max_marks')* 0.90, marks__marks__lt=F('max_marks'), then=1), output_field=IntegerField())),
    #             category_100=Count(Case(When(marks__marks=F('max_marks') , then=1), output_field=IntegerField()))
    #     ).filter(marks__student__school__block=block)
    #     .values('test_name','subject_name', 'avg_marks', 'percentage', 'category_0_33', 'category_33_60', 'category_60_80', 'category_80_90', 'category_90_100', 'category_100')
    #     .order_by('-percentage')
    # )
# Aggregate category counts for pie chart
    
    # Define the raw SQL query
    sql_query = """    WITH school_avg_marks AS (    SELECT        sch.id AS school_id,        sch.block_id,  -- Add block_id to the selection
        t.test_name,        t.subject_name,        t.max_marks,        AVG(m.marks) AS avg_marks    FROM public.school_app_marks m    JOIN public.school_app_student s ON m.student_id = s.id
    JOIN public.school_app_school sch ON s.school_id = sch.id    JOIN public.school_app_test t ON m.test_id = t.test_number    GROUP BY sch.id, sch.block_id, t.test_name, t.subject_name, t.max_marks  -- Include block_id in the group by
)SELECT     sam.test_name,    sam.subject_name,
    COUNT(DISTINCT CASE WHEN sam.avg_marks < sam.max_marks * 0.33 THEN sam.school_id END) AS category_0_33,
    COUNT(DISTINCT CASE WHEN sam.avg_marks >= sam.max_marks * 0.33 AND sam.avg_marks < sam.max_marks * 0.60 THEN sam.school_id END) AS category_33_60,
    COUNT(DISTINCT CASE WHEN sam.avg_marks >= sam.max_marks * 0.60 AND sam.avg_marks < sam.max_marks * 0.80 THEN sam.school_id END) AS category_60_80,
    COUNT(DISTINCT CASE WHEN sam.avg_marks >= sam.max_marks * 0.80 AND sam.avg_marks < sam.max_marks * 0.90 THEN sam.school_id END) AS category_80_90,
    COUNT(DISTINCT CASE WHEN sam.avg_marks >= sam.max_marks * 0.90 AND sam.avg_marks < sam.max_marks THEN sam.school_id END) AS category_90_100,
    COUNT(DISTINCT CASE WHEN sam.avg_marks = sam.max_marks THEN sam.school_id END) AS category_100 FROM school_avg_marks sam where sam.block_id = %s GROUP BY sam.block_id, sam.test_name, sam.subject_name ORDER BY sam.block_id, sam.test_name;  """
    
    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(sql_query, [block.id])
        result = cursor.fetchall()
    
    # Convert the result into a list of dictionaries for easy access
    result_data = []
    for row in result:
        result_data.append({
            'test_name': row[0],
            'subject_name': row[1],
            'category_0_33': row[2],
            'category_33_60': row[3],
            'category_60_80': row[4],
            'category_80_90': row[5],
            'category_90_100': row[6],
            'category_100': row[7]
        })
    return render(request, 'block_dashboard.html',{
        'data': data,                 
        'result': result_data,
        'total_schools': schools.count(),
        'total_students': students.count(),
        'total_tests': tests.count(),
        'tests': tests,
        'schools': schools,
        'Block_name': block.name_english
        })

def get_block_data(block):
    block_sql_query = """
    WITH student_marks AS (
        SELECT 
            m.student_id, t.test_name, t.subject_name, t.max_marks, 
            COALESCE(m.marks, 0) AS marks, sc.block_id
        FROM school_app_marks m
        JOIN school_app_test t ON m.test_id = t.test_number
        JOIN school_app_student s ON m.student_id = s.id
        JOIN school_app_school sc ON s.school_id = sc.id
        JOIN school_app_block b ON sc.block_id = b.id
        WHERE b.id = %s
    ),
    aggregated_marks AS (
        SELECT
            sm.block_id, sm.test_name, sm.subject_name, sm.max_marks,
            AVG(sm.marks) AS avg_marks,
            (AVG(sm.marks) * 100.0) / sm.max_marks AS percentage,
            SUM(CASE WHEN sm.marks < sm.max_marks * 0.33 THEN 1 ELSE 0 END) AS category_0_33,
            SUM(CASE WHEN sm.marks >= sm.max_marks * 0.33 AND sm.marks < sm.max_marks * 0.60 THEN 1 ELSE 0 END) AS category_33_60,
            SUM(CASE WHEN sm.marks >= sm.max_marks * 0.60 AND sm.marks < sm.max_marks * 0.80 THEN 1 ELSE 0 END) AS category_60_80,
            SUM(CASE WHEN sm.marks >= sm.max_marks * 0.80 AND sm.marks < sm.max_marks * 0.90 THEN 1 ELSE 0 END) AS category_80_90,
            SUM(CASE WHEN sm.marks >= sm.max_marks * 0.90 AND sm.marks < sm.max_marks THEN 1 ELSE 0 END) AS category_90_100,
            SUM(CASE WHEN sm.marks = sm.max_marks THEN 1 ELSE 0 END) AS category_100
        FROM student_marks sm
        GROUP BY sm.block_id, sm.test_name, sm.subject_name, sm.max_marks
    )
    SELECT
        am.block_id, am.test_name, am.subject_name, am.avg_marks, am.percentage,
        am.category_0_33, am.category_33_60, am.category_60_80, am.category_80_90,
        am.category_90_100, am.category_100
    FROM aggregated_marks am
    ORDER BY am.block_id, am.test_name, am.percentage DESC;
    """
    # Execute the query safely with block.id as a parameter
    with connection.cursor() as cursor:
        cursor.execute(block_sql_query, [block.id])  # Pass the block ID safely as a parameter
        result = cursor.fetchall()

    # Convert the result into a list of dictionaries for easy access
    data = []
    for row in result:
        data.append({
            'test_name': row[1],
            'subject_name': row[2],
            'category_0_33': row[5],  # Index adjusted to match the SQL select columns
            'category_33_60': row[6],
            'category_60_80': row[7],
            'category_80_90': row[8],
            'category_90_100': row[9],
            'category_100': row[10],
            'categories': [row[5], row[6], row[7], row[8], row[9], row[10]]  # List of category counts
        })

    return data

# Writtern by Sushil
@login_required
def collector_dashboard(request):
    from django.db.models import Avg, Count, Case, When, F, Value, IntegerField
    from django.db import connection
    # Fetch tests created by the collector
    if not request.user.groups.filter(name='Collector').exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    tests = Test.objects.all()
    # tests = Test.objects.filter(created_by=request.user)

    # Fetch all schools (You can add filters here if necessary)
    schools = School.objects.all()
    live_sessions = Session.objects.filter(expire_date__gte=timezone.now())

    data = (
        Test.objects.annotate(
            avg_marks=Avg('marks__marks'),
            percentage=ExpressionWrapper(
                F('avg_marks') * 100 / F('max_marks'),               
                output_field=FloatField()),
                category_0_33=Count(Case(When(marks__marks__lt=F('max_marks') * 0.33, then=1), output_field=IntegerField())),
                category_33_60=Count(Case(When(marks__marks__gte=F('max_marks') * 0.33, marks__marks__lt=F('max_marks')* 0.60, then=1), output_field=IntegerField())),
                category_60_80=Count(Case(When(marks__marks__gte=F('max_marks')* 0.60, marks__marks__lt=F('max_marks') * 0.80, then=1), output_field=IntegerField())),
                category_80_90=Count(Case(When(marks__marks__gte=F('max_marks')* 0.80, marks__marks__lt=F('max_marks')* 0.90, then=1), output_field=IntegerField())),
                category_90_100=Count(Case(When(marks__marks__gte=F('max_marks')* 0.90, marks__marks__lt=F('max_marks'), then=1), output_field=IntegerField())),
                category_100=Count(Case(When(marks__marks=F('max_marks') , then=1), output_field=IntegerField()))
        )
        .values('test_name','subject_name', 'avg_marks', 'percentage', 'category_0_33', 'category_33_60', 'category_60_80', 'category_80_90', 'category_90_100', 'category_100')
        .order_by('-percentage')
    )
# Aggregate category counts for pie chart
    for entry in data:
        entry['categories'] = [
            entry['category_0_33'],
            entry['category_33_60'],
            entry['category_60_80'],
            entry['category_80_90'],
            entry['category_90_100'],
            entry['category_100']
        ]
    # Define the raw SQL query
    sql_query = """
    WITH school_avg_marks AS (SELECT
            sch.id AS school_id, t.test_name, t.subject_name, t.max_marks, AVG(m.marks) AS avg_marks
        FROM  public.school_app_marks m
        JOIN  public.school_app_student s ON m.student_id = s.id         JOIN  public.school_app_school sch ON s.school_id = sch.id
        JOIN  public.school_app_test t ON m.test_id = t.test_number        GROUP BY    sch.id, t.test_name, t.subject_name, t.max_marks
    )
    SELECT         test_name,        subject_name,
        COUNT(DISTINCT CASE WHEN avg_marks < max_marks * 0.33 THEN school_id END) AS category_0_33,
        COUNT(DISTINCT CASE WHEN avg_marks >= max_marks * 0.33 AND avg_marks < max_marks * 0.60 THEN school_id END) AS category_33_60,
        COUNT(DISTINCT CASE WHEN avg_marks >= max_marks * 0.60 AND avg_marks < max_marks * 0.80 THEN school_id END) AS category_60_80,
        COUNT(DISTINCT CASE WHEN avg_marks >= max_marks * 0.80 AND avg_marks < max_marks * 0.90 THEN school_id END) AS category_80_90,
        COUNT(DISTINCT CASE WHEN avg_marks >= max_marks * 0.90 AND avg_marks < max_marks THEN school_id END) AS category_90_100,
        COUNT(DISTINCT CASE WHEN avg_marks = max_marks THEN school_id END) AS category_100
    FROM         school_avg_marks    GROUP BY   test_name, subject_name    ORDER BY   test_name;  """
    
    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        result = cursor.fetchall()
    
    # Convert the result into a list of dictionaries for easy access
    result_data = []
    for row in result:
        result_data.append({
            'test_name': row[0],
            'subject_name': row[1],
            'category_0_33': row[2],
            'category_33_60': row[3],
            'category_60_80': row[4],
            'category_80_90': row[5],
            'category_90_100': row[6],
            'category_100': row[7]
        })
    
    return render(request, 'school_app/collector_dashboard.html', {
        'tests': tests,
        'schools': schools,
        'total_schools': School.objects.count(),
        'total_students': Student.objects.count(),
        'total_tests': Test.objects.count(),
        'get_active_users': live_sessions.count(),
        'data': data,
        'result': result_data
    })

@login_required
# def view_test_results(request, test_number):
#     test = get_object_or_404(Test, test_number=test_number)
#     results = Marks.objects.filter(test_id=test_number).select_related('student')

#     # Get sorting parameters
#     sort_by = request.GET.get('sort_by', 'student__name')  # Default sorting by student name
#     order = request.GET.get('order', 'asc')  # Default order is ascending

#     # Adjust the ordering
#     if order == 'desc':
#         sort_by = f"-{sort_by}"
    
#     results = results.order_by(sort_by)

#     context = {
#         'test': test,
#         'results': results,
#         'current_sort_by': request.GET.get('sort_by', 'student__name'),
#         'current_order': request.GET.get('order', 'asc'),
#     }
#     return render(request, 'school_app/test_results.html', context)
def view_test_results(request, test_number):
    test = get_object_or_404(Test, test_number=test_number)
    
    # Check user role
    if request.user.is_block_user:
        # If user is a block user, get the block and filter results accordingly
        block = Block.objects.get(admin=request.user)
        schools = School.objects.filter(block=block)
    elif request.user.is_district_user:
        # If user is a district user, get the district and filter results accordingly
        
        schools = School.objects.all()

    elif request.user.is_school_user:
        # If user is a district user, get the district and filter results accordingly        
        schools = School.objects.filter(admin=request.user)
    else:
        # If the user is neither a block nor district user, show an error or default behavior
        return render(request, '403.html')  # Or redirect to an appropriate page

    # Get results for schools related to the block or district
    results = Marks.objects.filter(test_id=test_number, student__school__in=schools).select_related('student')

    # Get sorting parameters
    sort_by = request.GET.get('sort_by', 'student__name')  # Default sorting by student name
    order = request.GET.get('order', 'asc')  # Default order is ascending

    # Adjust the ordering
    if order == 'desc':
        sort_by = f"-{sort_by}"
    
    # Apply the sorting to the results
    results = results.order_by(sort_by)

    # Pass the context to the template
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
def student_ranking(request):
    selected_test = request.GET.get('test', None)

    rankings = []

    if request.user.is_district_user:
        if selected_test:
            # Ranking for a specific test
            rankings = (
                Marks.objects.filter(test__test_number=selected_test)
                .select_related('student', 'student__school', 'test')
                .annotate(
                    percentage=ExpressionWrapper(
                        F('marks') * 100 / F('test__max_marks'),
                        output_field=FloatField()
                    )
                )
                .values(
                    'student__id', 'student__name', 'student__school__name', 
                    'marks', 'percentage', 'test__test_name'
                )
                .order_by('-marks')
            )
        else:
            # Cumulative ranking for district user (all tests)
            rankings = (
                Marks.objects
                .select_related('student', 'student__school')
                .values('student__id', 'student__name', 'student__school__name')
                .annotate(
                    total_marks=Sum('marks'),
                    total_max_marks=Sum('test__max_marks'),
                    percentage=ExpressionWrapper(
                        (Sum('marks') * 100.0) / Sum('test__max_marks'),
                        output_field=FloatField()
                    )
                )
                .order_by('-total_marks')
            )

    elif request.user.is_block_user:
        block = Block.objects.get(admin=request.user)
        schools_in_block = School.objects.filter(block=block)
        students_in_block = Student.objects.filter(school__in=schools_in_block)

        if selected_test:
            # Ranking for a specific test within a block
            rankings = (
                Marks.objects.filter(student__in=students_in_block, test__test_number=selected_test)
                .select_related('student', 'student__school', 'test')
                .annotate(
                    percentage=ExpressionWrapper(
                        F('marks') * 100 / F('test__max_marks'),
                        output_field=FloatField()
                    )
                )
                .values(
                    'student__id', 'student__name', 'student__school__name', 
                    'marks', 'percentage', 'test__test_name'
                )
                .order_by('-marks')
            )
        else:
            # Cumulative ranking for block user (all tests)
            rankings = (
                Marks.objects.filter(student__in=students_in_block)
                .select_related('student', 'student__school')
                .values('student__id', 'student__name', 'student__school__name')
                .annotate(
                    total_marks=Sum('marks'),
                    total_max_marks=Sum('test__max_marks'),
                    percentage=ExpressionWrapper(
                        (Sum('marks') * 100.0) / Sum('test__max_marks'),
                        output_field=FloatField()
                    )
                )
                .order_by('-total_marks')
            )

    else:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Get all tests for the dropdown
    tests = Test.objects.all()

    return render(request, 'student_ranking.html', {
        'rankings': rankings,
        'tests': tests,
        'selected_test': selected_test
    })
@login_required
def student_report(request):
   
    # if not request.user.groups.filter(name='Collector').exists():
    #     return HttpResponseForbidden("You are not authorized to access this page.")
    # if not request.user.groups.filter(name='Collector').exists():
    #     return HttpResponseForbidden("You are not authorized to access this page.")
   
    if request.user.is_district_user:
         total_students = Student.objects.count()
    else:
        block = Block.objects.get(admin=request.user)
        schools = School.objects.all().filter(block=block)
        # Count students from all schools within the block
        students = Student.objects.filter(school__in=schools)
        total_students = students.count()

    #total_students = Student.objects.count()
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
    from django.db.models import Count, F, ExpressionWrapper, FloatField, Case, When
    if request.user.is_system_admin:
        return redirect('system_admin_dashboard')
    
    try:
        school = School.objects.get(admin=request.user)
        active_tests = Test.objects.filter(is_active=True)  # Fetch only active tests
        data = (
        Test.objects.annotate(
            avg_marks=Avg('marks__marks'),
            percentage=ExpressionWrapper(
                F('avg_marks') * 100 / F('max_marks'),               
                output_field=FloatField()),
                category_0_33=Count(Case(When(marks__marks__lt=F('max_marks') * 0.33, then=1), output_field=IntegerField())),
                category_33_60=Count(Case(When(marks__marks__gte=F('max_marks') * 0.33, marks__marks__lt=F('max_marks')* 0.60, then=1), output_field=IntegerField())),
                category_60_80=Count(Case(When(marks__marks__gte=F('max_marks')* 0.60, marks__marks__lt=F('max_marks') * 0.80, then=1), output_field=IntegerField())),
                category_80_90=Count(Case(When(marks__marks__gte=F('max_marks')* 0.80, marks__marks__lt=F('max_marks')* 0.90, then=1), output_field=IntegerField())),
                category_90_100=Count(Case(When(marks__marks__gte=F('max_marks')* 0.90, marks__marks__lt=F('max_marks'), then=1), output_field=IntegerField())),
                category_100=Count(Case(When(marks__marks=F('max_marks') , then=1), output_field=IntegerField()))
        )
        .values('test_name','subject_name', 'avg_marks', 'percentage', 'category_0_33', 'category_33_60', 'category_60_80', 'category_80_90', 'category_90_100', 'category_100')
        .order_by('-percentage')
       )
       # Aggregate category counts for pie chart
        for entry in data:
         entry['categories'] = [
            entry['category_0_33'],
            entry['category_33_60'],
            entry['category_60_80'],
            entry['category_80_90'],
            entry['category_90_100'],
            entry['category_100']
        ]
        result = (Marks.objects
              .filter(student__school_id=school.id)
              .values('test__test_name', 'test__subject_name', 'test__max_marks')
              .annotate(
                  avg_marks=Avg('marks'),
                  percentage=ExpressionWrapper(Avg('marks') / F('test__max_marks') * 100, output_field=FloatField()),
                  category_0_33_1=Count(Case(When(marks__lt=F('test__max_marks') * 0.33, then=1))),
                  category_33_60_1=Count(Case(When(marks__gte=F('test__max_marks') * 0.33, marks__lt=F('test__max_marks') * 0.60, then=1))),
                  category_60_80_1=Count(Case(When(marks__gte=F('test__max_marks') * 0.60, marks__lt=F('test__max_marks') * 0.80, then=1))),
                  category_80_90_1=Count(Case(When(marks__gte=F('test__max_marks') * 0.80, marks__lt=F('test__max_marks') * 0.90, then=1))),
                  category_90_100_1=Count(Case(When(marks__gte=F('test__max_marks') * 0.90, marks__lt=F('test__max_marks'), then=1))),
                  category_100_1=Count(Case(When(marks=F('test__max_marks'), then=1)))
              )
              .order_by('-percentage')
              )
    
        labels = [item['test__test_name'] for item in result]
        percentages = [item['percentage'] for item in result]
        category_0_33 = [item['category_0_33_1'] for item in result]
        category_33_60 = [item['category_33_60_1'] for item in result]
        category_60_80 = [item['category_60_80_1'] for item in result]
        category_80_90 = [item['category_80_90_1'] for item in result]
        category_90_100 = [item['category_90_100_1'] for item in result]
        category_100 = [item['category_100_1'] for item in result]

        query = """    SELECT se.school_name_with_nic_code, s.nic_code, 
        se.school_nic_code, se.session_year, se.total_students, se.passed_students, 
        se.first_division_students, se.overall_exam_result, se.math_exam_result, se.math_above_80, 
        se.math_above_90, se.math_100_percent     FROM student_exam_results se     INNER JOIN 
        school_app_school s      ON    se.school_nic_code = s.nic_code  WHERE s.nic_code =%s    """
        with connection.cursor() as cursor:
         cursor.execute(query,[school.nic_code])
         result = cursor.fetchall()
        # Convert result to a list of dictionaries
        results_dict = [
        {
            'school_name_with_nic_code': row[0],
            'nic_code': row[1],
            'school_nic_code': row[2],
            'session_year': row[3],
            'total_students': row[4],
            'passed_students': row[5],
            'first_division_students': row[6],
            'overall_exam_result': row[7],
            'math_exam_result': row[8],
            'math_above_80': row[9],
            'math_above_90': row[10],
            'math_100_percent': row[11]
        }
        for row in result
    ]
        
        context = {
            'school': school,
            'student_count': Student.objects.filter(school=school).count(),
            'active_tests': active_tests,
            'data': data,
            'labels': labels,
            'percentages': percentages,
            'category_0_33': category_0_33,
            'category_33_60': category_33_60,
            'category_60_80': category_60_80,
            'category_80_90': category_80_90,
            'category_90_100': category_90_100,
            'category_100': category_100,
            'results': results_dict,
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
    if request.user.is_block_user:
        block = Block.objects.get(admin=request.user)
        schools = School.objects.all().filter(block=block)
    else:
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
                    print(f"Error generating questions: {e}")
                    messages.error(request, f"Error generating questions: {str(e)}")
                    return redirect('login')

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
        print(f"Unexpected error: {e}")
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('login')

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
