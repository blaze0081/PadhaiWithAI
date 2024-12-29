from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, School, Student, Marks, TestPaper
from django.utils.html import format_html


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_system_admin')
    list_filter = ('is_staff', 'is_system_admin')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_system_admin', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_system_admin', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'created_by', 'created_at')
    search_fields = ('name', 'admin__email')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'class_name', 'school')
    list_filter = ('school', 'class_name')  
    search_fields = ('name', 'roll_number')

class MarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'test_number', 'marks', 'date')
    list_filter = ('test_number', 'date')
    search_fields = ('student__name', 'test_number')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Marks, MarksAdmin)

@admin.register(TestPaper)
class TestPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'class_level', 'uploaded_by', 'uploaded_at', 'download_links')
    list_filter = ('subject', 'class_level', 'uploaded_at')
    search_fields = ('title', 'uploaded_by__username')
    readonly_fields = ('uploaded_at',)

    def download_links(self, obj):
        question_paper_link = ''
        answer_key_link = ''
        
        if obj.question_paper:
            question_paper_link = f'<a class="button" href="{obj.question_paper.url}" target="_blank">Question Paper</a>'
        
        if obj.answer_key:
            answer_key_link = f'<a class="button" href="{obj.answer_key.url}" target="_blank">Answer Key</a>'
        
        return format_html(f'{question_paper_link} {answer_key_link}')
    
    download_links.short_description = 'Downloads'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
