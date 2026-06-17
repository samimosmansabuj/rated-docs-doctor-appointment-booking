from rest_framework import serializers
from account.models import User
from ..models import (
    Clinic,
    DentistProfile,
    DentistAddress,
    DentistWeeklyAvailability,
    SlotException,
    DentistVerification,
    DentistLicenseVerification,
)
from .serializers import (
    DentistLicenseVerificationSerializer, ClinicalOperationVerificationSerializer, ClinicalPathVerificationSerializer
)

class DentistUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone", "is_verified",]

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = "__all__"

class DentistAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentistAddress
        fields = "__all__"

class DentistWeeklyAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DentistWeeklyAvailability
        fields = "__all__"

class SlotExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlotException
        fields = "__all__"

class DentistLicenseVerificationSerializer(serializers.ModelSerializer):
    registration_authority_name = serializers.CharField(source="registration_authority.name", read_only=True)

    class Meta:
        model = DentistLicenseVerification
        fields = "__all__"

class DentistVerificationSerializer(serializers.ModelSerializer):
    dentist_license_verification = (DentistLicenseVerificationSerializer(read_only=True))
    operation_verification = (ClinicalOperationVerificationSerializer(read_only=True))
    clinical_path_verification = (ClinicalPathVerificationSerializer(read_only=True))
    
    class Meta:
        model = DentistVerification
        fields = "__all__"

class DentistProfileDetailSerializer(serializers.ModelSerializer):
    user = DentistUserSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    dentist_address = DentistAddressSerializer(many=True,read_only=True)
    weekly_availability = (DentistWeeklyAvailabilitySerializer(many=True,read_only=True))
    slot_exceptions = SlotExceptionSerializer(many=True,read_only=True)
    dentist_verification = (DentistVerificationSerializer(read_only=True))

    class Meta:
        model = DentistProfile
        fields = [
            "id", "user", "clinic",
            "full_name", "phone", "specialty", "bio", "experience_years",
            "rating_avg", "total_reviews",
            "rdv_score", "response_time_avg",
            "verification_phase", "is_verified", "verified_at",
            "dentist_address", "weekly_availability", "slot_exceptions",
            "dentist_verification",
            "created_at", "updated_at",
        ]



