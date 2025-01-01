from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import School, Student, Marks
from .forms import StudentForm, MarksForm, SchoolForm, SchoolAdminRegistrationForm, TestForm, Test
from django.db.models import Count
from .math_utils import solve_math_problem, generate_similar_questions
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

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(request, email=email, password=password)
#         if user is not None:
#             login(request, user)
#             if user.is_system_admin:
#                 return redirect('system_admin_dashboard')
#             elif School.objects.filter(admin=user).exists():
#                 return redirect('dashboard')
#             else:
#                 return redirect('school_add')
#         messages.error(request, 'Invalid credentials')
#     return render(request, 'school_app/login.html')

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

    return render(request, 'school_app/collector_dashboard.html', {
        'tests': tests,
        'schools': schools
    })

@login_required
def view_test_results(request, test_number):
    test = get_object_or_404(Test, test_number=test_number)
    results = Marks.objects.filter(test_number=test_number).select_related('student')

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
def student_ranking(request):
    # Student ranking
     if not request.user.groups.filter(name='Collector').exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
     rankings = Marks.objects.select_related('student', 'student__school').order_by('-marks')
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
# @login_required
# def dashboard(request):
#     if request.user.is_system_admin:
#         return redirect('system_admin_dashboard')
    
#     try:
#         school = School.objects.get(admin=request.user)
#         context = {
#             'school': school,
#             'student_count': Student.objects.filter(school=school).count(),
#         }
#     except School.DoesNotExist:
#         messages.error(request, "No school found for the current user.")
#         return redirect('login')

#     return render(request, 'school_app/system_admin_dashboard.html', context)

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
    #students = Student.objects.all()
    
    if request.method == 'POST':
        for student in students:
            marks_value = request.POST.get(f'marks_{student.id}', '').strip()
            if marks_value:  # Ensure marks are not empty
                try:
                    # Validate numeric marks
                    marks_value = float(marks_value)
                    mark, created = Marks.objects.get_or_create(student=student, test=test)
                    mark.marks = marks_value
                    mark.save()
                except InvalidOperation:
                    return render(request, 'test_marks_entry.html', {
                        'test': test,
                        'student_marks': [
                            {'student': s, 'marks': Marks.objects.filter(student=s, test=test).first().marks if Marks.objects.filter(student=s, test=test).first() else ''}
                            for s in students
                        ],
                        'error': f"Invalid marks entered for {student.name}. Please enter a valid number."
                    })
                except ValueError:
                    return render(request, 'test_marks_entry.html', {
                        'test': test,
                        'student_marks': [
                            {'student': s, 'marks': Marks.objects.filter(student=s, test=test).first().marks if Marks.objects.filter(student=s, test=test).first() else ''}
                            for s in students
                        ],
                        'error': f"Invalid marks entered for {student.name}. Please enter a valid number."
                    })
                except IntegrityError:
                    return render(request, 'test_marks_entry.html', {
                        'test': test,
                        'student_marks': [
                            {'student': s, 'marks': Marks.objects.filter(student=s, test=test).first().marks if Marks.objects.filter(student=s, test=test).first() else ''}
                            for s in students
                        ],
                        'error': f"Failed to save marks for {student.name}. Please try again."
                    })
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
    mark = get_object_or_404(Marks, student_id=student_id, test_id=test_id)
    mark.delete()
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

@login_required
def solve_math(request):
    if request.method == 'POST':
        try:
            # Get questions and book ID from POST data
            questions_json = request.POST.get('questions')
            book_id = request.session.get('selected_book')
            
            print("Received questions_json:", questions_json)  # Debug print
            
            if not questions_json:
                messages.error(request, 'No questions selected')
                return redirect('math_tools')

            # Get the book's language
            language = get_book_language(book_id)

            # Parse the JSON string to get list of questions
            questions = json.loads(questions_json)
            print("Parsed questions:", questions)  # Debug print
            
            # If questions is a string, try to parse it again
            if isinstance(questions, str):
                try:
                    questions = json.loads(questions)
                    print("Re-parsed questions:", questions)  # Debug print
                except json.JSONDecodeError:
                    pass

            solutions = []

            # Convert questions to list if it's not already
            if not isinstance(questions, list):
                questions = [questions]

            # Solve each question in the appropriate language
            for question_data in questions:
                print("Processing question_data:", question_data)  # Debug print
                print("Type of question_data:", type(question_data))  # Debug print
                
                # If question_data is a string, try to parse it as JSON
                if isinstance(question_data, str):
                    try:
                        question_data = json.loads(question_data)
                        print("Parsed question_data:", question_data)  # Debug print
                    except json.JSONDecodeError:
                        pass

                if isinstance(question_data, dict):
                    print("Processing as dict")  # Debug print
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
                        print(f"Looking for image at: {img_path}")  # Debug print
                        print(f"Does file exist? {os.path.exists(img_path)}")  # Debug print
                        
                        if os.path.exists(img_path):
                            solution = solve_math_problem(
                                question=question,
                                image_path=img_path,
                                language=language
                            )
                        else:
                            print(f"Warning: Image not found at {img_path}")
                            solution = solve_math_problem(question=question, language=language)
                    else:
                        solution = solve_math_problem(question=question, language=language)
                else:
                    print("Processing as string")  # Debug print
                    question = question_data
                    solution = solve_math_problem(question=question, language=language)
                
                # For template display, use the static URL path for images
                static_img_url = img_filename if 'img_filename' in locals() else None
                
                solutions.append({
                    'question': question if 'question' in locals() else question_data,
                    'img': static_img_url,
                    'solution': solution
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
                    generated_content = generate_similar_questions(
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

            context = {
                'generated_questions': combined_content,
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
    # Only allow school admins to access this view
    if not hasattr(request.user, 'administered_school'):
        raise PermissionDenied
    
    school = request.user.administered_school
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX requests for chart data
        class_name = request.GET.get('class_name')
        student_id = request.GET.get('student_id')
        
        # Base query for students in this school
        students = Student.objects.filter(school=school)
        
        if class_name:
            students = students.filter(class_name=class_name)
            
        marks_data = Marks.objects.filter(student__in=students)
        
        # If student_id is provided, get their specific marks
        student_progress = []
        if student_id:
            student_progress = list(Marks.objects.filter(
                student_id=student_id
            ).values('test_number', 'marks', 'date').order_by('date'))
        
        analysis_data = {
            'student_progress': student_progress,
            'class_performance': list(marks_data.filter(
                student__class_name=class_name
            ).values('test_number').annotate(
                average=Avg('marks'),
                max_mark=Max('marks'),
                min_mark=Min('marks')
            ).order_by('test_number')) if class_name else [],
            
            'students': list(students.values('id', 'name', 'roll_number'))
        }
        
        return JsonResponse(analysis_data)
    
    # Convert CLASS_CHOICES tuple into list for the template
    class_choices = list(Student.CLASS_CHOICES)
    
    # Initial page load context
    context = {
        'school': school,
        'class_choices': class_choices
    }
    return render(request, 'school_app/analysis_dashboard.html', context)