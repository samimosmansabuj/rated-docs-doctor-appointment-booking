from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.utils import timezone
from core.constants import DENTIST_DOCUMENT_TYPE, DENTIST_VERIFICATION_PHASE, DENTIST_VERIFICATION_STATUS, USER_ROLE_CHOICES, VERIFICATION_STATUS, PROCEDURE_CHOICES
from core.models import LicenseRegistrationAuthority, Procedure
from dentist.models import ClinicOperationVerification, ClinicalPathVerification, DentistLicenseVerification, DentistVerification, NoSurpriseGuarantee, ProcedureMaterialVerification, ProcedurePrice, SterilizationVerification, DentistProfile
from django.db import transaction


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

class DentistVerificationStatusSerializer(serializers.Serializer):
    current_phase = serializers.SerializerMethodField()
    next_phase = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()

    PHASE_LABELS = {
        DENTIST_VERIFICATION_PHASE.ONE: "License Verification",
        DENTIST_VERIFICATION_PHASE.TWO: "Operations Verification",
        DENTIST_VERIFICATION_PHASE.THREE: "Clinical Verification",
        DENTIST_VERIFICATION_PHASE.COMPLETE: "Verification Complete",
    }
    
    def _phase_status_map(self, verification):
        return {
            DENTIST_VERIFICATION_PHASE.ONE: verification.license_verification,
            DENTIST_VERIFICATION_PHASE.TWO: verification.operations_verification,
            DENTIST_VERIFICATION_PHASE.THREE: verification.clinical_verification,
            DENTIST_VERIFICATION_PHASE.COMPLETE: VERIFICATION_STATUS.APPROVED,
        }

    def get_current_phase(self, obj):
        verification = obj.dentist_verification
        status_map = self._phase_status_map(verification)
        return {
            "phase": obj.verification_phase,
            "label": self.PHASE_LABELS.get(obj.verification_phase),
            "status": status_map.get(obj.verification_phase),
        }
    
    def get_next_phase(self, obj):
        phase_order = [DENTIST_VERIFICATION_PHASE.ONE, DENTIST_VERIFICATION_PHASE.TWO, DENTIST_VERIFICATION_PHASE.THREE]
        if obj.verification_phase == DENTIST_VERIFICATION_PHASE.COMPLETE:
            return None
        try:
            current_index = phase_order.index(obj.verification_phase)
            next_phase = phase_order[current_index + 1]
            return {"phase": next_phase, "label": self.PHASE_LABELS[next_phase]}
        except (ValueError, IndexError):
            return None
    
    # def get_next_phase(self, obj):
    #     verification = obj.dentist_verification
    #     if (verification.license_verification != VERIFICATION_STATUS.APPROVED):
    #         return {"phase": DENTIST_VERIFICATION_PHASE.ONE, "label": "License Verification"}
    #     if (verification.operations_verification != VERIFICATION_STATUS.APPROVED):
    #         return {"phase": DENTIST_VERIFICATION_PHASE.TWO, "label": "Operations Verification"}
    #     if (verification.clinical_verification != VERIFICATION_STATUS.APPROVED):
    #         return {"phase": DENTIST_VERIFICATION_PHASE.THREE, "label": "Clinical Verification"}
    #     return None
    
    def get_progress_percentage(self, obj):
        verification = obj.dentist_verification
        approved_count = sum([
            verification.license_verification == VERIFICATION_STATUS.APPROVED,
            verification.operations_verification == VERIFICATION_STATUS.APPROVED,
            verification.clinical_verification == VERIFICATION_STATUS.APPROVED,
        ])
        return int((approved_count / 3) * 100)

    def get_is_verified(self, obj):
        verification = obj.dentist_verification

        return all([
            verification.license_verification == VERIFICATION_STATUS.APPROVED,
            verification.operations_verification == VERIFICATION_STATUS.APPROVED,
            verification.clinical_verification == VERIFICATION_STATUS.APPROVED,
        ])

    def get_steps(self, obj):
        verification = obj.dentist_verification

        return [
            {
                "phase": DENTIST_VERIFICATION_PHASE.ONE,
                "label": "License Verification",
                "status": verification.license_verification,
            },
            {
                "phase": DENTIST_VERIFICATION_PHASE.TWO,
                "label": "Operations Verification",
                "status": verification.operations_verification,
            },
            {
                "phase": DENTIST_VERIFICATION_PHASE.THREE,
                "label": "Clinical Verification",
                "status": verification.clinical_verification,
            },
        ]





# =====================================================================
# ------------------------Dentist Verification------------------------
class DentistLicenseVerificationSubmitSerializer(serializers.Serializer):
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
            dentist_verification.license_verification = VERIFICATION_STATUS.SUBMIT
            dentist_verification.save()
            return license_verification

