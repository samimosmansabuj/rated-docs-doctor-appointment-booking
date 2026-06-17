from django.urls import include, path
from rest_framework.routers import DefaultRouter
from dentist.verification_views import DentistLicenseVerificationSubmitAPIView, ClinicalOperationVerificationSubmitAPIView, ClinicalDepthVerificationSubmitAPIView
from dentist.views import (
    DentistVerificationProgressAPIView, DentistVerificationPhaseUpdateAPIView,
    
    AdminDentistViewSet, DentistProfileViewSet, PatientDentistViewSet
)
from dentist.admin_views import DentistClinicOperationVerificationViewSet, DentistLicenseVerificationViewSet, DentistClinicalDepthVerificationViewSet


patient_router = DefaultRouter()
patient_router.register("dentists", PatientDentistViewSet, basename="dentists-list")

admin_router = DefaultRouter()
admin_router.register("dentists", AdminDentistViewSet, basename="dentists-list")
admin_router.register(r"dentist-license-verifications", DentistLicenseVerificationViewSet, basename="dentist-license-verification")
admin_router.register(r"dentist-clinic-operation-verifications", DentistClinicOperationVerificationViewSet, basename="dentist-clinic-operation-verification")
admin_router.register(r"dentist-clinic-depth-verifications", DentistClinicalDepthVerificationViewSet, basename="dentist-clinic-depth-verification")

dentist_router = DefaultRouter()
# dentist_router.register("own", DentistProfileViewSet, basename="my-profile")

urlpatterns = [
    path("dentist/verification-progress/", DentistVerificationProgressAPIView.as_view(), name="dentist-verification-progress"),
    path("dentist/update-verification-phase/", DentistVerificationPhaseUpdateAPIView.as_view(), name="update-dentist-verification-phase"),
    
    path("dentist/verification-step/license/", DentistLicenseVerificationSubmitAPIView.as_view(), name="dentist-license-verification"),
    path("dentist/verification-step/operations/", ClinicalOperationVerificationSubmitAPIView.as_view(), name="dentist-clinical-operation-verification"),
    path("dentist/verification-step/clinical-depth/", ClinicalDepthVerificationSubmitAPIView.as_view(), name="dentist-clinical-depth-verification"),
    

    path("dentist/my-profile/", DentistProfileViewSet.as_view(), name="my-own-profile"),
    path("dentist/", include(dentist_router.urls)),
    
    # Admin Action APIs    
    path("patient/", include(patient_router.urls)),
    path("admin/", include(admin_router.urls)),
]
