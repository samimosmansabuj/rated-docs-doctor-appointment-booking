from core.utils.response import custom_response
from .consultant_models import Consultation
from rest_framework.response import Response
from rest_framework import status
from core.constants import CONSULTATION_STATUS
from core.permissions import IsPatient
from core.utils.views import OwnAPIView, APIView
from .serializers.serializers import (
    ConsultationPatientInfoSerializer, ConsultationTreatmentInterestStep2Serializer, ConsultationBudgetTravelStep3Serializer,
    ConsultationDentalHistoryStep4Serializer, ConsultationDentalPhotoStep5Serializer, ConsultationXrayStep6Serializer, ConsultationScheduleStep7Serializer,
)


class ConsultationMixin:
    def get_consultation(self, patient):
        consultation, _ = Consultation.objects.get_or_create(
            patient=patient,
            status=CONSULTATION_STATUS.DRAFT
        )
        return consultation


class ConsultationPatientInfoAPIView(OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationPatientInfoSerializer

    def get(self, request):
        user = request.user
        patient = user.patient_profile

        return custom_response(
            success=True,
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "date_of_birth": patient.date_of_birth,
                "country": patient.country
            }
        )

    def success_response(self, serializer):
        consultation = serializer.save()
        return custom_response(
            success=True,
            data=consultation,
            message="Patient Info Save."
        )

class ConsultationTreatmentInterestAPIView(ConsultationMixin, OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationTreatmentInterestStep2Serializer

    def get(self, request):
        user = request.user
        patient = user.patient_profile

        return custom_response(
            success=True,
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "date_of_birth": patient.date_of_birth,
                "country": patient.country
            }
        )

    def success_response(self, serializer):
        consultation = serializer.save()
        return custom_response(
            success=True,
            message="Added your treatment interest procedure.",
            data={
                "consultation_id": consultation.id
            }
        )

class ConsultationBudgetTravelAPIView(ConsultationMixin, OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationBudgetTravelStep3Serializer

    def get(self, request):
        user = request.user
        patient = user.patient_profile
        return custom_response(
            success=True,
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "date_of_birth": patient.date_of_birth,
                "country": patient.country
            }
        )

    def success_response(self, serializer):
        consultation = serializer.save()
        return custom_response(
            success=True,
            message="Update Budget and Travel Time.",
            data={
                "consultation_id": consultation.id
            }
        )

class ConsultationDentalHistoryAPIView(ConsultationMixin, OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationDentalHistoryStep4Serializer

    def get(self, request):
        user = request.user
        patient = user.patient_profile
        return custom_response(
            success=True,
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "date_of_birth": patient.date_of_birth,
                "country": patient.country
            }
        )

    def success_response(self, serializer):
        consultation = serializer.save()
        return custom_response(
            success=True,
            message="Update Dental History.",
            data={
                "consultation_id": consultation.id
            }
        )

class ConsultationDentalPhotoAPIView(ConsultationMixin, OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationDentalPhotoStep5Serializer

    def get(self, request):
        user = request.user
        patient = user.patient_profile
        return custom_response(
            success=True,
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "date_of_birth": patient.date_of_birth,
                "country": patient.country
            }
        )

    def success_response(self, serializer):
        result = serializer.save()
        return custom_response(
            success=True,
            message=f"{result} Dental photos uploaded successfully.",
        )

class ConsultationXrayAPIView(ConsultationMixin, OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationXrayStep6Serializer

    def get(self, request):
        user = request.user
        patient = user.patient_profile
        return custom_response(
            success=True,
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "date_of_birth": patient.date_of_birth,
                "country": patient.country
            }
        )

    def success_response(self, serializer):
        consultation = serializer.save()
        return custom_response(
            success=True,
            message=f"X-ray Report uploaded successfully.",
            data={
                "consultation_id": consultation.id
            }
        )

class ConsultationScheduleAPIView(OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationScheduleStep7Serializer

    def success_response(self, serializer):
        consultations = serializer.save()

        return custom_response(
            success=True,
            message=f"{len(consultations)} Consultation request submitted successfully.",
        )

class ConsultationGetAPIView(APIView):
    permission_classes = [IsPatient]
    
    def get(self,request, *args, **kwargs):
        patient = self.request.user.patient_profile
        consultation, _ = Consultation.objects.get_or_create(
            patient=patient,
            status=CONSULTATION_STATUS.DRAFT
        )
        if consultation:
            return Response(
                {
                    "success": True,
                    "consultation": {
                        "id": consultation.id
                    }
                }, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "success": True,
                    "consultation": None
                }, status=status.HTTP_200_OK
            )


