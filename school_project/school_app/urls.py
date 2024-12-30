from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('marks/', views.marks_list, name='marks_list'),
    path('marks/add/', views.marks_add, name='marks_add'),
    path('logout/', views.logout_view, name='logout'),
    path('school/add/', views.school_add, name='school_add'),
    path('students/<int:student_id>/edit/', views.student_edit, name='student_edit'),
    path('marks/<int:marks_id>/edit/', views.marks_edit, name='marks_edit'),
    path('analysis-dashboard/', views.analysis_dashboard, name='analysis_dashboard'),
    path('analysis-data/', views.analysis_dashboard, name='analysis_data'),


    
    # Math Tools URLs
    path('math-tools/', views.math_tools, name='math_tools'),
    path('math-tools/solve/', views.solve_math, name='solve_math'),
    path('math-tools/generate/', views.generate_math, name='generate_math'),
    path('math-tools/load-questions/', views.load_questions, name='load_questions'),
    
    # System Administrator URLs
    path('system-admin/dashboard/', views.system_admin_dashboard, name='system_admin_dashboard'),
    path('system-admin/schools/', views.system_admin_school_list, name='system_admin_school_list'),
    path('system-admin/schools/add/', views.system_admin_school_add, name='system_admin_school_add'),
    path('system-admin/students/', views.system_admin_student_list, name='system_admin_student_list'),
    path('system-admin/students/<int:school_id>/', views.system_admin_student_list, name='system_admin_school_students'),
    path('system-admin/marks/', views.system_admin_marks_list, name='system_admin_marks_list'),
    path('system-admin/marks/<int:school_id>/', views.system_admin_marks_list, name='system_admin_school_marks'),

    path('get-chapters/<str:book_id>/', views.get_chapters, name='get_chapters'),
    path('math-tools/generate-form/', views.generate_form, name='generate_form'),

    # Collector's Dashboard
    path('collector-dashboard/', views.collector_dashboard, name='collector_dashboard'),
    path('add-test/', views.add_test, name='add_test'),
  # Test Activation and Deactivation
    path('activate-test/<int:test_id>/', views.activate_test, name='activate_test'),
    path('deactivate/<int:test_id>/', views.deactivate_test, name='deactivate_test'),
    path('test-results/<int:test_number>/', views.view_test_results, name='view_test_results'),


]

