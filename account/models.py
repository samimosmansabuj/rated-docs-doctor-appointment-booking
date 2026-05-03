from django.db import models
from core.choice_options import USER_ROLE_CHOICES
from core.common_models import TimeStampedModel, SoftDeleteModel

class User(TimeStampedModel, SoftDeleteModel):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES.choices)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()


class PatientProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    country = models.CharField(max_length=100)
    medical_notes = models.TextField(blank=True)





