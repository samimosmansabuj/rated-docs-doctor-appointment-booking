
from core.utils.response import custom_response
from rest_framework.response import Response
from rest_framework import status
from core.utils.viewsets import OwnReadOnlyModelViewSet
from .consultant_models import Consultation, VideoConsultationSession
from core.constants import CONSULTATION_STATUS, VIDEO_SESSION_STATUS, APPOINTMENT_STATUS, ESCROW_PAYMENT_STATUS, PAYMENT_STATUS, TREATMENT_RESULT_PHOTO_TYPE
from core.permissions import IsPatient, IsAdmin, IsDentist
from rest_framework.decorators import action
from django.db import transaction
from .models import Appointment, EscrowPayment

from .serializers.serializers import (
    CreateRescheduleRequestSerializer,
    
    InitialTreatmentPlanCreateSerializer, AppointmentDecisionSerializer, ArrivalVerificationCreateSerializer, ArrivalCodeVerifySerializer,
    FinalTreatmentPlanCreateSerializer, FinalTreatmentDecisionSerializer, TreatmentResultPhotoSerializer, TreatmentReviewSerializer, PaymentReleaseSerializer, TreatmentCompletionSerializer
)
from .serializers.consultant import ConsultationDetailsSerializer
from .serializers.treatment import AppointmentDetailSerializer
from rest_framework.exceptions import ValidationError
from django.conf import settings


