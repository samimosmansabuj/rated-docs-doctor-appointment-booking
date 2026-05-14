from django.db import models
from core.choice_options import USER_ROLE_CHOICES
from core.common_models import TimeStampedModel, SoftDeleteModel
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail

class User(AbstractUser, TimeStampedModel, SoftDeleteModel):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES.choices)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone", "username"]
    
    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()


class PatientProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    country = models.CharField(max_length=100)
    medical_notes = models.TextField(blank=True)





