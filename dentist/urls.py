from django.urls import include, path
from rest_framework.routers import DefaultRouter
from dentist.verification_views import DentistLicenseVerificationSubmitAPIView, ClinicalOperationVerificationSubmitAPIView, ClinicalDepthVerificationSubmitAPIView
from dentist.views import DentistVerificationProgressAPIView, DentistVerificationPhaseUpdateAPIView
from dentist.admin_views import DentistClinicOperationVerificationViewSet, DentistLicenseVerificationViewSet, DentistClinicalDepthVerificationViewSet

router = DefaultRouter()
router.register(r"dentist-license-verifications", DentistLicenseVerificationViewSet, basename="dentist-license-verification")
router.register(r"dentist-clinic-operation-verifications", DentistClinicOperationVerificationViewSet, basename="dentist-clinic-operation-verification")
router.register(r"dentist-clinic-depth-verifications", DentistClinicalDepthVerificationViewSet, basename="dentist-clinic-depth-verification")


urlpatterns = [
    path("dentist/verification-progress/", DentistVerificationProgressAPIView.as_view(), name="dentist-verification-progress"),
    path("dentist/update-verification-phase/", DentistVerificationPhaseUpdateAPIView.as_view(), name="update-dentist-verification-phase"),
    
    path("dentist/verification-step/license/", DentistLicenseVerificationSubmitAPIView.as_view(), name="dentist-license-verification"),
    path("dentist/verification-step/operations/", ClinicalOperationVerificationSubmitAPIView.as_view(), name="dentist-clinical-operation-verification"),
    path("dentist/verification-step/clinical-depth/", ClinicalDepthVerificationSubmitAPIView.as_view(), name="dentist-clinical-depth-verification"),
    
    
    # Admin Action APIs
    path("admin/", include(router.urls)),
]
