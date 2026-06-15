from datetime import datetime
from account.models import PatientProfile
from rest_framework import serializers
from .consultant_models import Consultation, ConsultationDentalHistory, ConsultationDentalPhoto, ConsultationXRay, ConsultationSchedule, VideoConsultationSession
from core.constants import CONSULTATION_STATUS, LAST_VISIT_CHOICE, SCHEDULE_STATUS, VIDEO_SESSION_STATUS
from core.models import Procedure
from dentist.models import DentistProfile
from django.db import transaction
from django.utils import timezone

# Consultation All Serializers------------------------------------------------------------------------
class ConsultationPatientInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(read_only=True)
    date_of_birth = serializers.DateField()
    country = serializers.CharField()
    
    def save(self):
        user = self.context["request"].user
        patient = user.patient_profile

        user.first_name = self.validated_data["first_name"]
        user.last_name = self.validated_data["last_name"]
        user.save()

        patient.date_of_birth = self.validated_data["date_of_birth"]
        patient.country = self.validated_data["country"]
        patient.save()
        return {
            "first_name": self.validated_data["first_name"],
            "last_name": self.validated_data["last_name"],
            "email": user.email,
            "date_of_birth": self.validated_data["date_of_birth"],
            "country": self.validated_data["country"],
        }

class ConsultationTreatmentInterestSerializer(serializers.Serializer):
    procedures = serializers.PrimaryKeyRelatedField(queryset=Procedure.objects.all(), many=True)

    def get_consultation(self, patient):
        consultation, _ = Consultation.objects.get_or_create(
            patient=patient,
            status=CONSULTATION_STATUS.DRAFT
        )
        return consultation
    
    def save(self):
        user = self.context["request"].user
        patient = user.patient_profile
        consultation = self.get_consultation(patient)
        consultation.treatment_interest.set(
            self.validated_data["procedures"]
        )
        consultation.save()
        return consultation

class ConsultationBudgetTravelSerializer(serializers.Serializer):
    consultation_id = serializers.IntegerField(write_only=True)
    approximate_budget = serializers.DecimalField(max_digits=12, decimal_places=2)
    travel_start_date = serializers.DateField()
    travel_end_date = serializers.DateField()

    def save(self):
        consultation = Consultation.objects.get(id=self.validated_data["consultation_id"])
        consultation.approximate_budget = self.validated_data["approximate_budget"]
        consultation.travel_start_date = self.validated_data["travel_start_date"]
        consultation.travel_end_date = self.validated_data["travel_end_date"]
        consultation.save()
        return consultation

class ConsultationDentalHistorySerializer(serializers.Serializer):
    consultation_id = serializers.IntegerField(write_only=True)
    last_dentist_visit = serializers.ChoiceField(choices=LAST_VISIT_CHOICE.choices)
    conditions = serializers.ListField(child=serializers.CharField())
    notes = serializers.CharField(required=False, allow_blank=True)

    def save(self):
        consultation = Consultation.objects.get(id=self.validated_data["consultation_id"])
        ConsultationDentalHistory.objects.update_or_create(
            consultation=consultation,
            defaults={
                "last_dentist_visit": self.validated_data["last_dentist_visit"],
                "conditions": self.validated_data["conditions"],
                "notes": self.validated_data.get("notes", "")
            }
        )
        return consultation

class ConsultationDentalPhotoSerializer(serializers.Serializer):
    consultation_id = serializers.IntegerField(write_only=True)
    front_smile = serializers.ImageField(required=False)
    wide_smile = serializers.ImageField(required=False)
    upper_arch = serializers.ImageField(required=False)
    lower_arch = serializers.ImageField(required=False)
    left_side = serializers.ImageField(required=False)
    right_side = serializers.ImageField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        photo_fields = ["front_smile", "wide_smile", "upper_arch", "lower_arch", "left_side", "right_side",]
        uploaded_count = sum(1 for field in photo_fields if attrs.get(field))
        if uploaded_count == 0:
            raise serializers.ValidationError(
                "At least one dental photo is required."
            )
        attrs["uploaded_photo_count"] = uploaded_count
        return attrs
    
    def save(self):
        consultation_id = self.validated_data.pop("consultation_id")
        consultation = Consultation.objects.get(id=consultation_id)
        photo_count = self.validated_data.pop("uploaded_photo_count", 0)
        
        photo, _ = ConsultationDentalPhoto.objects.update_or_create(
            consultation=consultation,
            defaults=self.validated_data
        )
        return photo_count

class ConsultationXraySerializer(serializers.Serializer):
    consultation_id = serializers.IntegerField(write_only=True)
    file = serializers.FileField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def save(self):
        consultation = Consultation.objects.get(id=self.validated_data["consultation_id"])
        ConsultationXRay.objects.update_or_create(
            consultation=consultation,
            defaults={
                "file": self.validated_data["file"],
                "notes": self.validated_data.get("notes", "")
            }
        )
        return consultation

