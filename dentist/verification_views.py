from core.permissions import IsDentist
from rest_framework.exceptions import ValidationError
from core.utils.response import custom_response
from core.utils.views import OwnAPIView
from dentist.models import DentistLicenseVerification
from dentist.serializers import ClinicOperationVerificationSerializer, DentistLicenseVerificationSerializer

class DentistLicenseVerificationAPIView(OwnAPIView):
    permission_classes = [IsDentist]
    serializer_class = DentistLicenseVerificationSerializer

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

class ClinicOperationVerificationAPIView(OwnAPIView):
    permission_classes = [IsDentist]
    serializer_class = ClinicOperationVerificationSerializer

    def success_response(self, serializer):
        serializer.save()

        return custom_response(
            success=True,
            message="Operational verification submitted successfully.",
            detail="Phase 2 submitted."
        )

    # def get(self, request, *args, **kwargs):
    #     profile = request.user.dentist_profile
    #     try:
    #         instance = DentistLicenseVerification.objects.select_related(
    #             "dentist",
    #             "verification",
    #             "registration_authority"
    #         ).get(dentist=profile)
    #     except DentistLicenseVerification.DoesNotExist:
    #         return custom_response(
    #             success=True,
    #             message="No license verification found.",
    #             data={
    #                 "submitted": False,
    #                 "status": None
    #             }
    #         )

    #     return custom_response(
    #         success=True,
    #         message="License verification status fetched.",
    #         data={
    #             "submitted": True,
    #             "status": instance.status,
    #             "is_verified": instance.is_verified,
    #             "verified_at": instance.verified_at,
    #             "data": DentistLicenseVerificationSerializer(instance).data
    #         }
    #     )

