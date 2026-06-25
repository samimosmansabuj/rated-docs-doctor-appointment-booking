from django.db import models
from .common_models import TimeStampedModel
from .constants import PROCEDURE_CHOICES, MailConfigType

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
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.country})"

class PostMethodPayloadStore(TimeStampedModel):
    payload = models.JSONField(default=dict)
    payload_text = models.TextField(blank=True, null=True)





class EmailConfig(models.Model):
    type = models.CharField(max_length=25, choices=MailConfigType, default=MailConfigType.SMTP, blank=True, null=True)
    server = models.CharField(blank=True, max_length=50, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    host_user = models.CharField(max_length=255,blank=True, null=True)
    host_password = models.CharField(max_length=255,blank=True, null=True)
    host = models.CharField(max_length=255, blank=True, null=True)
    port = models.CharField(max_length=10, blank=True, null=True)
    tls = models.BooleanField(default=True)
    api_key = models.CharField(max_length=500, blank=True, null=True)
    ssl = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    today_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    daily_limit = models.PositiveIntegerField(blank=True, null=True)
    today_date = models.DateField(blank=True, null=True)
    today_complete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def increase_today_count(self):
        self.today_count+=1
        if self.today_count == self.daily_limit:
            self.today_complete = True
    
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
    
    
    
    def __str__(self):
        return f"{self.email} | {self.host} | LIMIT {self.daily_limit} | Active: {self.is_active}" if self.email else f"{self.server} | {self.api_key}"

