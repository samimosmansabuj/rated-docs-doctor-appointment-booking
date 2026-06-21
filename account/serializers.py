from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth import get_user_model
from .models import PatientProfile, OTP
from dentist.models import DentistProfile, DentistAddress, DentistVerification
from core.constants import DENTIST_SPECIALTY, OTP_PURPOSE, USER_ROLE_CHOICES
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "role"]

# ==========================================================================
# ======================Authentication Serializers=========================
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email", "gender", "password", "confirm_password", "role", "referral_code"]
    
    def validate_role(self, value):
        value = value.upper()
        if value in [
            USER_ROLE_CHOICES.ADMIN,
            USER_ROLE_CHOICES.STAFF,
        ]:
            raise serializers.ValidationError(
                "You are not allowed to register as Admin or Staff."
            )
        return value
    
    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        return attrs
    
    def generate_otp(self):
        import random
        return str(random.randint(100000, 999999))
    
    def create(self, validated_data):
        with transaction.atomic():
            password = validated_data.pop("password")
            validated_data.pop("confirm_password", None)
            validated_data.pop("referral_code", None)
            role = validated_data.pop("role")
            if role not in USER_ROLE_CHOICES.values: raise ValidationError("Invalid Role.")
            user = User.objects.create_user(**validated_data, password=password)
            user.role = role
            user.save()
            
            # auto profile create
            if role == "PATIENT": PatientProfile.objects.create(user=user)
            return user
    
    def send_otp(self, user):
        otp = OTP.objects.create(user=user, otp_code=self.generate_otp(), purpose=OTP_PURPOSE.EMAIL_VERIFICATION)
        return otp

class AdminUserAddSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "email", "username", "password", "role"]
    
    def create(self, validated_data):
        with transaction.atomic():
            password = validated_data.pop("password")
            phone = validated_data.pop("phone")
            role = validated_data.pop("role")
            if role not in USER_ROLE_CHOICES.values:
                raise ValidationError("Invalid Role.")
            
            user = User.objects.create_user(**validated_data)
            user.set_password(password)
            user.role = role
            user.is_verified = True
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

    def get_profile_created(self, user):
        if user.role == USER_ROLE_CHOICES.PATIENT and hasattr(user, "patient_profile"):
            return True
        elif user.role == USER_ROLE_CHOICES.DENTIST and hasattr(user, "dentist_profile"):
            return True
        elif user.role == USER_ROLE_CHOICES.ADMIN:
            return True
        else:
            return False
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        role = attrs.get("role")
        user = authenticate(email=email, password=password)
        if not user:
            raise ValidationError("Invalid credentials")
        self.check_role(role, user)
        if user.role in [USER_ROLE_CHOICES.PATIENT, USER_ROLE_CHOICES.DENTIST] and user.is_verified is False:
            raise ValidationError("User Unverified.")
        refresh = RefreshToken.for_user(user)
        
        response = {
            "user": UserSerializer(user).data,
            "role": user.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        if user.role in [USER_ROLE_CHOICES.PATIENT, USER_ROLE_CHOICES.DENTIST]:
            response["profile_created"] = self.get_profile_created(user)
        return response

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

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs["email"]
        otp_code = attrs["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("User not found.")

        otp = OTP.objects.filter(
            user=user,
            otp_code=otp_code,
            purpose=OTP_PURPOSE.EMAIL_VERIFICATION,
            is_verified=False
        ).order_by("-created_at").first()

        if not otp:
            raise ValidationError("Invalid OTP.")

        if otp.is_expired:
            raise ValidationError("OTP expired.")

        attrs["user"] = user
        attrs["otp_obj"] = otp
        return attrs

    def save(self):
        user = self.validated_data["user"]
        otp = self.validated_data["otp_obj"]

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        otp.is_verified = True
        otp.verified_at = timezone.now()
        otp.save(update_fields=["is_verified"])

        refresh = RefreshToken.for_user(user)

        return {
            "user": UserSerializer(user).data,
            "role": user.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.is_verified:
            raise serializers.ValidationError("User already verified.")
        self.user = user
        return value

    def generate_otp(self):
        import random
        return str(random.randint(100000, 999999))

    def save(self):
        OTP.objects.filter(
            user=self.user,
            purpose=OTP_PURPOSE.EMAIL_VERIFICATION,
            is_verified=False
        ).delete()
        return OTP.objects.create(
            user=self.user,
            otp_code=self.generate_otp(),
            purpose=OTP_PURPOSE.EMAIL_VERIFICATION
        )

# ======================Authentication Serializers=========================
# ==========================================================================


class DentistProfessionalSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    specialty = serializers.ChoiceField(choices=DENTIST_SPECIALTY.choices, required=True)
    experience_years = serializers.IntegerField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    
    def create(self, validated_data):
        with transaction.atomic():
            request = self.context.get("request")
            user = request.user
            if user.role != USER_ROLE_CHOICES.DENTIST:
                raise ValidationError("Only dentists can submit professional details.")

            dentist_profile, created = DentistProfile.objects.get_or_create(
                user=user,
                defaults={
                    "full_name": validated_data.get("full_name"),
                    "specialty": validated_data.get("specialty"),
                    "experience_years": validated_data.get("experience_years")
                }
            )
            DentistAddress.objects.update_or_create(
                profile=dentist_profile,
                defaults={
                    "city": validated_data.get("city"),
                    "country": validated_data.get("country")
                }
            )
            DentistVerification.objects.get_or_create(
                dentist=dentist_profile
            )
            return dentist_profile
