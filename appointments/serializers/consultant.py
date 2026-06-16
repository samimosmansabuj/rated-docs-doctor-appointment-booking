from account.models import PatientProfile
from rest_framework import serializers
from appointments.consultant_models import Consultation, ConsultationDentalHistory, ConsultationDentalPhoto, ConsultationXRay, ConsultationSchedule, VideoConsultationSession
from core.models import Procedure
from dentist.models import DentistProfile


# Consultation Details Serializers------------------------------------------------------------------------
class ConsultationPatientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = ["id", "full_name", "date_of_birth", "country", "medical_notes"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()

class ConsultationDentistSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentistProfile
        fields = ["id", "full_name", "specialty", "experience_years", "rating_avg", "total_reviews", "is_verified",]

class ConsultationProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ["id", "name",]

class ConsultationScheduleSerializer(serializers.ModelSerializer):
    # dentist = ConsultationDentistSerializer(read_only=True)

    class Meta:
        model = ConsultationSchedule
        fields = "__all__"

class ConsultationDentalPhotoSerializer(serializers.ModelSerializer):
    uploaded_photo_count = serializers.SerializerMethodField()

    class Meta:
        model = ConsultationDentalPhoto
        fields = "__all__"

    def get_uploaded_photo_count(self, obj):
        photo_fields = [ obj.front_smile, obj.wide_smile, obj.upper_arch, obj.lower_arch, obj.left_side, obj.right_side,]
        return len([photo for photo in photo_fields if photo])

class ConsultationXRaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationXRay
        fields = "__all__"

class ConsultationDentalHistorySerializer(serializers.ModelSerializer):
    last_dentist_visit_display = serializers.CharField(source="get_last_dentist_visit_display", read_only=True)

    class Meta:
        model = ConsultationDentalHistory
        fields = "__all__"

class VideoConsultationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoConsultationSession
        fields = "__all__"

class ConsultationDetailsSerializer(serializers.ModelSerializer):
    patient = ConsultationPatientSerializer(read_only=True)
    dentist = ConsultationDentistSerializer(read_only=True)
    treatment_interest = ConsultationProcedureSerializer(many=True, read_only=True)

    schedule = ConsultationScheduleSerializer(read_only=True)
    dental_photo = ConsultationDentalPhotoSerializer(read_only=True)
    xrays = ConsultationXRaySerializer(read_only=True)
    dental_history = ConsultationDentalHistorySerializer(read_only=True)
    video_session = VideoConsultationSessionSerializer(read_only=True)

    class Meta:
        model = Consultation
        fields = [
            "id", "patient", "dentist", "status",
            "treatment_interest",
            "approximate_budget", "travel_start_date", "travel_end_date",
            "schedule", "dental_photo", "xrays", "dental_history", "video_session",
            "created_at", "updated_at",
        ]

# -----------------------------------------------------------------------------------------------------