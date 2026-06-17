from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsDentist
from core.utils.response import custom_response
from core.utils.views import OwnAPIView
from dentist.serializer.serializers import (
    DentistVerificationPhaseUpdateSerializer, DentistVerificationStatusSerializer
)
from dentist.serializer.model import (
    DentistProfileDetailSerializer
)
from dentist.serializer.public import (
    PatientDentistDetailSerializer
)
from rest_framework.response import Response
from .models import DentistProfile
from core.utils.viewsets import OwnReadOnlyModelViewSet
from rest_framework.views import APIView
from core.permissions import IsAdmin, IsPatient, IsDentist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class DentistVerificationProgressAPIView(APIView):
    permission_classes = [IsDentist]

    def get(self, request):
        dentist = request.user.dentist_profile
        serializer = DentistVerificationStatusSerializer(
            dentist
        )
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class DentistVerificationPhaseUpdateAPIView(OwnAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DentistVerificationPhaseUpdateSerializer

    def success_response(self, serializer):
        profile = serializer.save()
        return custom_response(
            success=True,
            message="Verification phase updated successfully.",
            data={
                "verification_phase": profile.verification_phase,
                "verification_phase_label": profile.get_verification_phase_display(),
                "is_verified": profile.is_verified,
            }
        )





class DentistQuerysetMixin:
    def get_queryset(self):
        return DentistProfile.objects.select_related(
            "user", "clinic", "dentist_verification",
            "dentist_verification__dentist_license_verification",
            "dentist_verification__operation_verification",
            "dentist_verification__operation_verification__sterilization_verification",
            "dentist_verification__operation_verification__no_surprise_guarantee",
            "dentist_verification__clinical_path_verification",
        ).prefetch_related(
            "dentist_address", "weekly_availability", "slot_exceptions",
            "dentist_verification__operation_verification__procedures_feature__procedure",
            "dentist_verification__clinical_path_verification__procedure_material_verifications__own_procedure__procedure",
        )

class AdminDentistViewSet(DentistQuerysetMixin,OwnReadOnlyModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = DentistProfileDetailSerializer

class PatientDentistViewSet(DentistQuerysetMixin, OwnReadOnlyModelViewSet):
    permission_classes = [IsPatient]
    serializer_class = PatientDentistDetailSerializer
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["full_name", "specialty", "clinic__name", "clinic__country", "clinic__city",]
    ordering_fields = ["rating_avg", "total_reviews", "experience_years", "rdv_score",]
    filterset_fields = ["specialty",]

    def get_queryset(self):
        return super().get_queryset().filter(
            is_verified=True
        )

class DentistProfileViewSet(DentistQuerysetMixin, APIView):
    permission_classes = [IsDentist]
    serializer_class = DentistProfileDetailSerializer

    def get_queryset(self):
        return super().get_queryset().get(
            id=self.request.user.dentist_profile.id
        )
    
    def get(self, request, *args, **kwargs):
        my_profile = self.get_queryset()
        serializer = self.serializer_class(my_profile)
        return Response(
            {
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK
        )
    
