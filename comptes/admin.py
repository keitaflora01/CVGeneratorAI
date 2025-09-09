from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from comptes.models import User

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'full_name', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )
    search_fields = ['email', 'full_name']
    ordering = ['email']
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, CustomUserAdmin)