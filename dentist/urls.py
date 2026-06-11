from django.urls import include, path
from rest_framework.routers import DefaultRouter
from dentist.verification_views import ClinicOperationVerificationAPIView, DentistLicenseVerificationAPIView
from dentist.views import DentistVerificationProgressAPIView, DentistVerificationPhaseUpdateAPIView
from dentist.admin_views import DentistLicenseVerificationViewSet

router = DefaultRouter()
router.register(
    r"dentist-license-verifications", DentistLicenseVerificationViewSet, basename="dentist-license-verification"
)


urlpatterns = [
    path("dentist/verification-progress/", DentistVerificationProgressAPIView.as_view(), name="dentist-verification-progress"),
    path("dentist/update-verification-phase/", DentistVerificationPhaseUpdateAPIView.as_view(), name="update-dentist-verification-phase"),
    
    path("dentist/verification-step/license/", DentistLicenseVerificationAPIView.as_view(), name="dentist-license-verification"),
    path("dentist/verification-step/operations/", ClinicOperationVerificationAPIView.as_view(), name="dentist-operation-verification"),
    
    
    # Admin Action APIs
    path("admin/", include(router.urls)),
]
