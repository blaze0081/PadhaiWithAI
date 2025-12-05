from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
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
    path('api/students/', views.get_students, name='get_students'),
    path('api/student-analysis/<int:student_id>/', views.get_student_analysis, name='get_student_analysis'),
    path('captcha/', include('captcha.urls')),


    
    # Math Tools URLs
    path('math-tools/', views.math_tools, name='math_tools'),
    path('math-tools/solve/', views.solve_math, name='solve_math'),
    path('math-tools/solve-again/', views.solve_again, name='solve_again'),
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

    path('student-ranking/', views.student_ranking, name='student_ranking'),
    path('student-report/', views.student_report, name='student_report'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('delete_student_mark/<int:mark_id>/', views.delete_student_mark, name='delete_student_mark'),
    path('update-marks/<int:mark_id>/', views.update_marks, name='update_marks'),
    #31/12/2024
    path('active_test_list', views.active_test_list, name='active_test_list'),
    path('test/<int:test_id>/marks/', views.test_marks_entry, name='test_marks_entry'),
    path('test/<int:test_id>/marks/delete/<int:student_id>/', views.delete_marks, name='delete_marks'),
    path('studentslist/', views.school_student_list, name='school_student_list'),

    #01/01/2025

    path('school/average/', views.school_average_marks, name='school_average_marks'),
    path('students/top/', views.top_students, name='top_students'),
    path('students/weakest/', views.weakest_students, name='weakest_students'),
     path('upload-users/', views.upload_school_users, name='upload_school_users'),
    path('user/change-password/', views.password_change, name='change_password'),
    path('upload-student-data/', views.upload_student_data, name='upload_student_data'),
    #08/01/2025 Sushil Agrawal NIC TONK
    path('school/report/', views.school_report, name='school_report'),


    path('report/schools-without-students/', views.schools_without_students, name='schools_without_students'),
    path('report/inactive-schools/', views.inactive_schools, name='inactive_schools'),
    path('report/schools-with-test-counts/', views.schools_with_test_counts, name='schools_with_test_counts'),
    path('report/schools-without-tests/', views.schools_without_tests, name='schools_without_tests'),
    path('report/schools-with-student-counts/', views.schools_with_student_counts, name='schools_with_student_counts'),
    path('report/school/', views.report_dashboard, name='report_dashboard'),
    path('update-block-name/', views.update_block_name_from_excel, name='update_block_name'),
    path('test-average/', views.test_wise_average_marks, name='test_wise_average'),

    path('attendance/submit/', views.submit_attendance, name='submit_attendance'),
    path('attendance/summary/', views.attendance_summary, name='attendance_summary'),
    path('test-results-analysis/', views.test_results_analysis, name='test_results_analysis'),

        
    path('attendance/date-wise-summary/',views.date_wise_attendance_summary, name='date_wise_attendance_summary'),
    path('attendance/district-wise-summary/', views.district_wise_attendance_summary, name='district_wise_attendance_summary'),
    path('attendance/block-wise-summary/', views.block_wise_attendance_summary, name='block_wise_attendance_summary'),
  
    
    path('attendance/school-daily-summary/', views.school_daily_attendance_summary, name='school_daily_attendance_summary'),
    path('block-attendance-report/', views.block_attendance_report, name='block_attendance_report'),
    path('block-dashboard/', views.block_dashboard, name='block_dashboard'),
     #17102025
    path("ask-pai/", views.ask_pai, name="ask-pai"),
    path("chat/", views.chat_view, name="chat_page"),
]

