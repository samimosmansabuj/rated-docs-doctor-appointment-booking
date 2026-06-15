from django.urls import path, include
from .consultant_views import (
    ConsultationPatientInfoAPIView, ConsultationTreatmentInterestAPIView,
    ConsultationBudgetTravelAPIView, ConsultationDentalHistoryAPIView, ConsultationDentalPhotoAPIView,
    ConsultationXrayAPIView, ConsultationScheduleAPIView,
    MyConsultationViewSet, ConsultationViewSet, DentistConsultationViewSet
)
from rest_framework.routers import DefaultRouter

patient_router = DefaultRouter()
patient_router.register("consultations", MyConsultationViewSet, basename="patient-consultations")

admin_router = DefaultRouter()
admin_router.register("consultations", ConsultationViewSet, basename="admin-consultations")

dentist_router = DefaultRouter()
dentist_router.register("consultations", DentistConsultationViewSet, basename="dentist-consultations")


urlpatterns = [
    path("consultations/step-1/", ConsultationPatientInfoAPIView.as_view()),
    path("consultations/step-2/", ConsultationTreatmentInterestAPIView.as_view()),
    path("consultations/step-3/", ConsultationBudgetTravelAPIView.as_view()),
    path("consultations/step-4/", ConsultationDentalHistoryAPIView.as_view()),
    path("consultations/step-5/", ConsultationDentalPhotoAPIView.as_view()),
    path("consultations/step-6/", ConsultationXrayAPIView.as_view()),
    path("consultations/step-7/", ConsultationScheduleAPIView.as_view()),
    
    path("patient/", include(patient_router.urls)),
    path("admin/", include(admin_router.urls)),
    path("dentist/", include(dentist_router.urls)),
]

