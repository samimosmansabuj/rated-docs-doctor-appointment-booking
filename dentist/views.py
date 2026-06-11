from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from core.constants import USER_ROLE_CHOICES, DENTIST_VERIFICATION_PHASE
from core.utils.response import custom_response
from core.utils.views import OwnAPIView
from dentist.serializers import DentistVerificationPhaseUpdateSerializer

class DentistVerificationProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def phase_order(self):
        return [
            DENTIST_VERIFICATION_PHASE.ONE,
            DENTIST_VERIFICATION_PHASE.TWO,
            DENTIST_VERIFICATION_PHASE.THREE,
            DENTIST_VERIFICATION_PHASE.COMPLETE,
        ]
    
    def get_step_status(self, current_index):
        return [
            {
                "phase": DENTIST_VERIFICATION_PHASE.ONE,
                "label": "License",
                "completed": current_index > 0,
            },
            {
                "phase": DENTIST_VERIFICATION_PHASE.TWO,
                "label": "Operational",
                "completed": current_index > 1,
            },
            {
                "phase": DENTIST_VERIFICATION_PHASE.THREE,
                "label": "Clinical",
                "completed": current_index > 2,
            }
        ]

    def get_progress_percentage(self, current_index):
        total_steps = len(self.phase_order()) - 1
        if current_index >= total_steps:
            return 100
        return int((current_index / total_steps) * 100)
    
    def get(self, request):
        if request.user.role != USER_ROLE_CHOICES.DENTIST:
            raise ValidationError("Only dentists are allowed.")

        profile = request.user.dentist_profile
        phase_order = self.phase_order()
        current_index = phase_order.index(profile.verification_phase)
        steps = self.get_step_status(current_index)
        progress = self.get_progress_percentage(current_index)

        return custom_response(
            success=True,
            data={
                "current_phase": profile.verification_phase,
                "current_phase_label": profile.get_verification_phase_display(),
                "progress_percentage": progress,
                "is_verified": profile.is_verified,
                "steps": steps,
            }
        )

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




