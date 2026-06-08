from django.test import TestCase
from django.contrib.auth import get_user_model
from bookings.models import Booking
from flights.models import Airport, Flight
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test@test.com", email="test@test.com")
        origin = Airport.objects.create(code="LHR", city="London", country="UK")
        dest = Airport.objects.create(code="CDG", city="Paris", country="France")
        self.flight = Flight.objects.create(
            flight_number="TM100",
            origin=origin,
            destination=dest,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=3),
        )

    def test_booking_str(self):
        booking = Booking.objects.create(code="ABC12345", user=self.user, flight=self.flight)
        self.assertEqual(str(booking), "ABC12345")
