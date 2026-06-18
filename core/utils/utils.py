from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from appointments.models import EscrowPayment
from core.constants import (
    APPOINTMENT_STATUS,
    CONSULTATION_STATUS,
    PAYMENT_STATUS,
    ESCROW_PAYMENT_STATUS
)


class PaymentCallbackAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    @transaction.atomic
    def get(self, request):
        stripe_token = request.query_params.get("stripe-token")
        transaction_id = request.query_params.get("platform-transaction")
        payment_details = request.query_params.get("payment-details")
        
        if not transaction_id:
            return Response(
                {
                    "success": False,
                    "message": "platform-transaction is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment = (
                EscrowPayment.objects
                .select_related("appointment", "appointment__consultation",)
                .get(transaction_id=transaction_id, stripe_subscription_id=stripe_token)
            )
        except EscrowPayment.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Payment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        
        appointment = payment.appointment
        consultation = appointment.consultation

        # prevent duplicate callback processing
        if payment.status == ESCROW_PAYMENT_STATUS.IN_ESCROW:
            return Response(
                {
                    "success": True,
                    "message": "Payment already processed."
                }
            )

        payment.status = ESCROW_PAYMENT_STATUS.IN_ESCROW
        payment.paid_at = timezone.now()
        payment.payment_details = payment_details
        # payment.stripe_subscription_id = stripe_token
        payment.save(
            update_fields=[
                "status",
                "paid_at",
                "stripe_subscription_id",
            ]
        )

        appointment.status = APPOINTMENT_STATUS.CONFIRMED
        appointment.save(update_fields=["status"])

        # consultation.status = CONSULTATION_STATUS.SCHEDULED
        # consultation.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "message": "Payment completed successfully.",
                "transaction_id": payment.transaction_id,
            }
        )



