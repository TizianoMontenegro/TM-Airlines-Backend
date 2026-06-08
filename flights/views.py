from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from core.authentication import ServiceTokenAuthentication
from .models import Flight
from .serializers import FlightSerializer, FlightStatusSerializer

# Create your views here.
class FlightViewSet(ReadOnlyModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class FlightStatusView(APIView):
    authentication_classes = [ServiceTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, flight_number):
        flight = get_object_or_404(Flight, flight_number=flight_number)
        serializer = FlightStatusSerializer(flight)
        return Response(serializer.data)