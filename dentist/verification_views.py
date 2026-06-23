from core.permissions import IsDentist
from rest_framework.exceptions import ValidationError
from core.utils.response import custom_response
from core.utils.views import OwnAPIView
from dentist.models import ClinicOperationVerification, ClinicalPathVerification, DentistLicenseVerification
from .serializer.serializers import (
    # Submit
    ClinicalOperationVerificationSubmitSerializer, DentistLicenseVerificationSubmitSerializer, ClinicalPathVerificationSubmitSerializer, 
    
    # View
    ClinicalOperationVerificationSerializer, ClinicalPathVerificationSerializer, DentistLicenseVerificationSerializer
)
from .serializer.public import PublicProcedureSerializer
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from django.db import transaction

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
    
    def get_dentist(self):
        if hasattr(self.request.user, "dentist_profile"):
            return self.request.user.dentist_profile
        else:
            raise NotFound("You have no dentist profile.")
    
    def get(self, request, *args, **kwargs):
        try:
            dentist = self.get_dentist()
            instance = DentistLicenseVerification.objects.select_related(
                "dentist",
                "verification",
                "registration_authority"
            ).get(dentist=dentist)
        except DentistLicenseVerification.DoesNotExist:
            return custom_response(
                success=False,
                message="No license verification found.",
                data={
                    "submitted": False,
                    "status": None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except NotFound as e:
            return Response(
                {
                    "success": False,
                    "details": str(e)
                }, status=status.HTTP_404_NOT_FOUND
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
    
    def success_response(self, serializer):
        serializer.save()
        return custom_response(
            success=True,
            message="Operational verification submitted successfully.",
            detail="Phase 2 submitted."
        )

    def get_dentist(self):
        if hasattr(self.request.user, "dentist_profile"):
            return self.request.user.dentist_profile
        else:
            raise NotFound("You have no dentist profile.")
    
    def get(self, request, *args, **kwargs):
        try:
            dentist = self.get_dentist()
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
            ).get(dentist=dentist)
        except ClinicOperationVerification.DoesNotExist:
            return custom_response(
                success=True,
                message="No clinic operation verification found.",
                data={
                    "submitted": False,
                    "status": None
                }
            )
        except NotFound as e:
            return Response(
                {
                    "success": False,
                    "details": str(e)
                }, status=status.HTTP_404_NOT_FOUND
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

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data_copy = request.data.copy()
                # procedures = json.loads(data_copy["procedures"])
                # guarantee = json.loads(data_copy["guarantee"])
                
                # data = {}
                # data["procedures"] = procedures
                # data["guarantee"] = guarantee
                # data["jci_certificate"] = data_copy["jci_certificate"]
                # data["walkthrough_video"] = data_copy["walkthrough_video"]
                
                
                
                print("data: ", data_copy)
                serializer = self.get_serializer(data=data_copy)
                serializer.is_valid(raise_exception=True)
                return self.success_response(serializer)
        except ValidationError as e:
            return self.serializer_error_response(
                serializer=locals().get("serializer"),
                error=e
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "detail": str(e)
                }, status=status.HTTP_400_BAD_REQUEST
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

    def get_dentist(self):
        if hasattr(self.request.user, "dentist_profile"):
            return self.request.user.dentist_profile
        else:
            raise NotFound("You have no dentist profile.")
    
    def get(self, request, *args, **kwargs):
        try:
            dentist = self.get_dentist()
            instance = ClinicalPathVerification.objects.select_related(
                "dentist", "verification", "clinic", "verified_by"
            ).get(dentist=dentist)
        except ClinicalPathVerification.DoesNotExist:
            return custom_response(
                success=True,
                message="No clinical path verification found.",
                data={
                    "submitted": False,
                    "status": None
                }
            )
        except NotFound as e:
            return Response(
                {
                    "success": False,
                    "details": str(e)
                }, status=status.HTTP_404_NOT_FOUND
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

    def post(self, request, *args, **kwargs) -> Response:
        try:
            if self.get_serializer(data=request.data):
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                return self.success_response(serializer)
            return self.success_response()
        except ValidationError as e:
            return self.serializer_error_response(
                serializer=locals().get("serializer"),
                error=e
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "detail": str(e)
                }, status=status.HTTP_400_BAD_REQUEST
            )

class DentistProcedureReadListView(APIView):
    permission_classes = [IsDentist]
    
    def get(self, request, *args, **kwargs):
        dentist_procedure_list = self.request.user.dentist_profile.procedures_feature
        serializer = PublicProcedureSerializer(dentist_procedure_list, many=True)
        data = serializer.data
        return Response(
            {
                "success": True,
                "count": len(data),
                "procedure_list": data
            }, status=status.HTTP_200_OK
        )

