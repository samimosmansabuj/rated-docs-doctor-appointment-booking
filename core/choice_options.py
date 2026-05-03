from django.db import models


# Account App Choice Option---
class USER_ROLE_CHOICES(models.TextChoices):
    PATIENT = "Patient"
    DENTIST = "Dentist"
    ADMIN = "Admin"
    STAFF = "Staff"

# Dentist App Choice Option---
class DENTIST_VERIFICATION_PHASE(models.TextChoices):
    ONE = "Identity"
    TWO = "Operational"
    THREE = "Clinical"

class WEEK_DAY(models.TextChoices):
    SUN = "Sun", "Sunday"
    MON = "Mon", "Monday"
    TUE = "Tue", "Tuesday"
    WED = "Wed", "Wednesday"
    THU = "Thu", "Thursday"
    FRI = "Fri", "Friday"
    SAT = "Sat", "Saturday"

class DAY_STATUS(models.TextChoices):
    AVAILABLE = "AVAILABLE"
    OFF = "OFF"
    UNAVAILABLE = "UNAVAILABLE"

class APPOINTMENT_SLOT_EXCEPTION_TYPE(models.TextChoices):
    BOOKED = "BOOKED"
    UNAVAILABLE = "UNAVAILABLE"
    AVAILABLE = "AVAILABLE"
    FREEZED = "FREEZED"

class DENTIST_VERIFICATION_STATUS(models.TextChoices):
    PENDING = "PENDING"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    REJECT = "REJECT"

class DENTIST_DOCUMENT_TYPE(models.TextChoices):
    LICENSE = "License"
    CERTIFICATE = "Certificate"
    INSURANCE = "Insurance"

# Appointments App Choice Option---
class APPOINTMENT_STATUS_CHOICES(models.TextChoices):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class ESTIMATE_REQUEST_STATUS(models.TextChoices):
    PENDING = "Pending"
    REVIEW = "Review"
    CONFIRMED = "Confirmed"
    REJECT = "Reject"

class PAYMENT_STATUS(models.TextChoices):
    PENDING = "Pending"
    HELD = "Held"
    RELEASED = "Released"
    REFUND = "Refunded"

class REFUND_STATUS(models.TextChoices):
    PENDING = "Pending"
    PROCESSING = "Processing"
    CONFIRM = "Confirm"
    COMPLETE = "Complete"

