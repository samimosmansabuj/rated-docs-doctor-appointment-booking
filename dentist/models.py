from django.db import models
from core.common_models import TimeStampedModel, SoftDeleteModel
from core.constants import DENTIST_VERIFICATION_PHASE, WEEK_DAY, DAY_STATUS, APPOINTMENT_SLOT_EXCEPTION_TYPE, DENTIST_VERIFICATION_STATUS, DENTIST_DOCUMENT_TYPE
from rest_framework.exceptions import ValidationError
from account.models import User
from core.models import LicenseRegistrationAuthority, Procedure


class Clinic(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

class DentistProfile(TimeStampedModel, SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="dentist_profile")
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, blank=True, related_name="dentists")

    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    specialty = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    experience_years = models.IntegerField()
    is_claimed = models.BooleanField(default=False)

    rating_avg = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)

    rdv_score = models.FloatField(default=0)
    response_time_avg = models.FloatField(default=0)

    verification_phase = models.IntegerField(choices=DENTIST_VERIFICATION_PHASE.choices, default=DENTIST_VERIFICATION_PHASE.ONE)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email} Dentist Profile"

class DentistAddress(TimeStampedModel, SoftDeleteModel):
    profile = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="dentist_address")
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

# =====================================================================
# ------------------------Dentist Availability------------------------
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

# ------------------------Dentist Availability------------------------
# =====================================================================

# =====================================================================
# ------------------------Dentist Verification------------------------
class DentistVerification(TimeStampedModel):
    dentist = models.OneToOneField(DentistProfile, on_delete=models.CASCADE, related_name="dentist_verification")
    License_verification = models.BooleanField(default=False)
    operations_verification = models.BooleanField(default=False)
    clinical_verification = models.BooleanField(default=False)

    face_match_score = models.FloatField(null=True)

# License Verification Phase-----
class DentistLicenseVerification(TimeStampedModel):
    dentist = models.OneToOneField(DentistProfile, on_delete=models.CASCADE, related_name="dentist_license_verification")
    verification = models.OneToOneField(DentistVerification, on_delete=models.CASCADE, related_name="dentist_license_verification")
    
    # general field---
    professional_headshot = models.ImageField(upload_to="documents/headshot/", blank=True, null=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    registration_authority = models.ForeignKey(LicenseRegistrationAuthority, on_delete=models.SET_NULL, blank=True, null=True, related_name="dentist_license")
    registration_no = models.CharField(max_length=100)
    doc_type = models.CharField(max_length=20, choices=DENTIST_DOCUMENT_TYPE.choices)
    file = models.FileField(upload_to="documents/license/", blank=True, null=True)
    
    # Update field---
    status = models.CharField(max_length=20, choices=DENTIST_VERIFICATION_STATUS.choices, default=DENTIST_VERIFICATION_STATUS.SUBMITTED)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    reviewer_notes = models.TextField(blank=True)

# Clinical Operation Verification Phase-----
class ClinicOperationVerification(TimeStampedModel):
    clinic = models.OneToOneField(Clinic, on_delete=models.CASCADE, related_name="operation_verification")
    dentist = models.OneToOneField(DentistProfile, on_delete=models.CASCADE, related_name="operation_verification")
    verification = models.OneToOneField(DentistVerification, on_delete=models.CASCADE, related_name="operation_verification")

    # Update field---
    status = models.CharField(max_length=20, choices=DENTIST_VERIFICATION_STATUS.choices, default=DENTIST_VERIFICATION_STATUS.SUBMITTED)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey("account.User" ,null=True, blank=True, on_delete=models.SET_NULL)
    reviewer_notes = models.TextField(blank=True)

# Sterilization
class SterilizationVerification(TimeStampedModel):
    operation_verification = models.OneToOneField(ClinicOperationVerification, on_delete=models.CASCADE, related_name="sterilization_verification")
    has_jci_certificate = models.BooleanField(default=False)
    jci_certificate = models.FileField(upload_to="documents/jci/", blank=True, null=True)
    certificate_number = models.CharField(max_length=255, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issuing_authority = models.CharField(blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)

class SterilizationWalkthrough(TimeStampedModel):
    sterilization = models.OneToOneField(SterilizationVerification, on_delete=models.CASCADE, related_name="walkthrough")
    walkthrough_video = models.FileField(upload_to="documents/sterilization-videos/", blank=True, null=True)
    autoclave_brand = models.CharField(max_length=255)
    sealed_pouch_visible = models.BooleanField(default=False)
    ultrasonic_cleaner_available = models.BooleanField(default=False)
    cycle_frequency = models.CharField(max_length=255)

# Procedure Price
class ProcedurePrice(TimeStampedModel):
    operation_verification = models.ForeignKey(ClinicOperationVerification, on_delete=models.CASCADE, related_name="procedures_feature")
    dentist = models.ForeignKey(DentistProfile, on_delete=models.CASCADE, related_name="procedures_feature")
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="dentist_procedures_feature")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    option_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["dentist", "procedure"],
                name="unique_dentist_procedure_price"
            )
        ]
        
# No Surprise Guarantee
class NoSurpriseGuarantee(TimeStampedModel):
    operation_verification = models.OneToOneField(ClinicOperationVerification, on_delete=models.CASCADE, related_name="no_surprise_guarantee")
    allowed_variation_percent = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    signer_name = models.CharField(max_length=255)
    typed_signature = models.CharField(max_length=255)
    accepted_terms = models.BooleanField(default=False)
    signed_at = models.DateTimeField(auto_now_add=True)

# Clinical Procedure Verification Phase-----
class ClinicalPathVerification(TimeStampedModel):
    # Relation Field---
    clinic = models.OneToOneField(Clinic, on_delete=models.CASCADE, related_name="clinical_path_verification")
    dentist = models.OneToOneField(DentistProfile, on_delete=models.CASCADE, related_name="clinical_path_verification")
    verification = models.OneToOneField(DentistVerification, on_delete=models.CASCADE, related_name="clinical_path_verification")
    
    # Update field---
    reviewer = models.ForeignKey("account.User",on_delete=models.SET_NULL,null=True,blank=True,related_name="clinical_reviews")
    status = models.CharField(max_length=20, choices=DENTIST_VERIFICATION_STATUS.choices, default=DENTIST_VERIFICATION_STATUS.SUBMITTED)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(DentistProfile ,null=True, blank=True, on_delete=models.SET_NULL)
    reviewer_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "clinical_path_verifications"

# Procedure Material 
class ProcedureMaterialVerification(TimeStampedModel):
    clinical_path = models.ForeignKey(ClinicalPathVerification, on_delete=models.CASCADE, related_name="procedure_material_verifications")
    own_procedure = models.ForeignKey(ProcedurePrice, on_delete=models.CASCADE, related_name="procedure_material_verifications")
    brand_name = models.CharField(max_length=255)

    ce_certificate = models.FileField(upload_to="documents/material-document/", blank=True, null=True)
    material_brands = models.FileField(upload_to="documents/material-document/", blank=True, null=True)
    invoice = models.FileField(upload_to="documents/material-document/", blank=True, null=True)
    protocol_pdf = models.FileField(upload_to="documents/material-document/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "procedure_material_verification"

# ------------------------Dentist Verification------------------------
# =====================================================================




