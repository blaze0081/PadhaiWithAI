from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, School, Student, Marks

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