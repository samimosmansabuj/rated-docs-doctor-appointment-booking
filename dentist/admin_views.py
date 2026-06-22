from django.shortcuts import get_object_or_404
from core.permissions import IsAdmin
from core.constants import DENTIST_VERIFICATION_STATUS, VERIFICATION_STATUS
from dentist.serializer.serializers import (
    DentistLicenseVerificationSerializer, ClinicalOperationVerificationSerializer, ClinicalPathVerificationSerializer, DentistVerificationDetailSerializer
)
from dentist.models import DentistVerification
from core.constants import DENTIST_VERIFICATION_PHASE
from core.utils.response import custom_response
from core.utils.viewsets import OwnReadOnlyModelViewSet
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone


class DentistVerificationViewSet(OwnReadOnlyModelViewSet):
    queryset = DentistVerification.objects.select_related(
        "dentist", "dentist_license_verification", "operation_verification", "clinical_path_verification",
    ).prefetch_related(
        "operation_verification__procedures_feature",
        "operation_verification__procedures_feature__procedure",

        "clinical_path_verification__procedure_material_verifications",
        "clinical_path_verification__procedure_material_verifications__own_procedure",
    )

    serializer_class = DentistVerificationDetailSerializer
    permission_classes = [IsAdmin]
    
    @action(detail=True, methods=["post"], url_path="approve-license")
    def approve_license(self, request, pk=None):
        verification = self.get_object()
        license_obj = verification.dentist_license_verification
        if license_obj.status == DENTIST_VERIFICATION_STATUS.APPROVED:
            return custom_response(
                success=False,
                message="License already approved.",
                status=status.HTTP_400_BAD_REQUEST
            )

        license_obj.status = DENTIST_VERIFICATION_STATUS.APPROVED
        license_obj.is_verified = True
        license_obj.verified_at = timezone.now()
        license_obj.save(update_fields=["status", "is_verified", "verified_at"])

        verification.license_verification = VERIFICATION_STATUS.APPROVED
        verification.save(update_fields=["license_verification"])

        verification.dentist.verification_phase = (
            DENTIST_VERIFICATION_PHASE.TWO
        )
        verification.dentist.save(
            update_fields=["verification_phase"]
        )
        
        return custom_response(
            success=True,
            message="License approved successfully.",
            data=DentistLicenseVerificationSerializer(license_obj).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="approve-operation")
    def approve_operation(self, request, pk=None):
        verification = self.get_object()
        operation_obj = verification.operation_verification
        if operation_obj.status == DENTIST_VERIFICATION_STATUS.APPROVED:
            return custom_response(
                success=False,
                message="Operation already approved.",
                status=status.HTTP_400_BAD_REQUEST
            )

        operation_obj.status = DENTIST_VERIFICATION_STATUS.APPROVED
        operation_obj.is_verified = True
        operation_obj.verified_at = timezone.now()
        operation_obj.verified_by = request.user
        operation_obj.save(update_fields=["status", "is_verified", "verified_at", "verified_by"])

        verification.operations_verification = (VERIFICATION_STATUS.APPROVED)
        verification.save(update_fields=["operations_verification"])

        verification.dentist.verification_phase = (DENTIST_VERIFICATION_PHASE.THREE)
        verification.dentist.save(update_fields=["verification_phase"])
        
        return custom_response(
            success=True,
            message="Clinic operation verification approved successfully.",
            data=ClinicalOperationVerificationSerializer(operation_obj).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=["post"], url_path="approve-clinical")
    def approve_clinical(self, request, pk=None):
        verification = self.get_object()
        clinical_obj = verification.clinical_path_verification
        if clinical_obj.status == DENTIST_VERIFICATION_STATUS.APPROVED:
            return custom_response(
                success=False,
                message="Clinical verification already approved.",
                status=status.HTTP_400_BAD_REQUEST
            )

        clinical_obj.status = DENTIST_VERIFICATION_STATUS.APPROVED
        clinical_obj.is_verified = True
        clinical_obj.verified_at = timezone.now()
        clinical_obj.verified_by = request.user
        clinical_obj.save(update_fields=["status", "is_verified", "verified_at", "verified_by"])

        verification.clinical_verification = (VERIFICATION_STATUS.APPROVED)
        verification.save(update_fields=["clinical_verification"])

        verification.dentist.verification_phase = (DENTIST_VERIFICATION_PHASE.COMPLETE)
        verification.dentist.save(update_fields=["verification_phase"])
        
        return custom_response(
            success=True,
            message="Clinical path verification approved successfully.",
            data=ClinicalPathVerificationSerializer(clinical_obj).data,
            status=status.HTTP_200_OK
        )



