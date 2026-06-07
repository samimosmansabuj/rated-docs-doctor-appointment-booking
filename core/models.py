from django.db import models
from .common_models import TimeStampedModel

# Create your models here.
class Procedure(TimeStampedModel):
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    is_active = models.BooleanField(blank=True, null=True)

class LicenseRegistrationAuthority(TimeStampedModel):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "license_registration_authorities"
        verbose_name = "License Registration Authority"
        verbose_name_plural = "License Registration Authorities"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.country})"

