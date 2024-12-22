from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import School, Student, Marks, CustomUser
from .forms import StudentForm, MarksForm, SchoolForm, SchoolAdminRegistrationForm
from django.db.models import Count
from .math_utils import solve_math_problem, generate_similar_questions
import json
import os
from django.conf import settings
from django.http import JsonResponse


def is_system_admin(user):
    return user.is_authenticated and user.is_system_admin

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_system_admin:
                return redirect('system_admin_dashboard')
            elif School.objects.filter(admin=user).exists():
                return redirect('dashboard')
            else:
                return redirect('school_add')
        messages.error(request, 'Invalid credentials')
    return render(request, 'school_app/login.html')

@login_required
def dashboard(request):
    if request.user.is_system_admin:
        return redirect('system_admin_dashboard')
    
    try:
        school = School.objects.get(admin=request.user)
        context = {
            'school': school,
            'student_count': Student.objects.filter(school=school).count(),
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
    marks = Marks.objects.filter(student__school=school)
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

def logout_view(request):
    logout(request)
    return redirect('login')

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

@login_required
def solve_math(request):
    if request.method == 'POST':
        try:
            # Get questions from POST data
            questions_json = request.POST.get('questions')
            if not questions_json:
                messages.error(request, 'No questions selected')
                return redirect('math_tools')

            # Parse the JSON string to get list of questions
            questions = json.loads(questions_json)
            
            # Solve each question
            solutions = []
            for question in questions:
                solution = solve_math_problem(question)
                solutions.append({
                    'question': question,
                    'solution': solution
                })

            context = {
                'solutions': solutions,
                # Store original state in context
                'original_book': request.session.get('selected_book'),
                'original_chapter': request.session.get('selected_chapter')
            }

            return render(request, 'school_app/solutions.html', context)
            
        except json.JSONDecodeError:
            messages.error(request, 'Invalid question data received')
        except Exception as e:
            messages.error(request, f'Error solving questions: {str(e)}')
    
    return redirect('math_tools')

@login_required
def generate_math(request):
    generated_questions = None
    if request.method == 'POST':
        base_question = request.POST.get('base_question')
        difficulty = request.POST.get('difficulty')
        num_questions = int(request.POST.get('num_questions', 5))
        if base_question:
            generated_questions = generate_similar_questions(
                base_question, 
                difficulty,
                num_questions
            )
    return render(request, 'school_app/math_tools.html', {'generated_questions': generated_questions})


@login_required
def get_chapters(request, book_id):
    try:
        chapters = get_book_chapters(book_id)
        return JsonResponse({'chapters': chapters})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)