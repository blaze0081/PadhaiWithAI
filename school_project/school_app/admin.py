from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, School, Student, Marks,Attendance,Block, District
from django.contrib.auth.models import Group
from .models import Test
from django.utils.html import format_html

# Customizing the Test model in the admin interface
class TestAdmin(admin.ModelAdmin):
    # Define the fields to display in the list view
    list_display = ['test_number', 'test_name', 'subject_name', 'test_date', 'is_active', 'created_by', 'created_at', 'max_marks']
    
    # Add filters on the admin page for certain fields
    list_filter = ['is_active', 'test_date', 'subject_name', 'created_by']
    
    # Add search functionality for specific fields
    search_fields = ['test_name', 'subject_name', 'created_by__username']  # Allow searching by name, subject, and creator's username
    
    # Make the test date field a nice format in the list view
    date_hierarchy = 'test_date'
    
    # Optionally, you can add custom actions to the admin panel
    actions = ['make_active', 'make_inactive']
    
    # Custom action: Make selected tests active
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} tests marked as active.")
    make_active.short_description = "Mark selected tests as Active"
    
    # Custom action: Make selected tests inactive
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} tests marked as inactive.")
    make_inactive.short_description = "Mark selected tests as Inactive"

    # Customize the form layout and include file fields for PDF uploads
    fieldsets = (
        (None, {
            'fields': ('test_name', 'subject_name', 'test_date', 'pdf_file_questions', 'pdf_file_answers', 'is_active')
        }),
        ('Creator Info', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',),
        }),
    )
    
    # Optional: Add file preview for uploaded PDFs (using format_html to generate clickable links)
    def pdf_file_questions_preview(self, obj):
        if obj.pdf_file_questions:
            return format_html('<a href="{}" target="_blank">View Question PDF</a>', obj.pdf_file_questions.url)
        return "No file"
    pdf_file_questions_preview.short_description = 'Question PDF'

    def pdf_file_answers_preview(self, obj):
        if obj.pdf_file_answers:
            return format_html('<a href="{}" target="_blank">View Answer PDF</a>', obj.pdf_file_answers.url)
        return "No file"
    pdf_file_answers_preview.short_description = 'Answer PDF'

    # Add the preview to the list display
    list_display = ['test_number', 'test_name', 'subject_name', 'test_date', 'is_active', 'created_by', 'created_at', 'pdf_file_questions_preview', 'pdf_file_answers_preview']

# Register the Test model with the customized admin interface
admin.site.register(Test, TestAdmin)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_system_admin','is_district_user', 'is_block_user', 'is_school_user')
    list_filter = ('is_staff', 'is_system_admin','is_district_user', 'is_block_user', 'is_school_user')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {
            'fields': ('is_staff', 'is_system_admin', 'is_active', 'groups', 'user_permissions','is_district_user', 'is_block_user', 'is_school_user')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_system_admin', 'is_active','is_district_user', 'is_block_user', 'is_school_user')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

# Register the other models as they are
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'created_by', 'created_at')
    search_fields = ('name', 'admin__email')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'class_name', 'school')
    list_filter = ('school', 'class_name')  
    search_fields = ('name', 'roll_number')

class MarksAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'test', 'marks', 'date')  # Removed 'test_number'
    list_filter = ('test', 'student')  # Removed 'test_number'
    search_fields = ('student__name', 'test__test_name')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'is_present')
    list_filter = ('date', 'is_present')
    search_fields = ('student__name',)

class BlockAdmin(admin.ModelAdmin):
    list_display = ('name_english', 'name_hindi')
    search_fields = ('name_english', 'name_hindi')  # You can also search by district name
    #list_filter = ('district',)  # Filter blocks by district in the admin panel
    #ordering = ('name_english',)  # Default ordering by the English name

admin.site.register(Block, BlockAdmin)

admin.site.register(Attendance, AttendanceAdmin)
# Register models with updated admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Marks, MarksAdmin)

# admin.site.register(Group)  # Ensure the Group model is registered

#collector_group, created = Group.objects.get_or_create(name='Collector')

admin.site.site_header = 'PadhaiwithAI'
admin.site.site_title = 'PadhaiwithAI'