from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.authentication import ServiceTokenAuthentication
from .models import Booking
from .serializers import BookingSerializer

# Create your views here.

class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    authentication_classes = [ServiceTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self.request, "service_mode", False):
            user_id = self.request.query_params.get("user_id")
            if user_id:
                return Booking.objects.filter(user_id=user_id)
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
