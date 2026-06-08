from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from flights.models import Airport, Flight
from bookings.models import Booking
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with sample airports, flights, users, and bookings."

    def handle(self, *args, **options):
        counts = {"airports": 0, "flights": 0, "users": 0, "bookings": 0}

        # -- Airports --
        airports_data = [
            ("LHR", "London", "UK"),
            ("CDG", "Paris", "France"),
            ("FRA", "Frankfurt", "Germany"),
            ("AMS", "Amsterdam", "Netherlands"),
            ("JFK", "New York", "USA"),
            ("LAX", "Los Angeles", "USA"),
            ("NRT", "Tokyo", "Japan"),
            ("DXB", "Dubai", "UAE"),
        ]
        for code, city, country in airports_data:
            _, created = Airport.objects.get_or_create(
                code=code,
                defaults={"city": city, "country": country},
            )
            if created:
                counts["airports"] += 1

        # -- Flights --
        lhr = Airport.objects.get(code="LHR")
        cdg = Airport.objects.get(code="CDG")
        fra = Airport.objects.get(code="FRA")
        ams = Airport.objects.get(code="AMS")
        jfk = Airport.objects.get(code="JFK")
        dxb = Airport.objects.get(code="DXB")
        nrt = Airport.objects.get(code="NRT")

        now = timezone.now()
        flights_data = [
            ("TM100", lhr, cdg, now + timedelta(hours=2), now + timedelta(hours=5), "scheduled"),
            ("TM101", cdg, fra, now + timedelta(hours=3), now + timedelta(hours=5, minutes=30), "scheduled"),
            ("TM200", ams, jfk, now + timedelta(hours=4), now + timedelta(hours=11), "departed"),
            ("TM201", jfk, lhr, now + timedelta(hours=6), now + timedelta(hours=13), "scheduled"),
            ("TM300", lhr, dxb, now + timedelta(hours=8), now + timedelta(hours=15), "scheduled"),
            ("TM301", dxb, nrt, now + timedelta(hours=10), now + timedelta(hours=20), "cancelled"),
        ]
        for fn, origin, dest, dep, arr, status in flights_data:
            _, created = Flight.objects.get_or_create(
                flight_number=fn,
                defaults={
                    "origin": origin,
                    "destination": dest,
                    "departure_time": dep,
                    "arrival_time": arr,
                    "status": status,
                },
            )
            if created:
                counts["flights"] += 1

        # -- Users --
        users_data = [
            ("alice@example.com", "Alice", "Johnson", "en"),
            ("bob@example.com", "Bob", "Smith", "en"),
            ("carol@example.com", "Carol", "Williams", "fr"),
        ]
        for email, first, last, lang in users_data:
            _, created = User.objects.get_or_create(
                username=email,
                defaults={
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "language": lang,
                },
            )
            if created:
                counts["users"] += 1

        # -- Bookings --
        alice = User.objects.get(username="alice@example.com")
        bob = User.objects.get(username="bob@example.com")
        tm100 = Flight.objects.get(flight_number="TM100")
        tm200 = Flight.objects.get(flight_number="TM200")
        tm300 = Flight.objects.get(flight_number="TM300")

        bookings_data = [
            ("ABC12345", alice, tm100, "confirmed"),
            ("DEF67890", bob, tm100, "confirmed"),
            ("GHI11111", alice, tm200, "confirmed"),
            ("JKL22222", bob, tm300, "cancelled"),
        ]
        for code, user, flight, status in bookings_data:
            _, created = Booking.objects.get_or_create(
                code=code,
                defaults={
                    "user": user,
                    "flight": flight,
                    "status": status,
                },
            )
            if created:
                counts["bookings"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeding complete: {counts['airports']} airports, {counts['flights']} flights, "
            f"{counts['users']} users, {counts['bookings']} bookings created."
        ))
