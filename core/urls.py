from django.urls import path, include
from .utils.utils import PaymentCallbackAPIView
from rest_framework.routers import DefaultRouter
from .views import ProcedureViewSet, MainProcedureViewSet, LicenseRegistrationAuthorityViewSet

router = DefaultRouter()
router.register(r"procedure/procedures", ProcedureViewSet, basename="procedure")
router.register(r"procedure/main-procedures", MainProcedureViewSet, basename="main-procedure")
router.register(r"license-registration-authority", LicenseRegistrationAuthorityViewSet, basename="license-registration-authority")

urlpatterns = [
    path("pay/callback-url/", PaymentCallbackAPIView.as_view(), name="payment-callback"),
    
    path("api/v1/", include(router.urls))
    
]

