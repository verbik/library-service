from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as JwtTokenObtainPairSerializer,
)


class TokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=4, write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "first_name", "last_name", "password")

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=4, write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "first_name", "last_name", "password", "is_staff")