# Clinical Operation Verification Phase-----
class ProcedurePriceItemSerializer(serializers.Serializer):
    procedure_name = serializers.CharField(required=False)
    procedure_id = serializers.IntegerField(required=False)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    currency = serializers.CharField(default="USD")
    option_notes = serializers.CharField(required=False, allow_blank=True)

class NoSurpriseGuaranteeSerializer(serializers.Serializer):
    signer_name = serializers.CharField()
    typed_signature = serializers.CharField()
    accepted_terms = serializers.BooleanField()

class ClinicalOperationVerificationSubmitSerializer(serializers.Serializer):
    jci_certificate = serializers.FileField(required=False)
    walkthrough_video = serializers.FileField(required=False)
    procedures = ProcedurePriceItemSerializer(many=True)
    guarantee = NoSurpriseGuaranteeSerializer()
    
    def validate(self, attrs):
        # jci_certificate = attrs.get("jci_certificate")
        # walkthrough_video = attrs.get("walkthrough_video")
        # if not jci_certificate and not walkthrough_video:
        #     raise serializers.ValidationError(
        #         "Either JCI Certificate or Walkthrough Video is required."
        #     )
        return attrs

    def check_status_validation(self, operation_verification, created):
        if not created and operation_verification.status in [DENTIST_VERIFICATION_STATUS.SUBMITTED, DENTIST_VERIFICATION_STATUS.UNDER_REVIEW]:
            raise ValidationError(
                "Operational verification is already submitted and pending review."
            )
        elif not created and operation_verification.status == DENTIST_VERIFICATION_STATUS.APPROVED:
            raise ValidationError(
                "Operational verification has already been approved. You cannot update it."
            )
        # elif not created and operation_verification.status in [DENTIST_VERIFICATION_STATUS.REJECTED, DENTIST_VERIFICATION_STATUS.NEED_MORE_EVIDENCE, DENTIST_VERIFICATION_STATUS.RESUBMIT_REQUIRED]:
        #     raise ValidationError(
        #         "Operational verification needs resubmission. Please update the required information and resubmit."
        #     )
    
    def create(self, validated_data):
        with transaction.atomic():
            user = self.context["request"].user
            dentist = user.dentist_profile
            # clinic = dentist.clinic

            if dentist.verification_phase != DENTIST_VERIFICATION_PHASE.TWO:
                raise ValidationError(
                    "Operational verification is not available yet."
                )

            dentist_verification = DentistVerification.objects.get(dentist=dentist)
            operation_verification, created = (
                ClinicOperationVerification.objects.update_or_create(
                    # clinic=clinic,
                    dentist=dentist,
                    verification=dentist_verification,
                    defaults={
                        "status": DENTIST_VERIFICATION_STATUS.SUBMITTED
                    }
                )
            )
            self.check_status_validation(operation_verification, created)
            
            # sterilization object----
            jci_certificate = validated_data.pop("jci_certificate", None)
            walkthrough_video = validated_data.pop("walkthrough_video", None)
            sterilization, _ = (
                SterilizationVerification.objects.update_or_create(
                    operation_verification=operation_verification,
                    defaults={
                        "jci_certificate": jci_certificate,
                        "walkthrough_video": walkthrough_video,
                    }
                )
            )

            procedures_data = validated_data.pop("procedures")
            ProcedurePrice.objects.filter(operation_verification=operation_verification).delete()
            for item in procedures_data:
                procedure_name = item.get("procedure_name")
                procedure_id = item.get("procedure_id")
                if not procedure_name and not procedure_id:
                    raise serializers.ValidationError(
                        "Either Procedure Name or Procedure ID is required."
                    )
                procedure = self.get_procedure(procedure_id=procedure_id, procedure_name=procedure_name)
                ProcedurePrice.objects.create(
                    operation_verification=operation_verification,
                    dentist=dentist,
                    procedure=procedure,
                    price=item["price"],
                    currency=item.get("currency", "USD"),
                    option_notes=item.get("option_notes", "")
                )

            guarantee_data = validated_data.pop("guarantee")
            NoSurpriseGuarantee.objects.update_or_create(
                operation_verification=operation_verification,
                defaults=guarantee_data
            )
            
            dentist_verification.operations_verification = VERIFICATION_STATUS.SUBMIT
            dentist_verification.save()
            return operation_verification
    
    def get_procedure(self, procedure_id=None, procedure_name=None):
        if procedure_id:
            # procedure = Procedure.objects.filter(parent__isnull=True).get(id=procedure_id, type=PROCEDURE_CHOICES.OBJECTTIVE)
            procedure = Procedure.objects.get(id=procedure_id, type=PROCEDURE_CHOICES.OBJECTTIVE)
            if procedure is None:
                raise serializers.ValidationError(
                    "Wrong Procedure ID Submit."
                )
        else:
            procedure = Procedure.objects.create(
                name=procedure_name,
                type=PROCEDURE_CHOICES.OBJECTTIVE,
                base_price=0
            )
        return procedure

