from django.urls import path
from .views import (
    ResendOTPAPIView,
    SignupAPIView,
    LoginAPIView,
    RefreshTokenAPIView,
    LogoutAPIView,
    VerifyOTPAPIView,
    VerifyTokenAPIView, AdminUserAddViews,
    
    DentistProfessionalSubmitViews
)

urlpatterns = [
    path("auth/signup/", SignupAPIView.as_view()),
    path("auth/add-user/", AdminUserAddViews.as_view()),
    path("auth/verify-otp/", VerifyOTPAPIView.as_view()),
    path("auth/resend-otp/", ResendOTPAPIView.as_view()),
    path("auth/login/", LoginAPIView.as_view()),
    path("auth/logout/", LogoutAPIView.as_view()),
    path("auth/token/refresh/", RefreshTokenAPIView.as_view()),
    path("auth/token/verify/", VerifyTokenAPIView.as_view()),
    
    path("dentist/enter-professional-details/", DentistProfessionalSubmitViews.as_view()),
]
