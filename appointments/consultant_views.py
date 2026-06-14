from core.utils.response import custom_response
from core.utils.viewsets import OwnReadOnlyModelViewSet
from .consultant_models import Consultation
from core.constants import CONSULTATION_STATUS
from core.permissions import IsPatient
from rest_framework.permissions import IsAuthenticated
from core.utils.views import OwnAPIView
from .serializers import (
    ConsultationPatientInfoSerializer, ConsultationTreatmentInterestSerializer, ConsultationBudgetTravelSerializer,
    ConsultationDentalHistorySerializer, ConsultationDentalPhotoSerializer, ConsultationXraySerializer,
    ConsultationScheduleSerializer, ConsultationDetailsSerializer
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
    serializer_class = ConsultationTreatmentInterestSerializer

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
        serializer.save()
        return custom_response(
            success=True,
            message="Added your treatment interest procedure."
        )

class ConsultationBudgetTravelAPIView(ConsultationMixin, OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationBudgetTravelSerializer

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
        serializer.save()
        return custom_response(
            success=True,
            message="Update Budget and Travel Time."
        )

class ConsultationDentalHistoryAPIView(ConsultationMixin, OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationDentalHistorySerializer

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
        serializer.save()
        return custom_response(
            success=True,
            message="Update Dental History."
        )

class ConsultationDentalPhotoAPIView(ConsultationMixin, OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationDentalPhotoSerializer

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
    serializer_class = ConsultationXraySerializer

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
        serializer.save()
        return custom_response(
            success=True,
            message=f"X-ray Report uploaded successfully.",
        )

class ConsultationScheduleAPIView(OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationScheduleSerializer

    def success_response(self, serializer):
        consultations = serializer.save()

        return custom_response(
            success=True,
            message=f"{len(consultations)} Consultation request submitted successfully.",
            # data={
            #     "total_requests": len(consultations),
            #     "consultation_ids": [
            #         str(obj.id)
            #         for obj in consultations
            #     ]
            # }
        )


class MyConsultationViewSet(OwnReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConsultationDetailsSerializer

    def get_queryset(self):
        return (
            Consultation.objects
            .filter(
                patient__user=self.request.user
            )
            .select_related(
                "patient__user", "dentist__user", "schedule", "dental_photo", "xrays", "dental_history", "video_session",
            )
            .prefetch_related(
                "treatment_interest",
            )
            .order_by("-created_at")
        )


