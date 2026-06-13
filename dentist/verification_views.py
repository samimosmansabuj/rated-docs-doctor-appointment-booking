from core.permissions import IsDentist
from rest_framework.exceptions import ValidationError
from core.utils.response import custom_response
from core.utils.views import OwnAPIView
from dentist.models import ClinicOperationVerification, ClinicalPathVerification, DentistLicenseVerification
from dentist.serializers import ClinicalOperationVerificationSubmitSerializer, DentistLicenseVerificationSubmitSerializer, ClinicalPathVerificationSubmitSerializer
from .model_serializers import ClinicalOperationVerificationSerializer, ClinicalPathVerificationSerializer, DentistLicenseVerificationSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class DentistLicenseVerificationSubmitAPIView(OwnAPIView):
    permission_classes = [IsDentist]
    serializer_class = DentistLicenseVerificationSubmitSerializer

    def success_response(self, serializer):
        serializer.save()
        return custom_response(
            success=True,
            message="You’ve completed Phase 1. Continue to Phase 2 to submit operations details and keep moving through verification..",
            detail="License verified submitted.",
        )
    
    def get(self, request, *args, **kwargs):
        profile = request.user.dentist_profile
        try:
            instance = DentistLicenseVerification.objects.select_related(
                "dentist",
                "verification",
                "registration_authority"
            ).get(dentist=profile)
        except DentistLicenseVerification.DoesNotExist:
            return custom_response(
                success=True,
                message="No license verification found.",
                data={
                    "submitted": False,
                    "status": None
                }
            )

        return custom_response(
            success=True,
            message="License verification status fetched.",
            data={
                "submitted": True,
                "status": instance.status,
                "is_verified": instance.is_verified,
                "verified_at": instance.verified_at,
                "data": DentistLicenseVerificationSerializer(instance).data
            }
        )

class ClinicalOperationVerificationSubmitAPIView(OwnAPIView):
    permission_classes = [IsDentist]
    serializer_class = ClinicalOperationVerificationSubmitSerializer
    parser_classes = [MultiPartParser, FormParser]

    def success_response(self, serializer):
        serializer.save()

        return custom_response(
            success=True,
            message="Operational verification submitted successfully.",
            detail="Phase 2 submitted."
        )

    def get(self, request, *args, **kwargs):
        profile = request.user.dentist_profile
        try:
            instance = ClinicOperationVerification.objects.select_related(
                "dentist",
                "verification",
                "clinic",
                "verified_by",
                "sterilization_verification",
                "no_surprise_guarantee",
            ).prefetch_related(
                "procedures_feature",
                "procedures_feature__procedure",
            ).get(dentist=profile)
        except ClinicOperationVerification.DoesNotExist:
            return custom_response(
                success=True,
                message="No clinic operation verification found.",
                data={
                    "submitted": False,
                    "status": None
                }
            )

        return custom_response(
            success=True,
            message="Clinic operation verification status fetched.",
            data={
                "submitted": True,
                "status": instance.status,
                "is_verified": instance.is_verified,
                "verified_at": instance.verified_at,
                "data": ClinicalOperationVerificationSerializer(instance).data
            }
        )

class ClinicalDepthVerificationSubmitAPIView(OwnAPIView):
    permission_classes = [IsDentist]
    serializer_class = ClinicalPathVerificationSubmitSerializer
    # parser_classes = [MultiPartParser, FormParser]
    
    def success_response(self, serializer):
        serializer.save()
        return custom_response(
            success=True,
            message="Clinical path verification submitted successfully.",
            detail="Phase 3 submitted."
        )

    def get(self, request, *args, **kwargs):
        profile = request.user.dentist_profile
        try:
            instance = ClinicalPathVerification.objects.select_related(
                "dentist", "verification", "clinic", "verified_by"
            ).get(dentist=profile)
        except ClinicalPathVerification.DoesNotExist:
            return custom_response(
                success=True,
                message="No clinical path verification found.",
                data={
                    "submitted": False,
                    "status": None
                }
            )

        return custom_response(
            success=True,
            message="Clinical path verification status fetched.",
            data={
                "submitted": True,
                "status": instance.status,
                "is_verified": instance.is_verified,
                "verified_at": instance.verified_at,
                "data": ClinicalPathVerificationSerializer(instance).data
            }
        )

