import jwt
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import Booking
from flights.models import Airport, Flight

User = get_user_model()


def _service_token(user):
    payload = {
        "user_id": user.pk,
        "exp": timezone.now() + timedelta(days=365),
        "iat": timezone.now(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class RAGEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service_user = User.objects.create_user(
            username="rag-service@tm-airlines.internal",
            email="rag-service@tm-airlines.internal",
            is_active=True,
        )
        cls.user = User.objects.create_user(
            username="alice@test.com",
            email="alice@test.com",
            first_name="Alice",
            last_name="Mbeki",
            language="en",
        )
        cls.other_user = User.objects.create_user(
            username="bob@test.com",
            email="bob@test.com",
        )

        lhr = Airport.objects.create(code="LHR", city="London", country="UK")
        cdg = Airport.objects.create(code="CDG", city="Paris", country="France")
        jfk = Airport.objects.create(code="JFK", city="New York", country="USA")
        ams = Airport.objects.create(code="AMS", city="Amsterdam", country="Netherlands")

        now = timezone.now()
        cls.flight1 = Flight.objects.create(
            flight_number="TM100",
            origin=lhr,
            destination=cdg,
            departure_time=now + timedelta(days=1),
            arrival_time=now + timedelta(days=1, hours=3),
            status="scheduled",
        )
        cls.flight2 = Flight.objects.create(
            flight_number="TM200",
            origin=ams,
            destination=jfk,
            departure_time=now + timedelta(days=2),
            arrival_time=now + timedelta(days=2, hours=8),
            status="departed",
        )
        Flight.objects.create(
            flight_number="TM301",
            origin=lhr,
            destination=cdg,
            departure_time=now + timedelta(days=3),
            arrival_time=now + timedelta(days=3, hours=3),
            status="cancelled",
        )

        cls.booking1 = Booking.objects.create(
            code="BK001",
            user=cls.user,
            flight=cls.flight1,
            status="confirmed",
        )
        Booking.objects.create(
            code="BK002",
            user=cls.user,
            flight=cls.flight2,
            status="confirmed",
        )
        Booking.objects.create(
            code="BK003",
            user=cls.other_user,
            flight=cls.flight1,
            status="confirmed",
        )

        cls.token = _service_token(cls.service_user)

    def setUp(self):
        self.client = APIClient()
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    # --- 1. RAG User Profile ---

    def test_get_user_profile(self):
        response = self.client.get(f"/api/v1/rag/users/{self.user.pk}/", **self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], str(self.user.pk))
        self.assertEqual(data["email"], "alice@test.com")
        self.assertEqual(data["first_name"], "Alice")
        self.assertEqual(data["last_name"], "Mbeki")
        self.assertIsNone(data["phone"])
        self.assertIsNone(data["loyalty_program"])
        self.assertEqual(data["preferences"]["language"], "en")
        self.assertIsNone(data["preferences"]["seat_preference"])

    def test_get_user_profile_not_found(self):
        response = self.client.get("/api/v1/rag/users/9999/", **self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "User not found")

    def test_get_user_profile_requires_auth(self):
        response = self.client.get(f"/api/v1/rag/users/{self.user.pk}/")
        self.assertEqual(response.status_code, 403)

    # --- 2. RAG User Bookings ---

    def test_list_user_bookings(self):
        response = self.client.get(f"/api/v1/rag/users/{self.user.pk}/bookings/", **self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["bookings"]), 2)
        self.assertEqual(data["total"], 2)
        ids = [b["booking_id"] for b in data["bookings"]]
        self.assertIn("BK001", ids)
        self.assertIn("BK002", ids)

    def test_list_user_bookings_cancelled_filter(self):
        response = self.client.get(
            f"/api/v1/rag/users/{self.user.pk}/bookings/?status=cancelled",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["bookings"]), 0)

    def test_list_user_bookings_unknown_user(self):
        response = self.client.get("/api/v1/rag/users/9999/bookings/", **self.headers)
        self.assertEqual(response.status_code, 404)

    def test_list_user_bookings_pagination(self):
        response = self.client.get(
            f"/api/v1/rag/users/{self.user.pk}/bookings/?limit=1&offset=0",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["bookings"]), 1)
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["limit"], 1)
        self.assertEqual(data["offset"], 0)

    # --- 3. RAG Booking Detail ---

    def test_get_booking_detail(self):
        response = self.client.get(
            f"/api/v1/rag/bookings/BK001/?user_id={self.user.pk}",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["booking_id"], "BK001")
        self.assertEqual(data["status"], "confirmed")
        self.assertEqual(data["flight"]["flight_number"], "TM100")
        self.assertEqual(data["flight"]["departure_airport"], "LHR")
        self.assertEqual(data["flight"]["arrival_airport"], "CDG")
        self.assertEqual(data["passengers"], [])
        self.assertEqual(data["ancillaries"], [])
        self.assertIsNone(data["total_price"])
        self.assertIsNone(data["payment_status"])

    def test_get_booking_detail_wrong_user(self):
        response = self.client.get(
            f"/api/v1/rag/bookings/BK001/?user_id={self.other_user.pk}",
            **self.headers,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Booking not found")

    def test_get_booking_detail_missing_user_id(self):
        response = self.client.get("/api/v1/rag/bookings/BK001/", **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_get_booking_detail_not_found(self):
        response = self.client.get(
            f"/api/v1/rag/bookings/ZZZZ/?user_id={self.user.pk}",
            **self.headers,
        )
        self.assertEqual(response.status_code, 404)

    # --- 4. RAG Flight Status ---

    def test_get_flight_status(self):
        response = self.client.get("/api/v1/rag/flights/TM100/status/", **self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["flight_number"], "TM100")
        self.assertEqual(data["status"], "scheduled")
        self.assertEqual(data["departure"]["airport"], "LHR")
        self.assertEqual(data["arrival"]["airport"], "CDG")
        self.assertEqual(data["delay_minutes"], 0)
        self.assertIsNone(data["aircraft"])

    def test_get_flight_status_departed(self):
        response = self.client.get("/api/v1/rag/flights/TM200/status/", **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "departed")

    def test_get_flight_status_not_found(self):
        response = self.client.get("/api/v1/rag/flights/ZZ000/status/", **self.headers)
        self.assertEqual(response.status_code, 404)

    # --- 5. RAG Loyalty ---

    def test_get_loyalty(self):
        response = self.client.get(f"/api/v1/rag/users/{self.user.pk}/loyalty/", **self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], str(self.user.pk))
        self.assertIsNone(data["tier"])
        self.assertEqual(data["miles_balance"], 0)
        self.assertEqual(data["tier_benefits"], [])
        self.assertEqual(data["recent_activity"], [])

    def test_get_loyalty_not_found(self):
        response = self.client.get("/api/v1/rag/users/9999/loyalty/", **self.headers)
        self.assertEqual(response.status_code, 404)

    # --- 6. RAG Flight Search ---

    def test_search_flights(self):
        flight_date = self.flight1.departure_time.strftime("%Y-%m-%d")
        response = self.client.get(
            f"/api/v1/rag/flights/search/?origin=LHR&destination=CDG&date={flight_date}",
            **self.headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("flights", data)
        self.assertIn("search_criteria", data)

    def test_search_flights_missing_params(self):
        response = self.client.get(
            "/api/v1/rag/flights/search/?origin=LHR",
            **self.headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_search_flights_not_found(self):
        response = self.client.get(
            "/api/v1/rag/flights/search/?origin=AAA&destination=BBB&date=2099-01-01",
            **self.headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_search_flights_excludes_cancelled(self):
        cancelled = Flight.objects.get(flight_number="TM301")
        flight_date = cancelled.departure_time.strftime("%Y-%m-%d")
        response = self.client.get(
            f"/api/v1/rag/flights/search/?origin={cancelled.origin.code}&destination={cancelled.destination.code}&date={flight_date}",
            **self.headers,
        )
        self.assertEqual(response.status_code, 404)

    # --- Auth ---

    def test_invalid_token_returns_401(self):
        response = self.client.get(
            f"/api/v1/rag/users/{self.user.pk}/",
            HTTP_AUTHORIZATION="Bearer invalidtoken",
        )
        self.assertIn(response.status_code, (401, 403))
