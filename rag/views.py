from datetime import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking
from core.authentication import ServiceTokenAuthentication
from flights.models import Flight

from .serializers import (
    RAGBookingDetailSerializer,
    RAGFlightSearchSerializer,
    RAGFlightStatusSerializer,
    RAGLoyaltySerializer,
    RAGUserBookingSerializer,
    RAGUserProfileSerializer,
)

User = get_user_model()


class RAGUserProfileView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RAGUserProfileSerializer(user)
        return Response(serializer.data)


class RAGUserBookingsView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        queryset = Booking.objects.filter(user=user).select_related("flight__origin", "flight__destination")

        status_filter = request.query_params.get("status", "all")
        now = timezone.now()
        if status_filter == "upcoming":
            queryset = queryset.filter(flight__departure_time__gte=now)
        elif status_filter == "completed":
            queryset = queryset.filter(flight__departure_time__lt=now)
        elif status_filter == "cancelled":
            queryset = queryset.filter(status="cancelled")

        total = queryset.count()

        limit = int(request.query_params.get("limit", 10))
        offset = int(request.query_params.get("offset", 0))
        limit = max(1, min(limit, 50))
        offset = max(0, offset)

        bookings = queryset[offset:offset + limit]

        return Response({
            "bookings": RAGUserBookingSerializer(bookings, many=True).data,
            "total": total,
            "limit": limit,
            "offset": offset,
        })


class RAGBookingDetailView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"detail": "Missing required query parameter: user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            booking = Booking.objects.select_related(
                "flight__origin", "flight__destination"
            ).get(code=booking_id, user_id=user_id)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RAGBookingDetailSerializer(booking)
        return Response(serializer.data)


class RAGFlightStatusView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, flight_number):
        flight = get_object_or_404(Flight, flight_number=flight_number)
        serializer = RAGFlightStatusSerializer(flight)
        return Response(serializer.data)


class RAGUserLoyaltyView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RAGLoyaltySerializer(user)
        return Response(serializer.data)


class RAGFlightSearchView(APIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        origin = request.query_params.get("origin")
        destination = request.query_params.get("destination")
        date = request.query_params.get("date")

        missing = [p for p in ["origin", "destination", "date"] if not request.query_params.get(p)]
        if missing:
            return Response(
                {"detail": f"Missing required parameter(s): {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        flights = Flight.objects.filter(
            origin__code=origin.upper(),
            destination__code=destination.upper(),
            departure_time__date=date_obj,
        ).exclude(status="cancelled").select_related("origin", "destination")

        passengers = int(request.query_params.get("passengers", 1))
        seat_class = request.query_params.get("seat_class")

        if not flights.exists():
            return Response({"detail": "No flights found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RAGFlightSearchSerializer(flights, many=True)
        return Response({
            "flights": serializer.data,
            "search_criteria": {
                "origin": origin.upper(),
                "destination": destination.upper(),
                "date": date,
                "passengers": passengers,
                "seat_class": seat_class,
            },
        })
