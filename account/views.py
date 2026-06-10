from django.shortcuts import get_object_or_404
from dentist.models import DentistProfile
from rest_framework import status
from rest_framework.views import APIView
from .serializers import SignupSerializer, LoginSerializer, RefreshSerializer, DentistProfessionalSerializer
from core.utils.response import custom_response
from core.utils.views import OwnAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication


class SignupAPIView(OwnAPIView):
    serializer_class = SignupSerializer
    
    def success_response(self, serializer):
        user = serializer.save()
        return custom_response(
            success=True,
            message="User created successfully",
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
                data={"user_id": user.id, "email": user.email},
                status=200
            )
        except Exception:
            return custom_response(
                success=False,
                detail="Invalid or expired token",
                status=401
            )

class DentistProfessionalSubmitViews(APIView):
    def post(self, request, dentist_id, *args, **kwargs):
        dentist = get_object_or_404(DentistProfile, id=dentist_id)
        serializer = DentistProfessionalSerializer(dentist, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return custom_response(
            success=True, detail="Professional Details Submit.",
            status=status.HTTP_200_OK
        )
        
    

