from django.db import models
from .common_models import TimeStampedModel
from .constants import PROCEDURE_CHOICES

# Create your models here.
class Procedure(TimeStampedModel):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="sub_procedures", null=True, blank=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=PROCEDURE_CHOICES.choices, default=PROCEDURE_CHOICES.OBJECTTIVE)
    details = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

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




class PostMethodPayloadStore(TimeStampedModel):
    payload = models.JSONField(default=dict)
    payload_text = models.TextField(blank=True, null=True)



