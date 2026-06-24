from core.permissions import IsAdmin
from core.constants import DENTIST_VERIFICATION_STATUS, VERIFICATION_STATUS
from dentist.serializer.serializers import (
    DentistLicenseVerificationSerializer, ClinicalOperationVerificationSerializer, ClinicalPathVerificationSerializer, DentistVerificationDetailSerializer
)
from dentist.models import DentistVerification
from core.constants import DENTIST_VERIFICATION_PHASE
from core.utils.response import custom_response
from core.utils.viewsets import OwnReadOnlyModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction


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
    
    def mark_dentist_verify(self, verification):
        dentist = verification.dentist
        if (
            verification.license_verification == VERIFICATION_STATUS.APPROVED and 
            verification.operations_verification == VERIFICATION_STATUS.APPROVED and
            verification.clinical_verification == VERIFICATION_STATUS.APPROVED
        ):
            dentist.verification_phase = (DENTIST_VERIFICATION_PHASE.COMPLETE)
            dentist.is_verified = True
            dentist.save(update_fields=["verification_phase", "is_verified"])
        else:
            dentist.is_verified = False
            dentist.save(update_fields=["is_verified"])
        return dentist
    
    
    @action(detail=True, methods=["post"], url_path="approve-license")
    def approve_license(self, request, pk=None):
        with transaction.atomic():
            verification = self.get_object()
            license_obj = verification.dentist_license_verification
            if license_obj.status == DENTIST_VERIFICATION_STATUS.APPROVED:
                return custom_response(
                    success=False,
                    message="License already approved.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            license_obj.status = DENTIST_VERIFICATION_STATUS.APPROVED
            license_obj.reviewer_notes = note
            license_obj.is_verified = True
            license_obj.verified_at = timezone.now()
            license_obj.verified_by = request.user
            license_obj.save(update_fields=["status", "reviewer_notes", "is_verified", "verified_at", "verified_by"])
            
            verification.license_verification = VERIFICATION_STATUS.APPROVED
            verification.save(update_fields=["license_verification"])
            self.mark_dentist_verify(verification)
            return custom_response(
                success=True,
                message="License approved successfully.",
                data=DentistLicenseVerificationSerializer(license_obj).data,
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=["post"], url_path="reject-license")
    def reject_license(self, request, pk=None):
        with transaction.atomic():
            note = request.data.get("note", "License verification rejected.")
            verification = self.get_object()
            license_obj = verification.dentist_license_verification
            
            if license_obj.status == DENTIST_VERIFICATION_STATUS.APPROVED:
                return custom_response(
                    success=False,
                    message="License already approved.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            license_obj.status = DENTIST_VERIFICATION_STATUS.REJECTED
            license_obj.reviewer_notes = note
            license_obj.save(update_fields=["status", "reviewer_notes"])
            
            verification.license_verification = VERIFICATION_STATUS.REJECT
            verification.save(update_fields=["license_verification"])
            return custom_response(
                success=True,
                message="License verification rejected.",
                data=DentistLicenseVerificationSerializer(license_obj).data,
                status=status.HTTP_200_OK
            )

    
    @action(detail=True, methods=["post"], url_path="approve-operation")
    def approve_operation(self, request, pk=None):
        with transaction.atomic():
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
            self.mark_dentist_verify(verification)
            return custom_response(
                success=True,
                message="Clinic operation verification approved successfully.",
                data=ClinicalOperationVerificationSerializer(operation_obj).data,
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=["post"], url_path="reject-operation")
    def reject_operation(self, request, pk=None):
        with transaction.atomic():
            note = request.data.get("note", "Operation verification rejected.")
            verification = self.get_object()
            operation_obj = verification.operation_verification
            if operation_obj.status == DENTIST_VERIFICATION_STATUS.APPROVED:
                return custom_response(
                    success=False,
                    message="Operation already approved.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            operation_obj.status = DENTIST_VERIFICATION_STATUS.REJECTED
            operation_obj.reviewer_notes = note
            operation_obj.save(update_fields=["status", "reviewer_notes"])
            
            verification.operations_verification = VERIFICATION_STATUS.REJECT
            verification.save(update_fields=["operations_verification"])
            return custom_response(
                success=True,
                message="Operation verification rejected.",
                data=ClinicalOperationVerificationSerializer(operation_obj).data,
                status=status.HTTP_200_OK
            )
    
    
    @action(detail=True, methods=["post"], url_path="approve-clinical")
    def approve_clinical(self, request, pk=None):
        with transaction.atomic():
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

            self.mark_dentist_verify(verification)
            return custom_response(
                success=True,
                message="Clinical path verification approved successfully.",
                data=ClinicalPathVerificationSerializer(clinical_obj).data,
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=["post"], url_path="reject-clinical")
    def reject_clinical(self, request, pk=None):
        with transaction.atomic():
            note = request.data.get("note", "Clinical path verification rejected.")
            verification = self.get_object()
            clinical_obj = verification.clinical_path_verification
            if clinical_obj.status == DENTIST_VERIFICATION_STATUS.APPROVED:
                return custom_response(
                    success=False,
                    message="Clinical verification already approved.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            clinical_obj.status = DENTIST_VERIFICATION_STATUS.REJECTED
            clinical_obj.reviewer_notes = note
            clinical_obj.save(update_fields=["status", "reviewer_notes"])
            
            verification.clinical_verification = VERIFICATION_STATUS.REJECT
            verification.save(update_fields=["clinical_verification"])
            return custom_response(
                success=True,
                message="Clinical path verification rejected.",
                data=ClinicalOperationVerificationSerializer(clinical_obj).data,
                status=status.HTTP_200_OK
            )


