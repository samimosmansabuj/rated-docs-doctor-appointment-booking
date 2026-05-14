from django.db import models
from core.common_models import TimeStampedModel, SoftDeleteModel
from account.models import PatientProfile
from dentist.models import DentistProfile
from core.choice_options import ESTIMATE_REQUEST_STATUS, APPOINTMENT_STATUS_CHOICES, PAYMENT_STATUS, REFUND_STATUS

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
