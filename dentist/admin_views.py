from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from core.permissions import IsAdmin
from core.constants import DENTIST_VERIFICATION_STATUS
from dentist.model_serializers import DentistLicenseVerificationSerializer
from dentist.models import DentistLicenseVerification
from core.constants import DENTIST_VERIFICATION_PHASE
from core.utils.response import custom_response
from core.utils.viewsets import OwnModelViewSet, OwnReadOnlyModelViewSet
from django.utils import timezone


from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone


class DentistLicenseVerificationViewSet(OwnReadOnlyModelViewSet):
    queryset = DentistLicenseVerification.objects.select_related("dentist","verification","registration_authority").all()
    serializer_class = DentistLicenseVerificationSerializer
    permission_classes = [IsAdmin]

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        instance = self.get_object()

        if instance.status == DENTIST_VERIFICATION_STATUS.APPROVED:
            return custom_response(
                success=False,
                message="Already approved.",
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = DENTIST_VERIFICATION_STATUS.APPROVED
        instance.is_verified = True
        instance.verified_at = timezone.now()
        instance.save(update_fields=["status", "is_verified", "verified_at"])

        # update parent verification table
        verification = instance.verification
        verification.license_verification = True
        verification.save(update_fields=["license_verification"])

        # update dentist phase
        profile = instance.dentist
        profile.verification_phase = DENTIST_VERIFICATION_PHASE.TWO
        profile.save(update_fields=["verification_phase"])

        return custom_response(
            success=True,
            message="License approved successfully.",
            data=self.get_serializer(instance).data,
            status=status.HTTP_200_OK
        )



