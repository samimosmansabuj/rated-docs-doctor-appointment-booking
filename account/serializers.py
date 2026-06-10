from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth import get_user_model
from .models import PatientProfile
from dentist.models import DentistProfile
from core.constants import USER_ROLE_CHOICES
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "username", "role"]


class SignupSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email", "username", "password", "role"]

    def create(self, validated_data):
        with transaction.atomic():
            password = validated_data.pop("password")
            role = validated_data.pop("role")
            if role not in USER_ROLE_CHOICES.values:
                raise ValidationError("Invalid Role.")
            phone = validated_data.pop("phone")
            user = User.objects.create_user(**validated_data)
            user.set_password(password)
            user.role = role
            user.save()

            # auto profile create
            if role == "PATIENT":
                PatientProfile.objects.create(user=user, phone=phone)
            # elif role == "DENTIST":
            #     DentistProfile.objects.create(user=user, phone=phone)
            return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)
    
    def check_role(self, role, user):
        if role not in USER_ROLE_CHOICES.values:
            raise ValidationError("Invalid Role")
        if role != user.role:
            raise ValidationError(f"This user is not {role}")
        return True

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        role = attrs.get("role")
        user = authenticate(username=email, password=password)
        if not user:
            raise ValidationError("Invalid credentials")
        self.check_role(role, user)
        refresh = RefreshToken.for_user(user)
        return {
            "user": UserSerializer(user).data,
            "role": user.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs["refresh"])
            return {
                "access": str(refresh.access_token)
            }
        except Exception:
            raise serializers.ValidationError("Invalid refresh token")

class DentistProfessionalSerializer(serializers.Serializer):
    city = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True)
    
    class Meta:
        model = DentistProfile
        fields = ["full_name", "specialty", "experience_years", "city", "country"]
