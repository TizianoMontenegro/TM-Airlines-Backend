# AGENTS.md - Developer Guidelines for tm-airlines-backend

This document provides guidelines for AI agents working on this Django REST API project.

## Project Overview

- **Framework**: Django 4.x with Django REST Framework
- **Database**: SQLite (local) / PostgreSQL (production)
- **Authentication**: JWT via djangorestframework-simplejwt
- **Python Version**: 3.10+

## Commands

> **Note**: If `python` resolves to a system interpreter instead of the venv, use `venv\Scripts\python.exe` or activate the venv first: `venv\Scripts\Activate.ps1`

### Running the Server
```bash
python manage.py runserver
```

### Running Tests
```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test flights
python manage.py test bookings
python manage.py test users

# Run a single test class
python manage.py test flights.tests.SomeTestClass

# Run a single test method
python manage.py test flights.tests.SomeTestClass.test_something

# Run integration tests
python manage.py test tests.integration
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Django Management
```bash
# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Check for issues
python manage.py check

# Deployment check
python manage.py check --deploy

# Verify no pending migrations
python manage.py makemigrations --check
```

### Seed Data
```bash
python manage.py seed_data
```

### TM-RAG Service Token
```bash
python manage.py create_rag_service_user
python manage.py create_rag_service_user --username rag-service --days 365
```

### PostgreSQL Migration
```bash
# Requires DATABASE_URL env var (or DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT for self-hosted)
python scripts/migrate_to_postgres.py

# Or manually:
$env:DJANGO_SETTINGS_MODULE="config.settings.production"
python manage.py migrate
python manage.py seed_data
```

## Code Style Guidelines

### General Conventions

- **Language**: Python 3.10+
- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 100 characters
- **Encoding**: UTF-8
- **Newlines**: Unix-style (LF)

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Variables | snake_case | `flight_number`, `user_id` |
| Functions | snake_case | `get_flight()`, `calculate_total()` |
| Classes | PascalCase | `FlightSerializer`, `BookingViewSet` |
| Constants | SCREAMING_SNAKE | `MAX_PASSENGERS = 200` |
| Database tables | lowercase plural | `flights`, `bookings` |
| File names | snake_case | `models.py`, `flight_service.py` |

### Import Organization

Order imports in the following groups with blank lines between:

1. Standard library imports
2. Third-party imports
3. Django/DRF imports
4. Local application imports

```python
# Standard library
from datetime import timedelta
import os
import sys

# Third-party
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

# Django/DRF
from django.db import models
from django.conf import settings

# Local app
from flights.models import Flight, Airport
from bookings.serializers import BookingSerializer
```

### Model Guidelines

```python
from django.db import models

class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
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

    class Meta:
        ordering = ("departure_time",)
        indexes = [
            models.Index(fields=["departure_time"]),
        ]

    def __str__(self):
        return self.flight_number

    def clean(self):
        # Validation logic here
        pass

    def save(self, *args, **kwargs):
        # Pre-save logic
        super().save(*args, **kwargs)
```

**Rules:**
- Always include `__str__` method for models
- Use `related_name` on ForeignKey relationships
- Define choices as list of tuples at class level
- Use `on_delete=models.CASCADE` (or `PROTECT` where appropriate)
- Add `Meta` class for ordering and indexes
- Use `auto_now_add` for created_at, `auto_now` for updated_at

### Serializer Guidelines

```python
from rest_framework import serializers
from .models import Flight

class FlightSerializer(serializers.ModelSerializer):
    origin = AirportSerializer()
    destination = AirportSerializer()

    class Meta:
        model = Flight
        fields = "__all__"
        read_only_fields = ("created_at",)
```

**Rules:**
- Use `ModelSerializer` for simple cases
- Specify `fields` explicitly when possible (avoid `__all__` in production)
- Use `read_only_fields` for auto-populated fields
- Nest serializers for ForeignKey relationships

### ViewSet Guidelines

```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer

class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

**Rules:**
- Use `ModelViewSet` for CRUD operations
- Use `ReadOnlyModelViewSet` for read-only endpoints
- Always define `permission_classes`
- Override `get_queryset` for filtered results
- Override `perform_create` to set user automatically

### Error Handling

- Use appropriate HTTP status codes:
  - `200` - OK
  - `201` - Created
  - `400` - Bad Request
  - `401` - Unauthorized
  - `403` - Forbidden
  - `404` - Not Found
  - `500` - Server Error

- Let DRF handle exceptions automatically
- Use `serializer.is_valid(raise_exception=True)` for validation
- Return meaningful error messages in serializers

### Admin Configuration

Register models in `admin.py`:

```python
from django.contrib import admin
from .models import Flight

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("flight_number", "origin", "destination", "status")
    list_filter = ("status",)
    search_fields = ("flight_number",)
    ordering = ("departure_time",)
```

### Testing Guidelines

- Use Django's `TestCase` class
- Test views using `APIClient`
- Use factories for creating test objects

```python
from django.test import TestCase
from rest_framework.test import APIClient

class FlightTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_flight_list(self):
        response = self.client.get("/api/v1/flights/")
        self.assertEqual(response.status_code, 200)
```

### File Structure

```
tm-airlines-backend/
├── manage.py
├── requirements.txt
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── flights/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── admin.py
│   ├── urls.py (if needed)
│   ├── tests.py
│   └── apps.py
├── core/
│   ├── __init__.py
│   └── authentication.py       # ServiceTokenAuthentication for TM-RAG
├── scripts/
│   └── migrate_to_postgres.py  # SQLite → PostgreSQL migration tool
├── tests/
│   ├── __init__.py
│   └── integration/
│       ├── __init__.py
│       └── test_service_endpoints.py
├── bookings/
│   └── (same structure)
└── users/
    ├── management/
    │   └── commands/
    │       ├── seed_data.py
    │       └── create_rag_service_user.py
    └── (same structure)
```

## Environment Variables

Create a `.env` file in the root:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for local dev)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL (production) — just set DATABASE_URL:
# DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require

# Alternative: self-hosted PostgreSQL (uncomment and fill, comment DATABASE_URL above):
# DB_NAME=tm_airlines
# DB_USER=postgres
# DB_PASSWORD=change-me
# DB_HOST=localhost
# DB_PORT=5432

# TM-RAG Service Integration
TM_RAG_API_KEY=generate-via-create-rag-service-user-command
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/` | Obtain JWT token |
| POST | `/api/v1/auth/refresh/` | Refresh JWT token |
| POST | `/api/v1/auth/register/` | Register a new user |
| GET | `/api/v1/users/{id}/profile/` | Get user profile (service/user auth) |
| GET | `/api/v1/flights/` | List flights |
| GET | `/api/v1/flights/{id}/` | Get flight details |
| GET | `/api/v1/flights/{flight_number}/status/` | Get flight status (service/user auth) |
| GET | `/api/v1/bookings/` | List user bookings |
| POST | `/api/v1/bookings/` | Create booking |
| GET | `/api/v1/bookings/{id}/` | Get booking details |
| PUT | `/api/v1/bookings/{id}/` | Update booking |
| DELETE | `/api/v1/bookings/{id}/` | Cancel booking |
