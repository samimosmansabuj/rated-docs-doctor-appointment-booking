from django.urls import path
from .views import (
    SignupAPIView,
    LoginAPIView,
    RefreshTokenAPIView,
    LogoutAPIView,
    VerifyTokenAPIView
)

urlpatterns = [
    path("auth/signup/", SignupAPIView.as_view()),
    path("auth/login/", LoginAPIView.as_view()),
    path("auth/logout/", LogoutAPIView.as_view()),
    path("auth/token/refresh/", RefreshTokenAPIView.as_view()),
    path("auth/token/verify/", VerifyTokenAPIView.as_view()),
    
    # path("dentist/")
]
