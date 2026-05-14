from django.db import models
from core.common_models import TimeStampedModel, SoftDeleteModel
from core.choice_options import DENTIST_VERIFICATION_PHASE, WEEK_DAY, DAY_STATUS, APPOINTMENT_SLOT_EXCEPTION_TYPE, DENTIST_VERIFICATION_STATUS, DENTIST_DOCUMENT_TYPE
from rest_framework.exceptions import ValidationError
from account.models import User


class Clinic(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

class DentistProfile(TimeStampedModel, SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="dentist_profile")
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, related_name="dentists")

    full_name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    experience_years = models.IntegerField()
    is_claimed = models.BooleanField(default=False)

    rating_avg = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)

    rdv_score = models.FloatField(default=0)
    response_time_avg = models.FloatField(default=0)

    verification_phase = models.IntegerField(choices=DENTIST_VERIFICATION_PHASE.choices, default=DENTIST_VERIFICATION_PHASE.ONE)
    is_verified = models.BooleanField(default=False)


class DentistWeeklyAvailability(TimeStampedModel):
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="weekly_availability")
    day_of_week = models.CharField(max_length=10, choices=WEEK_DAY.choices)
    day_status = models.CharField(max_length=20, choices=DAY_STATUS.choices, default=DAY_STATUS.AVAILABLE)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("dentist", "day_of_week")    
        indexes = [
            models.Index(fields=["dentist", "day_of_week"]),
        ]

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Invalid time range")

class SlotException(TimeStampedModel):
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="slot_exceptions")
    type = models.CharField(max_length=20, choices=APPOINTMENT_SLOT_EXCEPTION_TYPE.choices, default=APPOINTMENT_SLOT_EXCEPTION_TYPE.BOOKED)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    appointment = models.ForeignKey("appointments.Appointment", on_delete=models.SET_NULL, blank=True, null=True, related_name="slot_exceptions")


class DentistVerification(TimeStampedModel):
    dentist = models.OneToOneField(DentistProfile, on_delete=models.CASCADE, related_name="dentist_verification")
    license_number = models.CharField(max_length=100)
    license_verified = models.BooleanField(default=False)
    identity_verified = models.BooleanField(default=False)
    sterilization_verified = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=DENTIST_VERIFICATION_STATUS.choices, default=DENTIST_VERIFICATION_STATUS.PENDING)
    face_match_score = models.FloatField(null=True)

    verified_at = models.DateTimeField(null=True, blank=True)

class DentistDocument(TimeStampedModel):
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="dentist_documents")
    verification_model = models.ForeignKey(DentistVerification, on_delete=models.SET_NULL, blank=True, null=True, related_name="verification_documents")
    doc_type = models.CharField(max_length=20, choices=DENTIST_DOCUMENT_TYPE.choices)
    file = models.FileField(upload_to="documents/")
    is_verified = models.BooleanField(default=False)


class DentistService(TimeStampedModel):
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="dentist_services")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

