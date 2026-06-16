from rest_framework.generics import CreateAPIView
from .serializers.serializers import (
    AppointmentDecisionSerializer
)
from core.permissions import IsDentist, IsPatient
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from core.utils.views import BaseCreateAPIView


class AppointmentDecisionAPIView(BaseCreateAPIView):
    serializer_class = AppointmentDecisionSerializer
    permission_classes = [IsPatient]
    success_message = "Initial Treatment Created."


