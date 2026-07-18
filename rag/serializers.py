from rest_framework import serializers


class RAGUserProfileSerializer(serializers.Serializer):
    user_id = serializers.SerializerMethodField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.SerializerMethodField()
    loyalty_program = serializers.SerializerMethodField()
    preferences = serializers.SerializerMethodField()

    def get_user_id(self, obj):
        return str(obj.id)

    def get_phone(self, obj):
        return None

    def get_loyalty_program(self, obj):
        return None

    def get_preferences(self, obj):
        return {
            "language": obj.language,
            "seat_preference": None,
            "meal_preference": None,
            "communication_email": None,
            "communication_sms": None,
        }


class FlightNestedSerializer(serializers.Serializer):
    flight_number = serializers.CharField()
    departure_airport = serializers.CharField(source="origin.code")
    arrival_airport = serializers.CharField(source="destination.code")
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()


class RAGUserBookingSerializer(serializers.Serializer):
    booking_id = serializers.CharField(source="code")
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    flight = FlightNestedSerializer()
    passengers = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    def get_passengers(self, obj):
        return None

    def get_total_price(self, obj):
        return None


class FlightDetailNestedSerializer(serializers.Serializer):
    flight_number = serializers.CharField()
    departure_airport = serializers.CharField(source="origin.code")
    arrival_airport = serializers.CharField(source="destination.code")
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()
    aircraft = serializers.SerializerMethodField()
    gate = serializers.SerializerMethodField()
    terminal = serializers.SerializerMethodField()

    def get_aircraft(self, obj):
        return None

    def get_gate(self, obj):
        return None

    def get_terminal(self, obj):
        return None


class RAGBookingDetailSerializer(serializers.Serializer):
    booking_id = serializers.CharField(source="code")
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    flight = FlightDetailNestedSerializer()
    passengers = serializers.SerializerMethodField()
    ancillaries = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()

    def get_passengers(self, obj):
        return []

    def get_ancillaries(self, obj):
        return []

    def get_total_price(self, obj):
        return None

    def get_payment_status(self, obj):
        return None


class RAGFlightStatusSerializer(serializers.Serializer):
    flight_number = serializers.CharField()
    date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    departure = serializers.SerializerMethodField()
    arrival = serializers.SerializerMethodField()
    delay_minutes = serializers.SerializerMethodField()
    aircraft = serializers.SerializerMethodField()
    last_updated = serializers.DateTimeField(source="updated_at")

    STATUS_MAP = {
        "scheduled": "scheduled",
        "departed": "departed",
        "cancelled": "cancelled",
    }

    def get_date(self, obj):
        return obj.departure_time.strftime("%Y-%m-%d")

    def get_status(self, obj):
        return self.STATUS_MAP.get(obj.status, "scheduled")

    def get_departure(self, obj):
        return {
            "airport": obj.origin.code,
            "scheduled_time": obj.departure_time,
            "estimated_time": None,
            "actual_time": None,
            "gate": None,
            "terminal": None,
        }

    def get_arrival(self, obj):
        return {
            "airport": obj.destination.code,
            "scheduled_time": obj.arrival_time,
            "estimated_time": None,
            "actual_time": None,
        }

    def get_delay_minutes(self, obj):
        return 0

    def get_aircraft(self, obj):
        return None


class RAGLoyaltySerializer(serializers.Serializer):
    user_id = serializers.SerializerMethodField()
    tier = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()
    miles_balance = serializers.SerializerMethodField()
    miles_expiring_soon = serializers.SerializerMethodField()
    tier_benefits = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()

    def get_user_id(self, obj):
        return str(obj.id)

    def get_tier(self, obj):
        return None

    def get_member_since(self, obj):
        return None

    def get_miles_balance(self, obj):
        return 0

    def get_miles_expiring_soon(self, obj):
        return None

    def get_tier_benefits(self, obj):
        return []

    def get_recent_activity(self, obj):
        return []


class RAGFlightSearchSerializer(serializers.Serializer):
    flight_number = serializers.CharField()
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()
    duration_minutes = serializers.SerializerMethodField()
    aircraft = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    def get_duration_minutes(self, obj):
        delta = obj.arrival_time - obj.departure_time
        return int(delta.total_seconds() / 60)

    def get_aircraft(self, obj):
        return None

    def get_available_seats(self, obj):
        return {}

    def get_price(self, obj):
        return None
