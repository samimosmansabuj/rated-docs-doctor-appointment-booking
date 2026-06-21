from django.contrib import admin

from .models import (
    Clinic,
    DentistProfile,
    DentistAddress,
    DentistWeeklyAvailability,
    SlotException,
    DentistVerification,
    DentistLicenseVerification,
    ClinicOperationVerification,
    SterilizationVerification,
    ProcedurePrice,
    NoSurpriseGuarantee,
    ClinicalPathVerification,
    ProcedureMaterialVerification,
)


admin.site.register(Clinic)
admin.site.register(DentistProfile)
admin.site.register(DentistAddress)

admin.site.register(DentistWeeklyAvailability)
admin.site.register(SlotException)

admin.site.register(DentistVerification)
admin.site.register(DentistLicenseVerification)

admin.site.register(ClinicOperationVerification)
admin.site.register(SterilizationVerification)

admin.site.register(ProcedurePrice)
admin.site.register(NoSurpriseGuarantee)

admin.site.register(ClinicalPathVerification)
admin.site.register(ProcedureMaterialVerification)