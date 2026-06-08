from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from flights.models import Airport, Flight
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class ServiceEndpointsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="alice@test.com", email="alice@test.com")
        origin = Airport.objects.create(code="LHR", city="London", country="UK")
        dest = Airport.objects.create(code="CDG", city="Paris", country="France")
        self.flight = Flight.objects.create(
            flight_number="TM100",
            origin=origin,
            destination=dest,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=3),
        )

    def test_profile_endpoint_requires_auth(self):
        response = self.client.get(f"/api/v1/users/{self.user.pk}/profile/")
        self.assertEqual(response.status_code, 403)

    def test_flight_status_requires_auth(self):
        response = self.client.get("/api/v1/flights/TM100/status/")
        self.assertEqual(response.status_code, 403)

    def test_flight_status_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/flights/TM100/status/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["flight_number"], "TM100")

    def test_flight_status_returns_404_for_unknown(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/flights/ZZ000/status/")
        self.assertEqual(response.status_code, 404)
