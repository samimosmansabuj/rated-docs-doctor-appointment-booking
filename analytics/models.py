from django.db import models
from core.common_models import TimeStampedModel
from dentist.models import DentistProfile
from account.models import PatientProfile, User

# Create your models here.
class RDVScoreLog(TimeStampedModel):
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="rdv_score_logs")
    score = models.FloatField()

class RecommendationLog(TimeStampedModel):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="recommendation_log")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="recommendation_log")
    score = models.FloatField()

class EventLog(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_logs")
    event_type = models.CharField(max_length=100)
    metadata = models.JSONField()


