# main/admin.py

from django.contrib import admin
from .models import CustomUser, Profile, LoginMethod
from .forms import CustomLoginForm
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'birth_date')
    readonly_fields = ('user',)

@admin.register(LoginMethod)
class LoginMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_type', 'identifier')
    list_filter = ('login_type',)
    
admin.site.login_form = CustomLoginForm