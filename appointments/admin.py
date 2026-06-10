from django.contrib import admin

from .consultant_models import (
    Consultation,
    ConsultationSchedule,
    ConsultationDentalPhoto,
    ConsultationXRay,
    ConsultationDentalHistory,
    VideoConsultationSession,
)
from .models import (
    TreatmentPlan,
    TreatmentPlanProcedure,
    TreatmentPlanFile,
    Appointment,
    AppointmentDecision,
    EscrowPayment,
    ArrivalVerification,
    FinalTreatmentDecision,
    PaymentReleaseCode,
    TreatmentCompletion,
    TreatmentCompletionFile,
    TreatmentResultPhoto,
    TreatmentReview,
    AppointmentRefund,
)


admin.site.register(TreatmentPlan)
admin.site.register(TreatmentPlanProcedure)
admin.site.register(TreatmentPlanFile)

admin.site.register(Appointment)
admin.site.register(AppointmentDecision)

admin.site.register(EscrowPayment)
admin.site.register(ArrivalVerification)

admin.site.register(FinalTreatmentDecision)
admin.site.register(PaymentReleaseCode)

admin.site.register(TreatmentCompletion)
admin.site.register(TreatmentCompletionFile)

admin.site.register(TreatmentResultPhoto)
admin.site.register(TreatmentReview)

admin.site.register(AppointmentRefund)


admin.site.register(Consultation)
admin.site.register(ConsultationSchedule)
admin.site.register(ConsultationDentalPhoto)
admin.site.register(ConsultationXRay)
admin.site.register(ConsultationDentalHistory)
admin.site.register(VideoConsultationSession)