from django.db import models
from core.constants import USER_ROLE_CHOICES, USER_GENDER, OTP_PURPOSE, PAYMENT_METHOD_TYPE
from core.common_models import TimeStampedModel, SoftDeleteModel
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import transaction

class User(AbstractUser, TimeStampedModel, SoftDeleteModel):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES.choices)
    phone = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

class PatientProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=USER_GENDER)
    country = models.CharField(max_length=100)
    medical_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.email} Patient Profile"

class OTP(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=20, choices=OTP_PURPOSE.choices)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).seconds > 300

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["otp_code"]),
        ]
    
    def __str__(self):
        return f"{self.otp_code} OTP for {self.user.email} | Purpose: {self.purpose} | Verified: {self.is_verified} | Expired: {self.is_expired}"

class UserPaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_methods")
    provider = models.CharField(max_length=50)  # stripe, razorpay
    method_type = models.CharField(max_length=30, choices=PAYMENT_METHOD_TYPE.choices, default=PAYMENT_METHOD_TYPE.CARD)

    payment_token = models.CharField(max_length=255)
    provider_payment_method_id = models.CharField(max_length=255, blank=True, null=True)
    fingerprint = models.CharField(max_length=50, blank=True, null=True)
    expiry_month = models.CharField(max_length=50, blank=True, null=True)
    expiry_year = models.CharField(max_length=50, blank=True, null=True)
    holder_name = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    last4 = models.CharField(max_length=4, blank=True, null=True)
    # optional extra data (non-sensitive only)
    method_data = models.JSONField(blank=True, null=True)

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True),
                name="unique_default_payment_per_user"
            )
        ]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not UserPaymentMethod.objects.filter(user=self.user).exists():
                self.is_default = True
            
            if self.is_default:
                UserPaymentMethod.objects.filter(
                    user=self.user,
                    is_default=True
                ).update(is_default=False)
            super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        with transaction.atomic():
            user = self.user
            is_default = self.is_default
            super().delete(*args, **kwargs)
            if is_default:
                next_method = UserPaymentMethod.objects.filter(user=user).first()
                if next_method:
                    next_method.is_default = True
                    next_method.save()

