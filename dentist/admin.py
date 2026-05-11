from django.contrib import admin
from .models import Clinic, DentistProfile, DentistWeeklyAvailability, SlotException, DentistVerification, DentistDocument, DentistService

admin.site.register(Clinic)
admin.site.register(DentistProfile)
admin.site.register(DentistWeeklyAvailability)
admin.site.register(SlotException)
admin.site.register(DentistVerification)
admin.site.register(DentistDocument)
admin.site.register(DentistService)
