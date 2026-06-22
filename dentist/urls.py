from django.urls import include, path
from rest_framework.routers import DefaultRouter
from dentist.verification_views import (
    DentistLicenseVerificationSubmitAPIView, ClinicalOperationVerificationSubmitAPIView, ClinicalDepthVerificationSubmitAPIView, DentistProcedureReadListView
)
from dentist.views import (
    DentistVerificationProgressAPIView, DentistVerificationPhaseUpdateAPIView,
    
    AdminDentistViewSet, DentistProfileViewSet, PatientDentistViewSet
)
from dentist.admin_views import DentistVerificationViewSet


patient_router = DefaultRouter()
patient_router.register("dentists", PatientDentistViewSet, basename="patient-dentists-list")

admin_router = DefaultRouter()
admin_router.register("dentists", AdminDentistViewSet, basename="admin-dentists-list")
admin_router.register("dentist-verification", DentistVerificationViewSet, basename="dentists-verification")

dentist_router = DefaultRouter()
# dentist_router.register("own", DentistProfileViewSet, basename="my-profile")

urlpatterns = [
    # Check Verification Process---
    path("dentist/verification-progress/", DentistVerificationProgressAPIView.as_view(), name="dentist-verification-progress"),
    path("dentist/update-verification-phase/", DentistVerificationPhaseUpdateAPIView.as_view(), name="update-dentist-verification-phase"),
    
    # Verification Step Action---
    path("dentist/verification-step/license/", DentistLicenseVerificationSubmitAPIView.as_view(), name="dentist-license-verification"),
    path("dentist/verification-step/operations/", ClinicalOperationVerificationSubmitAPIView.as_view(), name="dentist-clinical-operation-verification"),
    path("dentist/verification-step/dentist-procedure-list/", DentistProcedureReadListView.as_view(), name="dentist-procedure-list"),
    path("dentist/verification-step/clinical-depth/", ClinicalDepthVerificationSubmitAPIView.as_view(), name="dentist-clinical-depth-verification"),
    
    # Dentist Own Profile Details----
    path("dentist/my-profile/", DentistProfileViewSet.as_view(), name="my-own-profile"),
    path("dentist/", include(dentist_router.urls)),
    
    # Admin and Patient Action APIs
    path("patient/", include(patient_router.urls)),
    path("admin/", include(admin_router.urls)),
]
