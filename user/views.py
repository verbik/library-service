from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserSerializer,
    TokenObtainPairSerializer,
    UserDetailSerializer,
)


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            return Response(status=status.HTTP_201_CREATED)
        return response


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserDetailSerializer

        return UserSerializer
