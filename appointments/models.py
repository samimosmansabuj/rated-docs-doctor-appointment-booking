from django.db import models
from core.common_models import TimeStampedModel, SoftDeleteModel
from account.models import PatientProfile
from dentist.models import DentistProfile
from core.constants import ESTIMATE_REQUEST_STATUS, APPOINTMENT_STATUS_CHOICES, PAYMENT_STATUS, REFUND_STATUS
from .consultant_models import Consultation
from core.models import Procedure


class TREATMENT_PLAN_STAGE(models.TextChoices):
    INITIAL = "INITIAL", "Initial"
    FINAL = "FINAL", "Final"

class APPOINTMENT_STATUS(models.TextChoices):

    AWAITING_RESPONSE = (
        "awaiting_response",
        "Awaiting Response"
    )

    REJECTED = (
        "rejected",
        "Rejected"
    )

    CONFIRMED = (
        "confirmed",
        "Confirmed"
    )

    IN_PROGRESS = (
        "in_progress",
        "In Progress"
    )

    COMPLETED = (
        "completed",
        "Completed"
    )

    CANCELLED = (
        "cancelled",
        "Cancelled"
    )

class PAYMENT_STATUS(models.TextChoices):

    PENDING = "pending", "Pending"

    IN_ESCROW = "in_escrow", "In Escrow"

    RELEASED = "released", "Released"

    REFUNDED = "refunded", "Refunded"

    PARTIAL_REFUND = (
        "partial_refund",
        "Partial Refund"
    )

class TreatmentPlan(TimeStampedModel, SoftDeleteModel):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="treatment_plans")
    version = models.CharField(max_length=20, choices=TREATMENT_PLAN_STAGE.choices)
    created_by = models.ForeignKey(DentistProfile, on_delete=models.SET_NULL, null=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    other_information = models.TextField(blank=True)
    is_patient_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

class TreatmentPlanProcedure(TimeStampedModel, SoftDeleteModel):
    treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.CASCADE, related_name="procedures")
    procedure = models.ForeignKey(Procedure, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)

class TreatmentPlanFile(TimeStampedModel, SoftDeleteModel):
    treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="treatment-plan/files/")
    title = models.CharField(max_length=255)


class Appointment(TimeStampedModel):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="appointment")
    patient = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name="appointment")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name="appointment")
    
    appointment_date = models.DateField(null=True, blank=True)
    appointment_time = models.TimeField(null=True, blank=True)

    initial_treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.PROTECT, related_name="initial_appointments")
    final_treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="final_appointments")

    status = models.CharField(max_length=30, choices=APPOINTMENT_STATUS.choices, default=APPOINTMENT_STATUS.AWAITING_RESPONSE)

class AppointmentDecision(TimeStampedModel):
    appointment = models.OneToOneField(Appointment,on_delete=models.CASCADE,related_name="decision")

    decision = models.CharField(
        max_length=20,
        choices=[
            ("approved", "Approved"),
            ("rejected", "Rejected")
        ]
    )

    note = models.TextField(blank=True)

    signature_image = models.ImageField(
        upload_to="signatures/",
        null=True,
        blank=True
    )

    decided_at = models.DateTimeField(auto_now_add=True)


class EscrowPayment(TimeStampedModel):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="escrow_payment"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=10,
        default="USD"
    )

    status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS.choices,
        default=PAYMENT_STATUS.PENDING
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

class ArrivalVerification(TimeStampedModel):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="arrival_verification"
    )

    arrival_code = models.CharField(
        max_length=20,
        unique=True
    )

    verified_by = models.ForeignKey(
        DentistProfile,
        on_delete=models.SET_NULL,
        null=True
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

class FinalTreatmentDecision(TimeStampedModel):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="final_decision"
    )

    decision = models.CharField(
        max_length=20,
        choices=[
            ("approved", "Approved"),
            ("rejected", "Rejected")
        ]
    )

    rejection_reason = models.TextField(
        blank=True
    )

    extra_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    refund_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

class PaymentReleaseCode(TimeStampedModel):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="release_code"
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    verified = models.BooleanField(
        default=False
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )


class TreatmentCompletion(TimeStampedModel):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="completion"
    )

    notes = models.TextField(blank=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )


class TreatmentCompletionFile(TimeStampedModel):
    completion = models.ForeignKey(
        TreatmentCompletion,
        on_delete=models.CASCADE,
        related_name="files"
    )

    file = models.FileField(
        upload_to="treatment/completion/"
    )

    title = models.CharField(
        max_length=255
    )


class TreatmentResultPhoto(TimeStampedModel):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="result_photos"
    )

    image = models.ImageField(
        upload_to="treatment-results/"
    )

    image_type = models.CharField(
        max_length=20,
        choices=[
            ("before", "Before"),
            ("after", "After")
        ]
    )


class TreatmentReview(TimeStampedModel):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="review"
    )

    communication = models.PositiveSmallIntegerField()

    value_for_money = models.PositiveSmallIntegerField()

    follow_through = models.PositiveSmallIntegerField()

    review_text = models.TextField(blank=True)

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )


















class EstimateRequest(TimeStampedModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="estimate_requests")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="estimate_requests")

    description = models.TextField()
    status = models.CharField(max_length=20, choices=ESTIMATE_REQUEST_STATUS.choices, default=ESTIMATE_REQUEST_STATUS.PENDING)

class EstimateResponse(TimeStampedModel):
    request = models.OneToOneField(EstimateRequest, on_delete=models.CASCADE, related_name="estimate_response")

    treatment_plan = models.TextField()
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)



class Appointment(TimeStampedModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="appointments")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="appointments")
    estimate = models.ForeignKey(EstimateResponse, on_delete=models.SET_NULL, null=True, related_name="appointments")

    appointment_date = models.DateField()
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS_CHOICES.choices, default=APPOINTMENT_STATUS_CHOICES.PENDING)
    is_video = models.BooleanField(default=False)

    meeting_link = models.URLField(null=True, blank=True)

class Payment(TimeStampedModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="payments")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS.choices, default=PAYMENT_STATUS.PENDING)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    stripe_payment_intent = models.CharField(max_length=255)
    payment_details = models.JSONField(blank=True, null=True)

class Refund(TimeStampedModel):
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, blank=True, null=True, related_name="refunds")
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="refunds")
    status = models.CharField(max_length=20, choices=REFUND_STATUS.choices, default=REFUND_STATUS.PENDING)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    payment_details = models.JSONField(blank=True, null=True)

class Review(TimeStampedModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="reviews")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="reviews")

    rating = models.IntegerField()
    comment = models.TextField()

    # sentiment_score = models.FloatField(default=0)
    # is_flagged = models.BooleanField(default=False)
