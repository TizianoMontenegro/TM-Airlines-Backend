from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User

    list_display = (
        "id",
        "username",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = ("is_staff", "is_active")

    search_fields = ("username", "email")

    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        ("Preferences", {"fields": ("language",)}),
    )