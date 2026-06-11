from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.utils import timezone
from core.constants import DENTIST_DOCUMENT_TYPE, DENTIST_VERIFICATION_PHASE, DENTIST_VERIFICATION_STATUS, USER_ROLE_CHOICES
from core.models import LicenseRegistrationAuthority, Procedure
from dentist.models import ClinicOperationVerification, DentistLicenseVerification, DentistVerification, NoSurpriseGuarantee, ProcedurePrice, SterilizationVerification, SterilizationWalkthrough
from django.db import transaction

class DentistVerificationProgressSerializer(serializers.Serializer):
    current_phase = serializers.CharField()
    current_phase_label = serializers.CharField()
    progress_percentage = serializers.IntegerField()
    is_verified = serializers.BooleanField()
    steps = serializers.ListField()

class DentistVerificationPhaseUpdateSerializer(serializers.Serializer):
    verification_phase = serializers.ChoiceField(choices=DENTIST_VERIFICATION_PHASE.choices)

    def save(self):
        user = self.context["request"].user
        profile = user.dentist_profile
        phase = self.validated_data["verification_phase"]
        profile.verification_phase = phase
        if phase == DENTIST_VERIFICATION_PHASE.COMPLETE:
            profile.is_verified = True
            profile.verified_at = timezone.now()
        profile.save()
        return profile










# =====================================================================
# ------------------------Dentist Verification------------------------
class DentistLicenseVerificationSerializer(serializers.Serializer):
    professional_headshot = serializers.ImageField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    registration_authority = serializers.PrimaryKeyRelatedField(
        queryset=LicenseRegistrationAuthority.objects.all()
    )
    registration_no = serializers.CharField(required=True)
    # doc_type = serializers.ChoiceField(choices=DENTIST_DOCUMENT_TYPE.choices)
    file = serializers.FileField(required=True)
    
    def get_user(self):
        user = self.context["request"].user
        if user.role != USER_ROLE_CHOICES.DENTIST:
            raise serializers.ValidationError(
                "Only dentists can submit verification."
            )
        return user
    
    def create(self, validated_data):
        with transaction.atomic():
            user = self.get_user()
            profile = user.dentist_profile
            dentist_verification, _ = DentistVerification.objects.get_or_create(dentist=profile)
            registration_authority = validated_data.pop("registration_authority")

            dentist_license_verification = DentistLicenseVerification.objects.filter(
                verification=dentist_verification
            ).first()
            if dentist_license_verification:
                status = dentist_license_verification.status
                error_messages = {
                    DENTIST_VERIFICATION_STATUS.APPROVED: "License verification has already been approved. You cannot update it.",
                    DENTIST_VERIFICATION_STATUS.SUBMITTED: "License verification is already submitted and pending review.",
                    DENTIST_VERIFICATION_STATUS.UNDER_REVIEW: "License verification is currently under review.",
                    DENTIST_VERIFICATION_STATUS.REJECTED: "License verification has been rejected.",
                    DENTIST_VERIFICATION_STATUS.NEED_MORE_EVIDENCE: "License verification needs more evidence.",
                    DENTIST_VERIFICATION_STATUS.RESUBMIT_REQUIRED: "License verification requires resubmission.",
                    DENTIST_VERIFICATION_STATUS.EXPIRED: "License verification has expired.",
                }
                if status in error_messages:
                    raise serializers.ValidationError({
                        "error": error_messages[status]
                    })
            
            license_verification, created = (
                DentistLicenseVerification.objects.update_or_create(
                    dentist=profile,
                    verification=dentist_verification,
                    defaults={
                        **validated_data,
                        "registration_authority": registration_authority,
                        "status": DENTIST_VERIFICATION_STATUS.SUBMITTED,
                    }
                )
            )
            return license_verification


class SterilizationSectionSerializer(serializers.Serializer):
    has_jci_certificate = serializers.BooleanField()
    jci_certificate = serializers.FileField(required=False)
    certificate_number = serializers.CharField(required=False)
    expiry_date = serializers.DateField(required=False)
    issuing_authority = serializers.CharField(required=False)
    issue_date = serializers.DateField(required=False)

    walkthrough_video = serializers.FileField(required=False)

    autoclave_brand = serializers.BooleanField()
    sealed_pouch_visible = serializers.BooleanField()
    ultrasonic_cleaner_available = serializers.BooleanField()

class ProcedurePriceItemSerializer(serializers.Serializer):
    procedure = serializers.PrimaryKeyRelatedField(queryset=Procedure.objects.all())
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(default="USD")
    option_notes = serializers.CharField(required=False, allow_blank=True)

class NoSurpriseGuaranteeSerializer(serializers.Serializer):
    signer_name = serializers.CharField()
    typed_signature = serializers.CharField()
    accepted_terms = serializers.BooleanField()

class ClinicOperationVerificationSerializer(serializers.Serializer):
    sterilization = SterilizationSectionSerializer()
    procedures = ProcedurePriceItemSerializer(many=True)
    guarantee = NoSurpriseGuaranteeSerializer()

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context["request"].user
            dentist = user.dentist_profile

            if dentist.verification_phase != DENTIST_VERIFICATION_PHASE.TWO:
                raise ValidationError(
                    "Operational verification is not available yet."
                )

            # clinic = dentist.clinic

            dentist_verification = DentistVerification.objects.get(
                dentist=dentist
            )

            operation_verification, _ = (
                ClinicOperationVerification.objects.update_or_create(
                    # clinic=clinic,
                    dentist=dentist,
                    verification=dentist_verification,
                    defaults={
                        "status": DENTIST_VERIFICATION_STATUS.SUBMITTED
                    }
                )
            )

            sterilization_data = validated_data.pop("sterilization")
            procedures_data = validated_data.pop("procedures")
            guarantee_data = validated_data.pop("guarantee")

            sterilization, _ = (
                SterilizationVerification.objects.update_or_create(
                    operation_verification=operation_verification,
                    defaults={
                        "has_jci_certificate": sterilization_data.get("has_jci_certificate"),
                        "jci_certificate": sterilization_data.get("jci_certificate"),
                        "certificate_number": sterilization_data.get("certificate_number"),
                        "expiry_date": sterilization_data.get("expiry_date"),
                        "issuing_authority": sterilization_data.get("issuing_authority"),
                        "issue_date": sterilization_data.get("issue_date"),
                    }
                )
            )
            if sterilization.has_jci_certificate:
                SterilizationWalkthrough.objects.update_or_create(
                    sterilization=sterilization,
                    defaults={
                        "walkthrough_video": sterilization_data.get("walkthrough_video"),
                        "autoclave_brand": sterilization_data.get("autoclave_brand"),
                        "sealed_pouch_visible": sterilization_data.get("sealed_pouch_visible"),
                        "ultrasonic_cleaner_available": sterilization_data.get("ultrasonic_cleaner_available"),
                    }
                )

            ProcedurePrice.objects.filter(
                operation_verification=operation_verification
            ).delete()

            for item in procedures_data:
                ProcedurePrice.objects.create(
                    operation_verification=operation_verification,
                    dentist=dentist,
                    procedure=item["procedure"],
                    price=item["price"],
                    currency=item.get("currency", "USD"),
                    option_notes=item.get("option_notes", "")
                )

            NoSurpriseGuarantee.objects.update_or_create(
                operation_verification=operation_verification,
                defaults=guarantee_data
            )

            return operation_verification

# ------------------------Dentist Verification------------------------
# =====================================================================
