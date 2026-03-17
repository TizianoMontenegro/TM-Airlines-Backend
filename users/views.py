from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer


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
