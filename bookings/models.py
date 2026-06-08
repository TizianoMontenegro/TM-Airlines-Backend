from django.db import models
from django.conf import settings
from flights.models import Flight

# Create your models here.

class Booking(models.Model):
    code = models.CharField(max_length=8, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]