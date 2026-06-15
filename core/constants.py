from django.db import models


# Account App Choice Option---
class USER_ROLE_CHOICES(models.TextChoices):
    PATIENT = "PATIENT", "Patient"
    DENTIST = "DENTIST", "Dentist"
    ADMIN = "ADMIN", "Admin"
    STAFF = "STAFF", "Staff"

class USER_GENDER(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"

class OTP_PURPOSE(models.TextChoices):
    LOGIN = "LOGIN"
    REGISTER = "REGISTER"
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    RESET = "RESET"

class PAYMENT_METHOD_TYPE(models.TextChoices):
    CARD = "CARD"
    BANK = "BANK"
    WALLET = "WALLET"

# Dentist App Choice Option---
class DENTIST_SPECIALTY(models.TextChoices):
    PERIODONTIST = "PERIODONTIST", "Periodontist"
    DENTIST = "DENTIST", "Dentist"
    SURGEON = "SURGEON", "Surgeon"

class DENTIST_VERIFICATION_PHASE(models.TextChoices):
    ONE = "LICENSE", "License"
    TWO = "OPERATIONAL", "Operational"
    THREE = "CLINICAL", "Clinical"
    COMPLETE = "COMPLETE", "Complete"

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


# Log and Notification App Choice Option---
class NOTIFICATION_FOR(models.TextChoices):
    USER = "USER", "User"
    ADMIN = "ADMIN", "Admin"
    STAFF = "STAFF", "Staff"

class LogStatus(models.TextChoices):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

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
    # WAITING_FOR_SCHEDULING = "waiting_for_scheduling", "Waiting for Scheduling"
    SCHEDULED = "scheduled", "Scheduled"
    COMPLETED = "completed", "Completed"
    ESTIMATE_PENDING = "estimate_pending", "Estimate Pending"
    ESTIMATE_RECEIVED = "estimate_received", "Estimate Received"
    CANCELLED = "cancelled", "Cancelled"
    REJECTED = "rejected", "Rejected"

class LAST_VISIT_CHOICE(models.TextChoices):
    MONTH_6 = "MONTH_6", "Less than 6 month age"
    MONTH_12 = "MONTH_12", "6-2 month age"
    MONTH_OVER_12 = "MONTH_OVER_12", "over a year age"

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
    NO_SHOW = "no_show", "No Show"

class RESCHEDULE_REQUEST_STATUS(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"


class TREATMENT_PLAN_STAGE(models.TextChoices):
    INITIAL = "INITIAL", "Initial"
    FINAL = "FINAL", "Final"

class APPOINTMENT_DECISION(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"

class FINAL_TREATMENT_DECISION_STATUS(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"

class TREATMENT_RESULT_PHOTO_TYPE(models.TextChoices):
    BEFORE = "BEFORE", "Before"
    AFTER = "AFTER", "After"

class APPOINTMENT_STATUS(models.TextChoices):
    AWAITING_RESPONSE = "AWAITING_RESPONSE", "Awaiting Response"
    REJECTED = "REJECTED", "Rejected"
    CONFIRMED = "CONFIRMED", "Confirmed"
    ARRIVED = "ARRIVED", "Arrived"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    PAYMENT_RELEASE_PENDING = "PAYMENT_RELEASE_PENDING", "Payment Release Pending"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"

class PAYMENT_STATUS(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_ESCROW = "IN_ESCROW", "In Escrow"
    RELEASED = "RELEASED", "Released"
    REFUNDED = "REFUNDED", "Refunded"
    PARTIAL_REFUND = "PARTIAL_REFUND", "Partial Refund"

class REFUND_STATUS(models.TextChoices):
    REQUESTED = "REQUESTED", "Requested"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PROCESSED = "PROCESSED", "Processed"

class REFUND_TYPE(models.TextChoices):
    FULL = "FULL", "Full Refund"
    PARTIAL = "PARTIAL", "Partial Refund"

class REFUND_REASON(models.TextChoices):
    PATIENT_REJECTED_FINAL_PLAN = "PATIENT_REJECTED_FINAL_PLAN", "Patient Rejected Final Treatment Plan"
    APPOINTMENT_CANCELLED = "APPOINTMENT_CANCELLED", "Appointment Cancelled"
    DOCTOR_UNAVAILABLE = "DOCTOR_UNAVAILABLE", "Doctor Unavailable"
    NO_SHOW = "NO_SHOW", "Patient No Show"
    PARTIAL_REFUND = "PARTIAL_REFUND", "Partial Refund"
    ADMIN_MANUAL = "ADMIN_MANUAL", "Admin Manual Refund"


