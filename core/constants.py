from django.db import models


# Account App Choice Option---
class USER_ROLE_CHOICES(models.TextChoices):
    PATIENT = "Patient"
    DENTIST = "Dentist"
    ADMIN = "Admin"
    STAFF = "Staff"

class USER_GENDER(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Male"

class OTP_PURPOSE(models.TextChoices):
    LOGIN = "LOGIN"
    REGISTER = "REGISTER"
    RESET = "RESET"

class PAYMENT_METHOD_TYPE(models.TextChoices):
    CARD = "CARD"
    BANK = "BANK"
    WALLET = "WALLET"

# Dentist App Choice Option---
class DENTIST_VERIFICATION_PHASE(models.TextChoices):
    ONE = "LICENSE", "License"
    TWO = "OPERATIONAL" "Operational"
    THREE = "CLINICAL" "Clinical"

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
    SUBMITTED = "SUBMITTED", "Submitted"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    APPROVED = "APPROVED", "Approved"
    NEED_MORE_EVIDENCE = "NEED_MORE_EVIDENCE", "Need More Evidence"
    RESUBMIT_REQUIRED = "RESUBMIT_REQUIRED", "Resubmit Required"
    REJECTED = "REJECTED", "Rejected"
    EXPIRED = "EXPIRED", "Expired"

class DENTIST_DOCUMENT_TYPE(models.TextChoices):
    LICENSE = "LICENSE", "License"
    CERTIFICATE = "CERTIFICATE", "Certificate"
    INSURANCE = "INSURANCE", "Insurance"



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

class CONSULTATION_STATUS(models.TextChoices):
    DRAFT = "draft", "Draft"
    INTAKE_IN_PROGRESS = "intake_in_progress", "Intake In Progress"
    PENDING_REVIEW = "pending_review", "Pending Review"
    WAITING_FOR_SCHEDULING = "waiting_for_scheduling", "Waiting for Scheduling"
    SCHEDULED = "scheduled", "Scheduled"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    ESTIMATE_PENDING = "estimate_pending", "Estimate Pending"
    ESTIMATE_RECEIVED = "estimate_received", "Estimate Received"
    CANCELLED = "cancelled", "Cancelled"
    REJECTED = "rejected", "Rejected"

class DENTAL_PHOTO_TYPE(models.TextChoices):
    FRONT_SMILE = "front_smile"
    WIDE_SMILE = "wide_smile"
    LOWER_ARCH = "lower_arch"
    UPPER_ARCH = "upper_arch"
    LEFT_SIDE = "left_side"
    RIGHT_SIDE = "right_side"

class SCHEDULE_STATUS(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    RESCHEDULED = "rescheduled", "Rescheduled"
    CANCELLED = "cancelled", "Cancelled"
    NO_SHOW = "no_show", "No Show"
    COMPLETED = "completed", "Completed"

class VIDEO_SESSION_STATUS(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    WAITING = "waiting", "Waiting"
    IN_CALL = "in_call", "In Call"
    ENDED = "ended", "Ended"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    RECONNECTED = "reconnected", "Reconnected"



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