# Clinical Depth Verification Phase-----
class ProcedureMaterialVerificationItemSerializer(serializers.Serializer):
    own_procedure = serializers.PrimaryKeyRelatedField(queryset=ProcedurePrice.objects.all())
    brand_name = serializers.CharField(required=True)
    # ce_certificate = serializers.FileField(required=False)
    # material_brands = serializers.FileField(required=False)
    # invoice = serializers.FileField(required=False)
    # protocol_pdf = serializers.FileField(required=False)
    # notes = serializers.CharField(required=False, allow_blank=True)

class ClinicalPathVerificationSubmitSerializer(serializers.Serializer):
    materials = ProcedureMaterialVerificationItemSerializer(many=True, required=True)

    def validate_materials(self, value):
        user = self.context["request"].user
        dentist = user.dentist_profile
        for item in value:
            if item["own_procedure"].dentist_id != dentist.id:
                raise serializers.ValidationError(
                    "You can only submit your own procedures."
                )
        return value

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context["request"].user
            dentist = user.dentist_profile
            if dentist.verification_phase != DENTIST_VERIFICATION_PHASE.THREE:
                raise serializers.ValidationError(
                    "Clinical verification is not available yet."
                )

            # clinic = dentist.clinic
            verification = DentistVerification.objects.get(
                dentist=dentist
            )

            clinical_path, created = (
                ClinicalPathVerification.objects.update_or_create(
                    # clinic=clinic,
                    dentist=dentist,
                    verification=verification,
                    defaults={
                        "status": DENTIST_VERIFICATION_STATUS.SUBMITTED
                    }
                )
            )
            
            if not created and clinical_path.status in [DENTIST_VERIFICATION_STATUS.SUBMITTED, DENTIST_VERIFICATION_STATUS.UNDER_REVIEW]:
                raise ValidationError(
                    "Clinical Depth verification is already submitted and pending review."
                )
            elif not created and clinical_path.status == DENTIST_VERIFICATION_STATUS.APPROVED:
                raise ValidationError(
                    "Clinical Depth verification has already been approved. You cannot update it."
                )

            materials = validated_data["materials"]
            ProcedureMaterialVerification.objects.filter(
                clinical_path=clinical_path
            ).delete()

            for item in materials:
                own_procedure = item["own_procedure"]
                ProcedureMaterialVerification.objects.create(
                    clinical_path=clinical_path,
                    own_procedure=own_procedure,
                    brand_name=item["brand_name"],
                    # ce_certificate=item.get("ce_certificate"),
                    # material_brands=item.get("material_brands"),
                    # invoice=item.get("invoice"),
                    # protocol_pdf=item.get("protocol_pdf"),
                    # notes=item.get("notes", "")
                )
            
            verification.clinical_verification = VERIFICATION_STATUS.SUBMIT
            verification.save()
            return clinical_path

# ------------------------Dentist Verification------------------------
# =====================================================================


# =============================Admin or Verification Object Model Serializer=============================
# Dentist License Verification Phase-------------------------------------------------------------
class DentistLicenseVerificationSerializer(serializers.ModelSerializer):
    # dentist = DentistProfileSerializer(read_only=True)
    # verification = DentistVerificationSerializer(read_only=True)
        
    class Meta:
        model = DentistLicenseVerification
        fields = "__all__"
# ------------------------------------------------------------------------------------------------

# Clinical Operation Verification Phase-----------------------------------------------------------
class SterilizationVerificationSerializer(serializers.ModelSerializer):

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
# ------------------------------------------------------------------------------------------------

# Clinical Depth Verification Phase---------------------------------------------------------------
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

class DentistProfileSerializerForVerification(serializers.ModelSerializer):
    class Meta:
        model = DentistProfile
        fields = "__all__"

class DentistVerificationDetailSerializer(serializers.ModelSerializer):
    dentist = DentistProfileSerializerForVerification(read_only=True)
    license_step = DentistLicenseVerificationSerializer(source="dentist_license_verification", read_only=True)
    operation_step = ClinicalOperationVerificationSerializer(source="operation_verification", read_only=True)
    clinical_step = ClinicalPathVerificationSerializer(source="clinical_path_verification", read_only=True)

    class Meta:
        model = DentistVerification
        fields = [
            "id", "dentist",
            
            "license_verification",
            "operations_verification",
            "clinical_verification",
            "face_match_score",

            "license_step",
            "operation_step",
            "clinical_step",
        ]

# -------------------------------------------------------------------------------------------------
# =============================Admin or Verification Object Model Serializer=============================


