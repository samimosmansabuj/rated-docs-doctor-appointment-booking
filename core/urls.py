from django.urls import path
from .utils.utils import PaymentCallbackAPIView

urlpatterns = [
    path("pay/callback-url/", PaymentCallbackAPIView.as_view(), name="payment-callback"
)
]
