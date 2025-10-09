from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from comptes.models import User

class CustomUserAdmin(UserAdmin):
    model = User
    
    # Champs affichés dans la liste
    list_display = ['email', 'full_name', 'first_name', 'last_name', 'account_tier', 'is_active']
    list_filter = ['is_active', 'account_tier']
    
    # Organisation des champs
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('full_name', 'first_name', 'last_name', 'headline', 'profile_image')}),
        ('Contact', {'fields': ('phone_number', 'mobile_phone', 'linkedin_url', 'github_url', 'country', 'state', 'city')}),
        ('Préférences', {'fields': ('timezone', 'language')}),
        ('Abonnement', {'fields': ('account_tier', 'subscription_end_date', 'cv_limit')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    # Champs lors de l'ajout d'un nouvel utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    search_fields = ['email', 'full_name', 'first_name', 'last_name']
    ordering = ['email']

admin.site.register(User, CustomUserAdmin)