from django.contrib import admin
from .models import Booking

# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "user",
        "flight",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("code", "user__username", "user__email")
    ordering = ("-created_at",)
