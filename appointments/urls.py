from django.urls import path, include
from .consultant_views import (
    ConsultationPatientInfoAPIView, ConsultationTreatmentInterestAPIView,
    ConsultationBudgetTravelAPIView, ConsultationDentalHistoryAPIView, ConsultationDentalPhotoAPIView,
    ConsultationXrayAPIView, ConsultationScheduleAPIView,
    MyConsultationViewSet
)
from rest_framework.routers import DefaultRouter

consultations_router = DefaultRouter()
consultations_router.register("consultations", MyConsultationViewSet, basename="patient-consultations")

urlpatterns = [
    path("consultations/step-1/", ConsultationPatientInfoAPIView.as_view()),
    path("consultations/step-2/", ConsultationTreatmentInterestAPIView.as_view()),
    path("consultations/step-3/", ConsultationBudgetTravelAPIView.as_view()),
    path("consultations/step-4/", ConsultationDentalHistoryAPIView.as_view()),
    path("consultations/step-5/", ConsultationDentalPhotoAPIView.as_view()),
    path("consultations/step-6/", ConsultationXrayAPIView.as_view()),
    path("consultations/step-7/", ConsultationScheduleAPIView.as_view()),
    
    path("patient/", include(consultations_router.urls))
]

