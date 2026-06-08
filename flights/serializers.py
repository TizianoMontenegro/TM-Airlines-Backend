from rest_framework import serializers
from .models import Airport, Flight

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class FlightSerializer(serializers.ModelSerializer):
    origin = AirportSerializer()
    destination = AirportSerializer()

    class Meta:
        model = Flight
        fields = "__all__"


class FlightStatusSerializer(serializers.ModelSerializer):
    origin_code = serializers.CharField(source="origin.code", read_only=True)
    destination_code = serializers.CharField(source="destination.code", read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id", "flight_number", "origin_code", "destination_code",
            "departure_time", "arrival_time", "status", "updated_at",
        )
