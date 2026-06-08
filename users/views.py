from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from core.authentication import ServiceTokenAuthentication
from .serializers import CustomTokenObtainPairSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "User created successfully."},
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = [ServiceTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