# ---Final Step:7----
class ConsultationScheduleItemSerializer(serializers.Serializer):
    dentist = serializers.PrimaryKeyRelatedField(queryset=DentistProfile.objects.all())
    scheduled_date = serializers.DateField()
    scheduled_time = serializers.TimeField()

class ConsultationScheduleSerializer(serializers.Serializer):
    consultation_id = serializers.IntegerField(write_only=True)
    dentists = ConsultationScheduleItemSerializer(many=True, required=True)

    def validate(self, attrs):
        dentists = attrs.get("dentists", [])
        if not dentists:
            raise serializers.ValidationError(
                "At least one dentist is required."
            )
        dentist_ids = [item["dentist"].id for item in dentists]
        if len(dentist_ids) != len(set(dentist_ids)):
            raise serializers.ValidationError(
                "Duplicate dentist selection is not allowed."
            )
        
        schedule_slots = [
            (
                item["scheduled_date"],
                item["scheduled_time"]
            )
            for item in dentists
        ]
        if len(schedule_slots) != len(set(schedule_slots)):
            raise serializers.ValidationError(
                "Duplicate schedule date and time is not allowed."
            )
        return attrs

    def copy_dental_history(self, source_consultation, target_consultation):
        if hasattr(source_consultation, "dental_history"):
            history = source_consultation.dental_history
            ConsultationDentalHistory.objects.create(
                consultation=target_consultation,
                last_dentist_visit=history.last_dentist_visit,
                conditions=history.conditions,
                notes=history.notes,
            )
    
    def copy_dental_photos(self, source_consultation, target_consultation):
        if hasattr(source_consultation, "dental_photo"):
            photo = source_consultation.dental_photo
            ConsultationDentalPhoto.objects.create(
                consultation=target_consultation,
                front_smile=photo.front_smile,
                wide_smile=photo.wide_smile,
                lower_arch=photo.lower_arch,
                left_side=photo.left_side,
                right_side=photo.right_side,
                notes=photo.notes,
            )
    
    def copy_xrays(self, source_consultation, target_consultation):
        if hasattr(source_consultation, "xrays"):
            xray = source_consultation.xrays
            ConsultationXRay.objects.create(
                consultation=target_consultation,
                file=xray.file,
                notes=xray.notes,
            )
    
    def copy_related_data(self, source_consultation, target_consultation):
        target_consultation.treatment_interest.set(source_consultation.treatment_interest.all())
        self.copy_dental_history(source_consultation, target_consultation) # Dental History
        self.copy_dental_photos(source_consultation, target_consultation) # Dental Photos
        self.copy_xrays(source_consultation, target_consultation) # X-Ray
    
    def create(self, validated_data):
        with transaction.atomic():
            consultation = Consultation.objects.get(id=validated_data["consultation_id"])
            request_user = self.context["request"].user
            if consultation.patient.user != request_user:
                raise serializers.ValidationError(
                    "You do not have permission."
                )
            if consultation.status != CONSULTATION_STATUS.DRAFT:
                raise serializers.ValidationError(
                    "Only draft consultation can be submitted."
                )

            created_consultations = []
            for item in validated_data["dentists"]:
                dentist = item["dentist"]
                scheduled_datetime = datetime.combine(item["scheduled_date"], item["scheduled_time"])
                if timezone.make_aware(scheduled_datetime) <= timezone.now():
                    raise serializers.ValidationError(
                        "Schedule time must be in the future."
                    )
                
                new_consultation = Consultation.objects.create(
                    patient=consultation.patient, dentist=dentist,
                    status=CONSULTATION_STATUS.SCHEDULED, approximate_budget=consultation.approximate_budget,
                    travel_start_date=consultation.travel_start_date, travel_end_date=consultation.travel_end_date,
                )
                self.copy_related_data(consultation, new_consultation)

                ConsultationSchedule.objects.create(
                    consultation=new_consultation, dentist=dentist,
                    scheduled_at=scheduled_datetime,
                    timezone="UTC",
                    status=SCHEDULE_STATUS.CONFIRMED,
                )
                
                VideoConsultationSession.objects.create(
                    consultation=new_consultation,
                    meeting_url="https://meet.google.com/sie-kfkk-wiv",
                    room_id="sie-kfkk-wiv",
                    started_at=scheduled_datetime,
                    ended_at=scheduled_datetime+30,
                    status=VIDEO_SESSION_STATUS.SCHEDULED
                )

                created_consultations.append(
                    new_consultation
                )
            
            consultation.delete()
            return created_consultations

class ConsultationRescheduleSerializer(serializers.Serializer):
    scheduled_at = serializers.DateTimeField()
    timezone = serializers.CharField(required=False)

    def validate_scheduled_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Reschedule time must be in the future."
            )
        return value

# -----------------------------------------------------------------------------------------------------



# Consultation Details Serializers------------------------------------------------------------------------
class ConsultationPatientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = ["id", "full_name", "date_of_birth", "gender", "country", "medical_notes"]

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
