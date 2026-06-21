from django.urls import path, include
from .utils.utils import PaymentCallbackAPIView
from rest_framework.routers import DefaultRouter
from .views import ProcedureViewSet, MainProcedureViewSet

router = DefaultRouter()
router.register(r"procedures", ProcedureViewSet, basename="procedure")
router.register(r"main-procedures", MainProcedureViewSet, basename="main-procedure")

urlpatterns = [
    path("pay/callback-url/", PaymentCallbackAPIView.as_view(), name="payment-callback"),
    
    path("api/v1/procedure/", include(router.urls))
    
]

