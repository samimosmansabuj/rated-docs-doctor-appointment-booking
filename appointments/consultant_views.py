from core.utils.response import custom_response
from core.utils.viewsets import OwnReadOnlyModelViewSet
from .consultant_models import Consultation, VideoConsultationSession
from core.constants import CONSULTATION_STATUS, VIDEO_SESSION_STATUS
from core.permissions import IsPatient, IsAdmin, IsDentist
from rest_framework.permissions import IsAuthenticated
from core.utils.views import OwnAPIView
from .serializers import (
    ConsultationPatientInfoSerializer, ConsultationTreatmentInterestStep2Serializer, ConsultationBudgetTravelStep3Serializer,
    ConsultationDentalHistoryStep4Serializer, ConsultationDentalPhotoStep5Serializer, ConsultationXrayStep6Serializer, ConsultationScheduleStep7Serializer,
    
    ConsultationDetailsSerializer, CreateRescheduleRequestSerializer
)
from django.utils import timezone
from rest_framework.decorators import action


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
        serializer.save()
        return custom_response(
            success=True,
            message="Added your treatment interest procedure."
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
        serializer.save()
        return custom_response(
            success=True,
            message="Update Budget and Travel Time."
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
        serializer.save()
        return custom_response(
            success=True,
            message="Update Dental History."
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
        serializer.save()
        return custom_response(
            success=True,
            message=f"X-ray Report uploaded successfully.",
        )

class ConsultationScheduleAPIView(OwnAPIView):
    permission_classes = [IsPatient]
    serializer_class = ConsultationScheduleStep7Serializer

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
    
    @action(detail=True, methods=["post"], url_path="re-schedule")
    def re_schedule(self, request, pk=None):
        data = request.data.copy()
        data["consultation_id"] = pk
        serializer = CreateRescheduleRequestSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return custom_response(
            success=True,
            message="Reschedule request submitted."
        )

class ConsultationViewSet(OwnReadOnlyModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = ConsultationDetailsSerializer

    queryset = (
        Consultation.objects
        .select_related(
            "patient__user", "dentist__user", "schedule", "dental_photo", "xrays", "dental_history", "video_session",
        )
        .prefetch_related(
            "treatment_interest",
        )
        .order_by("-created_at")
    )

class DentistConsultationViewSet(OwnReadOnlyModelViewSet):
    permission_classes = [IsDentist]
    serializer_class = ConsultationDetailsSerializer

    def get_queryset(self):
        dentist = self.request.user.dentist_profile

        return (
            Consultation.objects
            .filter(
                dentist=dentist
            )
            .select_related(
                "patient__user", "dentist__user", "schedule", "dental_photo", "xrays", "dental_history", "video_session",
            )
            .prefetch_related(
                "treatment_interest",
            )
            .order_by("-created_at")
        )
    
    @action(detail=True, methods=["post"], url_path="create-estimate")
    def create_estimate(self, request, pk=None):
        return custom_response(
            success=True,
            message="Estimate Create successfully."
        ) 
    
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        consultation = self.get_object()
        consultation.status = CONSULTATION_STATUS.SCHEDULED
        consultation.save(update_fields=["status"])
        VideoConsultationSession.objects.get_or_create(
            consultation=consultation,
            defaults={
                "status": VIDEO_SESSION_STATUS.SCHEDULED
            }
        )
        return custom_response(
            success=True,
            message="Consultation accepted successfully."
        )
