from appointments.models import (
    TreatmentPlan, TreatmentPlanProcedure, Appointment, AppointmentDecision, EscrowPayment, ArrivalVerification, TreatmentPlanFile, TreatmentReview, TreatmentResultPhoto, TreatmentCompletionFile, TreatmentCompletion, FinalTreatmentDecision, PaymentReleaseCode, AppointmentRefund
)
from rest_framework import serializers
from .consultant import ConsultationDetailsSerializer

# Treatment Details Serializers------------------------------------------------------------------------
class TreatmentPlanProcedureReadSerializer(serializers.ModelSerializer):
    procedure_name = serializers.CharField(source="procedure.name",read_only=True)

    class Meta:
        model = TreatmentPlanProcedure
        fields = "__all__"

class TreatmentPlanFileReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentPlanFile
        fields = "__all__"

class TreatmentPlanReadSerializer(serializers.ModelSerializer):
    procedures = TreatmentPlanProcedureReadSerializer(many=True,read_only=True)
    files = TreatmentPlanFileReadSerializer(many=True,read_only=True)
    dentist_name = serializers.CharField(source="created_by.full_name",read_only=True)

    class Meta:
        model = TreatmentPlan
        fields = "__all__"

class AppointmentDecisionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentDecision
        fields = "__all__"

class EscrowPaymentReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = EscrowPayment
        fields = "__all__"

class ArrivalVerificationReadSerializer(serializers.ModelSerializer):
    dentist_name = serializers.CharField(source="verified_by.full_name",read_only=True)

    class Meta:
        model = ArrivalVerification
        fields = "__all__"

class FinalTreatmentDecisionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalTreatmentDecision
        fields = "__all__"

class PaymentReleaseCodeReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentReleaseCode
        fields = "__all__"

class TreatmentCompletionFileReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentCompletionFile
        fields = "__all__"

class TreatmentCompletionReadSerializer(serializers.ModelSerializer):
    files = TreatmentCompletionFileReadSerializer(many=True,read_only=True)

    class Meta:
        model = TreatmentCompletion
        fields = "__all__"

class TreatmentResultPhotoReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentResultPhoto
        fields = "__all__"

class TreatmentReviewReadSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.get_full_name",read_only=True)
    dentist_name = serializers.CharField(source="dentist.full_name",read_only=True)

    class Meta:
        model = TreatmentReview
        fields = "__all__"

class AppointmentRefundReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentRefund
        fields = "__all__"


class AppointmentDetailSerializer(serializers.ModelSerializer):
    # consultation = ConsultationDetailsSerializer(read_only=True)
    initial_treatment_plan = (TreatmentPlanReadSerializer(read_only=True))
    final_treatment_plan = (TreatmentPlanReadSerializer(read_only=True))
    decision = AppointmentDecisionReadSerializer(read_only=True)
    escrow_payment = (EscrowPaymentReadSerializer(read_only=True))
    arrival_verification = (ArrivalVerificationReadSerializer(read_only=True))
    final_decision = (FinalTreatmentDecisionReadSerializer(read_only=True))
    release_code = (PaymentReleaseCodeReadSerializer(read_only=True))
    completion = (TreatmentCompletionReadSerializer(read_only=True))
    result_photos = (TreatmentResultPhotoReadSerializer(many=True,read_only=True))
    review = (TreatmentReviewReadSerializer(read_only=True))
    refund = (AppointmentRefundReadSerializer(read_only=True))
    patient_name = serializers.CharField(source="patient.user.get_full_name",read_only=True)
    dentist_name = serializers.CharField(source="dentist.full_name",read_only=True)
    
    class Meta:
        model = Appointment
        fields = "__all__"

# -----------------------------------------------------------------------------------------------------

