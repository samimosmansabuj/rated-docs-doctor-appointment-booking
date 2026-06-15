from django.db import models
from core.common_models import TimeStampedModel, SoftDeleteModel
from account.models import PatientProfile
from dentist.models import DentistProfile
from core.models import Procedure
from core.constants import VIDEO_SESSION_STATUS, DENTAL_PHOTO_TYPE, SCHEDULE_STATUS, CONSULTATION_STATUS, LAST_VISIT_CHOICE
# from django.db.

class Consultation(TimeStampedModel, SoftDeleteModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="consultations")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="consultations")
    status = models.CharField(max_length=30, choices=CONSULTATION_STATUS.choices, default=CONSULTATION_STATUS.DRAFT)
    treatment_interest = models.ManyToManyField(Procedure, blank=True, null=True)

    # rough_budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    # rough_budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    approximate_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    travel_start_date = models.DateField(null=True, blank=True)
    travel_end_date = models.DateField(null=True, blank=True)

class ConsultationSchedule(TimeStampedModel):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="schedule")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, blank=True, null=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    re_scheduled_at = models.DateTimeField(blank=True, null=True)
    re_scheduled_confirm = models.BooleanField(blank=True, null=True)
    timezone = models.CharField(max_length=50)
    duration_minutes = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=SCHEDULE_STATUS.choices, default=SCHEDULE_STATUS.PENDING)

class ConsultationDentalPhoto(TimeStampedModel):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="dental_photo")
    front_smile = models.ImageField(upload_to="consultation/dental-photo/", blank=True, null=True)
    wide_smile = models.ImageField(upload_to="consultation/dental-photo/", blank=True, null=True)
    lower_arch = models.ImageField(upload_to="consultation/dental-photo/", blank=True, null=True)
    upper_arch = models.ImageField(upload_to="consultation/dental-photo/", blank=True, null=True)
    left_side = models.ImageField(upload_to="consultation/dental-photo/", blank=True, null=True)
    right_side = models.ImageField(upload_to="consultation/dental-photo/", blank=True, null=True)
    notes = models.TextField(blank=True)

class ConsultationXRay(TimeStampedModel):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="xrays")
    file = models.FileField(upload_to="consultation/xrays/")
    notes = models.TextField(blank=True)

class ConsultationDentalHistory(TimeStampedModel):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="dental_history")
    last_dentist_visit = models.CharField(max_length=20, choices=LAST_VISIT_CHOICE.choices, null=True, blank=True)
    conditions = models.JSONField(default=list)
    notes = models.TextField(blank=True)

class VideoConsultationSession(TimeStampedModel):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="video_session")
    meeting_url = models.URLField(blank=True, null=True)
    room_id = models.CharField(max_length=255, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=VIDEO_SESSION_STATUS.choices, default=VIDEO_SESSION_STATUS.SCHEDULED)


class ConsultationChangesRequest(TimeStampedModel):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="changes_request")
    # related_object = 

