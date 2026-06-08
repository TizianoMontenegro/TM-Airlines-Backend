from django.db import models

# Create your models here.
class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ("code",)
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["country"]),
        ]


class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("cancelled", "Cancelled"),
        ("departed", "Departed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.flight_number

    class Meta:
        ordering = ("departure_time",)
        indexes = [
            models.Index(fields=["flight_number"]),
            models.Index(fields=["departure_time"]),
            models.Index(fields=["status"]),
            models.Index(fields=["origin"]),
            models.Index(fields=["destination"]),
        ]