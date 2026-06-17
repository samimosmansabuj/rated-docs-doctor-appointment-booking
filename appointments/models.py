from django.db import models
from core.common_models import TimeStampedModel, SoftDeleteModel
from account.models import PatientProfile
from dentist.models import DentistProfile
from core.constants import TREATMENT_PLAN_STAGE, APPOINTMENT_DECISION, FINAL_TREATMENT_DECISION_STATUS, TREATMENT_RESULT_PHOTO_TYPE, APPOINTMENT_STATUS, PAYMENT_STATUS, REFUND_STATUS, REFUND_TYPE, REFUND_REASON
from .consultant_models import Consultation
from core.models import Procedure
import uuid


# Treatment Plan Estimate Plan Models--------
class TreatmentPlan(TimeStampedModel, SoftDeleteModel):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="treatment_plans")
    created_by = models.ForeignKey(DentistProfile, on_delete=models.SET_NULL, null=True, related_name="treatment_plans")
    version = models.CharField(max_length=20, choices=TREATMENT_PLAN_STAGE.choices)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
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

# Appointment Booked and Details Models--------
class Appointment(TimeStampedModel):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="appointment")
    patient = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name="appointment")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name="appointment")
    
    status = models.CharField(max_length=30, choices=APPOINTMENT_STATUS.choices, default=APPOINTMENT_STATUS.AWAITING_RESPONSE)
    appointment_date = models.DateField(null=True, blank=True)
    appointment_time = models.TimeField(null=True, blank=True)

    initial_treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.PROTECT, related_name="initial_appointments")
    final_treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="final_appointments")

class AppointmentDecision(TimeStampedModel):
    appointment = models.OneToOneField(Appointment,on_delete=models.CASCADE,related_name="decision")
    decision = models.CharField(max_length=20, choices=APPOINTMENT_DECISION.choices)
    note = models.TextField(blank=True)
    signature_image = models.ImageField(upload_to="signatures/", null=True, blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

class EscrowPayment(TimeStampedModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="escrow_payment")
    patient = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name="payments")
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=30, choices=PAYMENT_STATUS.choices, default=PAYMENT_STATUS.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_provider = models.CharField(max_length=50, blank=True, null=True)
    payment_details = models.JSONField(default=dict)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    
    provider_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)

    invoice_url = models.CharField(max_length=255, blank=True, null=True)
    receipt_url = models.CharField(max_length=255, blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"PAY-{uuid.uuid4()}"
        if not self.stripe_subscription_id:
            self.stripe_subscription_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

class ArrivalVerification(TimeStampedModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="arrival_verification")
    arrival_code = models.CharField(max_length=20, unique=True)
    verified_by = models.ForeignKey(DentistProfile, on_delete=models.SET_NULL, null=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

class FinalTreatmentDecision(TimeStampedModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="final_decision")
    decision = models.CharField(max_length=20, choices=FINAL_TREATMENT_DECISION_STATUS.choices)
    rejection_reason = models.TextField(blank=True)
    extra_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class PaymentReleaseCode(TimeStampedModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="release_code")
    code = models.CharField(max_length=20, unique=True)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

class TreatmentCompletion(TimeStampedModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="completion")
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class TreatmentCompletionFile(TimeStampedModel):
    completion = models.ForeignKey(TreatmentCompletion, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="treatment/completion/")

class TreatmentResultPhoto(TimeStampedModel):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="result_photos")
    image = models.ImageField(upload_to="treatment-results/")
    image_type = models.CharField(max_length=20, choices=TREATMENT_RESULT_PHOTO_TYPE.choices)

class TreatmentReview(TimeStampedModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="review")
    patient = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name="treatment_review")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name="treatment_review")
    communication = models.PositiveSmallIntegerField()
    value_for_money = models.PositiveSmallIntegerField()
    follow_through = models.PositiveSmallIntegerField()
    review_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    sentiment_score = models.FloatField(default=0)
    is_flagged = models.BooleanField(default=False)

class AppointmentRefund(TimeStampedModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="refund")
    # escrow_payment = models.ForeignKey(EscrowPayment, on_delete=models.PROTECT, related_name="refunds")
    escrow_payment = models.OneToOneField(EscrowPayment, on_delete=models.PROTECT, related_name="refund")
    
    refund_type = models.CharField(max_length=20, choices=REFUND_TYPE.choices)
    reason = models.CharField(max_length=100, choices=REFUND_REASON.choices)
    
    initial_budget = models.DecimalField(max_digits=12, decimal_places=2)
    final_budget = models.DecimalField(max_digits=12, decimal_places=2)
    percentage_difference = models.DecimalField(max_digits=5, decimal_places=2)
    rejection_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rejection_fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=REFUND_STATUS.choices, default=REFUND_STATUS.REQUESTED)
    processed_at = models.DateTimeField(null=True, blank=True)
    admin_note = models.TextField(blank=True)














