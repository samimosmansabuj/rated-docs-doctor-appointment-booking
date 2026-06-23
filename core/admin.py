from django.contrib import admin
from .models import Procedure, LicenseRegistrationAuthority, PostMethodPayloadStore

admin.site.register(Procedure)
admin.site.register(LicenseRegistrationAuthority)
admin.site.register(PostMethodPayloadStore)