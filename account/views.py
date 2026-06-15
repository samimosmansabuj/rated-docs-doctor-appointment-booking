from django.shortcuts import get_object_or_404
from dentist.models import DentistProfile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ResendOTPSerializer, SignupSerializer, LoginSerializer, RefreshSerializer, DentistProfessionalSerializer, AdminUserAddSerializer, VerifyOTPSerializer
from core.utils.response import custom_response
from core.utils.views import OwnAPIView
from core.constants import USER_ROLE_CHOICES
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.permissions import IsDentist

# ==========================================================================
# ======================Authentication Views=========================
class SignupAPIView(OwnAPIView):
    serializer_class = SignupSerializer
    
    def success_response(self, serializer):
        user = serializer.save()
        serializer.send_otp(user)        
        return custom_response(
            success=True,
            message="User created successfully",
            data={"email": user.email, "role": user.role},
            status=status.HTTP_201_CREATED
        )

class AdminUserAddViews(OwnAPIView):
    serializer_class = AdminUserAddSerializer
    permission_classes = [IsAuthenticated]

    def success_response(self, serializer):
        user = serializer.save()
        return custom_response(
            success=True,
            message="User added successfully",
            data={"email": user.email, "role": user.role},
            status=status.HTTP_201_CREATED
        )

class LoginAPIView(OwnAPIView):
    serializer_class = LoginSerializer
    
    def success_response(self, serializer):
        return custom_response(
            success=True,
            message="Login successful",
            data=serializer.validated_data,
            status=status.HTTP_200_OK
        )

class VerifyOTPAPIView(OwnAPIView):
    serializer_class = VerifyOTPSerializer

    def success_response(self, serializer):
        data = serializer.save()
        return custom_response(
            success=True,
            message="OTP verified successfully.",
            data=data
        )

class ResendOTPAPIView(OwnAPIView):
    serializer_class = ResendOTPSerializer

    def success_response(self, serializer):
        serializer.save()
        return custom_response(
            success=True,
            message="OTP sent successfully."
        )

class RefreshTokenAPIView(OwnAPIView):
    serializer_class = RefreshSerializer
    
    def success_response(self, serializer):
        return custom_response(
            success=True,
            message="Token refreshed",
            data=serializer.validated_data,
            status=status.HTTP_200_OK
        )

class LogoutAPIView(OwnAPIView):
    def success_response(self):
        refresh_token = self.request.data.get("refresh")
        if not refresh_token:
            return custom_response(
                success=False,
                message="Refresh token is required",
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return custom_response(
                success=False,
                message="Logout is failed",
                status=status.HTTP_400_BAD_REQUEST
            )
        return custom_response(
            success=True,
            message="Logout successful",
            status=status.HTTP_200_OK
        )

class VerifyTokenAPIView(APIView):
    def get(self, request):
        auth = JWTAuthentication()
        try:
            user, token = auth.authenticate(request)
            return custom_response(
                success=True,
                message="Token is valid",
                data={"user_id": user.id, "email": user.email, "type": user.role},
                status=200
            )
        except Exception:
            return custom_response(
                success=False,
                detail="Invalid or expired token",
                status=401
            )

# ======================Authentication Views=========================
# ==========================================================================

class DentistProfessionalSubmitViews(APIView):
    permission_classes = [IsDentist]
    
    def post(self, request, *args, **kwargs):
        serializer = DentistProfessionalSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return custom_response(
            success=True, detail="Professional Details Submit.",
            status=status.HTTP_200_OK
        )