class MyConsultationViewSet(OwnReadOnlyModelViewSet):
    permission_classes = [IsPatient]
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
    
    @action(detail=True, methods=["get"], url_path="estimate-review")
    def estimate_review(self, request, pk=None):
        consultation = self.get_object()
        treatment = consultation.appointment
        serializer = AppointmentDetailSerializer(treatment)
        return Response(
            {
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )
    
    def payment_callback_url(self, payment: EscrowPayment):
        token = f"stripe-token={payment.stripe_subscription_id}"
        platform_transaction_id = f"platform-transaction={payment.transaction_id}"
        payment_details={"tranx_id": "854334d", "amount": 500.00, "currency": "USD"}
        url = f"{settings.FRONTEND_URL}/pay/callback-url/?{token}&{platform_transaction_id}&payment-details={payment_details}"
        return url
    
    def escrow_payment(self, appointment):
        if appointment.status != APPOINTMENT_STATUS.AWAITTING_FOR_PAYMENT:
            raise ValidationError(
                "Appointment is not confirmed."
            )
        if hasattr(appointment, "escrow_payment"):
            payment = appointment.escrow_payment
        else:
            payment, _ = EscrowPayment.objects.get_or_create(
                appointment=appointment,
                patient=self.request.user.patient_profile,
                defaults={
                    "amount": appointment.initial_treatment_plan.total_cost,
                    "currency": "USD",
                    "status": ESCROW_PAYMENT_STATUS.PENDING
                }
            )
        payment_callback_url = self.payment_callback_url(payment)
        return {
            "payment_callback_url": payment_callback_url,
            "stripe_subscription_id": payment.stripe_subscription_id
        }
    
    @estimate_review.mapping.post
    def estimate_review_submit(self, request, pk=None):
        with transaction.atomic():
            consultation = self.get_object()
            appointment = consultation.appointment
            data = request.data.copy()
            data["appointment_id"] = appointment.id
            data["consultation_id"] = consultation.id
            
            serializer = AppointmentDecisionSerializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            appointment.refresh_from_db()
            decision = serializer.validated_data["decision"]
            
            payment_data = self.escrow_payment(appointment)
            return Response(
                {
                    "success": True,
                    "message": f"Treatment plan {decision.lower()} successfully.",
                    "data": payment_data
                },
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=["get"])
    def pay(self, request, pk=None):
        consultation = self.get_object()
        appointment = consultation.appointment
        payment_data = self.escrow_payment(appointment)
        return Response(
            {
                "success": True,
                "data": payment_data
            },
            status=status.HTTP_200_OK
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

class AdminConsultationViewSet(OwnReadOnlyModelViewSet):
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
    
    @action(detail=True, methods=["post"], url_path="create-initial-estimate")
    def create_initial_estimate(self, request, pk=None):
        with transaction.atomic():
            data = request.data.copy()
            data["consultation_id"] = pk
            serializer = InitialTreatmentPlanCreateSerializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Initial Treatment Created"
                }, status=status.HTTP_201_CREATED
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




class PatientAppointmentViewSet(OwnReadOnlyModelViewSet):
    serializer_class = AppointmentDetailSerializer
    permission_classes = [IsPatient]
    
    def get_queryset(self):
        patient = self.request.user.patient_profile
        return Appointment.objects.select_related(
            "consultation", "patient", "dentist",
            "initial_treatment_plan", "final_treatment_plan", "decision", "escrow_payment", "arrival_verification", "final_decision", "release_code",
            "completion", "review", "refund"
        ).prefetch_related(
            "result_photos",
            "initial_treatment_plan__procedures", "initial_treatment_plan__files",
            "final_treatment_plan__procedures", "final_treatment_plan__files",
            "completion__files",
        ).filter(
            patient=patient
        ).order_by("-created_at")
    
    @action(detail=True, methods=["get"], url_path="travel-mark")
    def travel_mark(self, request, pk=None):
        data = {"appointment_id": pk}
        serializer = ArrivalVerificationCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Patient Travel Mark Complete."
            }, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="final-decision")
    def final_decision(self, request, pk=None):
        with transaction.atomic():
            data = request.data.copy()
            data["appointment_id"] = pk
            serializer = FinalTreatmentDecisionSerializer(
                data=data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            decision = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": f"Final treatment decision {decision}."
                }, status=status.HTTP_200_OK
            )

    @action(detail=True, methods=["post"], url_path="result-photo")
    def result_photo(self, request, pk=None):
        with transaction.atomic():
            data = request.data.copy()
            data["appointment_id"] = pk
            data["image_type"] = TREATMENT_RESULT_PHOTO_TYPE.AFTER

            serializer = TreatmentResultPhotoSerializer(
                data=data,
                context={"request": request}
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Result photo uploaded."
                }, status=status.HTTP_200_OK
            )

    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        with transaction.atomic():
            data = request.data.copy()
            data["appointment_id"] = pk

            serializer = TreatmentReviewSerializer(
                data=data,
                context={"request": request}
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Review submitted."
                }, status=status.HTTP_200_OK
            )
    
    @review.mapping.patch
    def review_update(self, request, pk=None):
        with transaction.atomic():
            appointment = self.get_object()
            if hasattr(appointment, "review"):
                review = appointment.review
                serializer = TreatmentReviewSerializer(
                    review,
                    data=request.data,
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response(
                    {
                        "success": True,
                        "message": "Review updated."
                    }, status=status.HTTP_200_OK
                )

class DentistAppointmentViewSet(OwnReadOnlyModelViewSet):
    serializer_class = AppointmentDetailSerializer
    permission_classes = [IsDentist]

    def get_queryset(self):
        dentist = self.request.user.dentist_profile
        return Appointment.objects.select_related(
            "consultation", "patient", "dentist",
            "initial_treatment_plan", "final_treatment_plan", "decision", "escrow_payment", "arrival_verification", "final_decision", "release_code",
            "completion", "review", "refund"
        ).prefetch_related(
            "result_photos",
            "initial_treatment_plan__procedures", "initial_treatment_plan__files",
            "final_treatment_plan__procedures", "final_treatment_plan__files",
            "completion__files",
        ).filter(
            dentist=dentist
        ).order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="arrival-confirm")
    def arrival_confirm(self, request, pk=None):
        with transaction.atomic():
            data = request.data.copy()
            data["appointment_id"] = pk
            serializer = ArrivalCodeVerifySerializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Patient Arrival Confirm."
                }
            )

    @action(detail=True, methods=["post"], url_path="final-treatment-plan")
    def final_treatment_plan(self, request, pk=None):
        with transaction.atomic():
            data = request.data.copy()
            data["appointment_id"] = pk
            serializer = FinalTreatmentPlanCreateSerializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Initial Treatment Created"
                }, status=status.HTTP_201_CREATED
            )

    @action(detail=True, methods=["post"], url_path="release-payment")
    def release_payment(self, request, pk=None):
        with transaction.atomic():
            data = request.data.copy()
            data["appointment_id"] = pk

            serializer = PaymentReleaseSerializer(
                data=data,
                context={"request": request}
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Payment released successfully."
                }
            )

    @action(detail=True, methods=["post"], url_path="complete-treatment")
    def complete_treatment(self, request, pk=None):
        with transaction.atomic():
            print(request.data)
            print(request.FILES)

            data = request.data.copy()
            data["appointment_id"] = pk

            serializer = TreatmentCompletionSerializer(
                data=data,
                context={"request": request}
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Treatment completed successfully."
                }
            )

class AdminAppointmentViewSet(OwnReadOnlyModelViewSet):
    serializer_class = AppointmentDetailSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        return Appointment.objects.select_related(
            "consultation", "patient", "dentist",
            "initial_treatment_plan", "final_treatment_plan", "decision", "escrow_payment", "arrival_verification", "final_decision", "release_code",
            "completion", "review", "refund"
        ).prefetch_related(
            "result_photos",
            "initial_treatment_plan__procedures", "initial_treatment_plan__files",
            "final_treatment_plan__procedures", "final_treatment_plan__files",
            "completion__files",
        ).order_by("-created_at")


