from django.test import TestCase
from django.db import IntegrityError
from flights.models import Airport, Flight
from django.utils import timezone
from datetime import timedelta


class AirportModelTest(TestCase):
    def test_airport_str(self):
        airport = Airport.objects.create(code="LHR", city="London", country="UK")
        self.assertEqual(str(airport), "LHR")


class FlightModelTest(TestCase):
    def setUp(self):
        self.origin = Airport.objects.create(code="LHR", city="London", country="UK")
        self.dest = Airport.objects.create(code="CDG", city="Paris", country="France")

    def test_flight_str(self):
        flight = Flight.objects.create(
            flight_number="TM100",
            origin=self.origin,
            destination=self.dest,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=3),
        )
        self.assertEqual(str(flight), "TM100")

    def test_flight_number_unique(self):
        Flight.objects.create(
            flight_number="TM100", origin=self.origin, destination=self.dest,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=3),
        )
        with self.assertRaises(IntegrityError):
            Flight.objects.create(
                flight_number="TM100", origin=self.origin, destination=self.dest,
                departure_time=timezone.now() + timedelta(days=2),
                arrival_time=timezone.now() + timedelta(days=2, hours=3),
            )
