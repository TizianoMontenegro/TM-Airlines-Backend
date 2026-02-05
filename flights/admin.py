from django.contrib import admin
from .models import Airport, Flight

# Register your models here.
@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("code", "city", "country")
    search_fields = ("code", "city", "country")
    ordering = ("code",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "flight_number",
        "origin",
        "destination",
        "departure_time",
        "arrival_time",
        "status",
    )

    list_filter = ("status", "origin", "destination")
    search_fields = ("flight_number",)
    ordering = ("departure_time",)
