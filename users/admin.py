# users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm, ProjectCAMCreationForm, ProjectCreationForm
from .models import CustomUser, CAM, Project

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    list_display = [field.name for field in CustomUser._meta.fields if field.name!='password']
    list_filter = ("last_login", "date_joined")
    fields = [field.name for field in CustomUserChangeForm.Meta.fields]


@admin.register(CAM)
class CAMAdmin(admin.ModelAdmin):
    add_form = ProjectCAMCreationForm
    list_display = [field.name for field in CAM._meta.fields]
    #list_filter = ("last_login", "date_joined")
    fields = [field for field in ProjectCAMCreationForm.Meta.fields]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    add_form = ProjectCreationForm
    list_display = [field.name for field in Project._meta.fields]
    #list_filter = ("last_login", "date_joined")
    fields = [field for field in ProjectCreationForm.Meta.fields]
