from rest_framework import serializers

from .models import (
    Clinic,
    DentistProfile,
    DentistAddress,
    DentistWeeklyAvailability,
    SlotException,
    DentistVerification,
    DentistLicenseVerification,
    ClinicOperationVerification,
    SterilizationVerification,
    SterilizationWalkthrough,
    ProcedurePrice,
    NoSurpriseGuarantee,
    ClinicalPathVerification,
    ProcedureMaterialVerification,
)

from core.models import Procedure
from account.models import User
from .models import LicenseRegistrationAuthority


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


class DentistProfileSerializer(serializers.ModelSerializer):
    clinic = ClinicSerializer(read_only=True)

    dentist_address = DentistAddressSerializer(
        many=True,
        read_only=True
    )

    weekly_availability = DentistWeeklyAvailabilitySerializer(
        many=True,
        read_only=True
    )

    slot_exceptions = SlotExceptionSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = DentistProfile
        fields = "__all__"



class DentistProfileCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentistProfile
        fields = "__all__"


class DentistVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentistVerification
        fields = "__all__"


class DentistLicenseVerificationSerializer(serializers.ModelSerializer):
    # dentist = DentistProfileSerializer(read_only=True)
    # verification = DentistVerificationSerializer(read_only=True)
        
    class Meta:
        model = DentistLicenseVerification
        fields = "__all__"



# Clinical Operation Verification Phase-------------------------------------------------------------
class SterilizationWalkthroughSerializer(serializers.ModelSerializer):
    class Meta:
        model = SterilizationWalkthrough
        fields = "__all__"

class SterilizationVerificationSerializer(serializers.ModelSerializer):
    walkthrough = SterilizationWalkthroughSerializer(read_only=True)

    class Meta:
        model = SterilizationVerification
        fields = "__all__"

class ProcedurePriceSerializer(serializers.ModelSerializer):
    procedure_name = serializers.CharField(source="procedure.name", read_only=True)

    class Meta:
        model = ProcedurePrice
        fields = "__all__"

class NoSurpriseGuaranteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoSurpriseGuarantee
        fields = "__all__"

class ClinicalOperationVerificationSerializer(serializers.ModelSerializer):
    sterilization_verification = SterilizationVerificationSerializer(read_only=True)
    no_surprise_guarantee = NoSurpriseGuaranteeSerializer(read_only=True)
    procedures_feature = ProcedurePriceSerializer(many=True, read_only=True)

    class Meta:
        model = ClinicOperationVerification
        fields = "__all__"
# -----------------------------------------------------------------------------------------------------



# Clinical Depth Verification Phase-------------------------------------------------------------------
class ProcedureMaterialVerificationSerializer(serializers.ModelSerializer):
    own_procedure = ProcedurePriceSerializer(read_only=True)

    class Meta:
        model = ProcedureMaterialVerification
        fields = "__all__"

class ClinicalPathVerificationSerializer(serializers.ModelSerializer):
    procedure_material_verifications = (ProcedureMaterialVerificationSerializer(many=True, read_only=True))
    
    class Meta:
        model = ClinicalPathVerification
        fields = "__all__"
# -----------------------------------------------------------------------------------------------------

