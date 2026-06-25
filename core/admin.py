from django.contrib import admin
from .models import Procedure, LicenseRegistrationAuthority, PostMethodPayloadStore, EmailConfig

admin.site.register(Procedure)
admin.site.register(LicenseRegistrationAuthority)
admin.site.register(PostMethodPayloadStore)
admin.site.register(EmailConfig)