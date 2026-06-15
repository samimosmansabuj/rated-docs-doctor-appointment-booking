from django.shortcuts import get_object_or_404
from datetime import datetime
from account.models import PatientProfile
from rest_framework import serializers
from .consultant_models import Consultation, ConsultationDentalHistory, ConsultationDentalPhoto, ConsultationXRay, ConsultationSchedule, VideoConsultationSession, ConsultationRescheduleRequest, RESCHEDULE_REQUEST_STATUS
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

class ConsultationTreatmentInterestStep2Serializer(serializers.Serializer):
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

class ConsultationBudgetTravelStep3Serializer(serializers.Serializer):
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

class ConsultationDentalHistoryStep4Serializer(serializers.Serializer):
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

class ConsultationDentalPhotoStep5Serializer(serializers.Serializer):
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

class ConsultationXrayStep6Serializer(serializers.Serializer):
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

class ConsultationScheduleStep7Serializer(serializers.Serializer):
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
                    status=VIDEO_SESSION_STATUS.SCHEDULED
                )

                created_consultations.append(
                    new_consultation
                )
            
            consultation.delete()
            return created_consultations


class CreateRescheduleRequestSerializer(serializers.Serializer):
    consultation_id = serializers.IntegerField(write_only=True)
    scheduled_date = serializers.DateField()
    scheduled_time = serializers.TimeField()
    timezone = serializers.CharField(required=False)
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        user = self.context["request"].user
        consultation = get_object_or_404(Consultation, id=attrs["consultation_id"])
        is_patient = (hasattr(user, "patient_profile") and consultation.patient == user.patient_profile)
        is_dentist = (hasattr(user, "dentist_profile") and consultation.dentist == user.dentist_profile)
        if not (is_patient or is_dentist):
            raise serializers.ValidationError(
                "You are not allowed for this consultation."
            )
        attrs["consultation"] = consultation
        return attrs

    def create(self, validated_data):
        scheduled_datetime = datetime.combine(validated_data.get("scheduled_date"), validated_data.get("scheduled_time"))
        if timezone.make_aware(scheduled_datetime) <= timezone.now():
            raise serializers.ValidationError(
                "Schedule time must be in the future."
            )
        return ConsultationRescheduleRequest.objects.create(
            consultation=validated_data["consultation"],
            requested_by=self.context["request"].user,
            proposed_datetime=scheduled_datetime,
            timezone=validated_data.get("timezone", "EST"),
            reason=validated_data.get("reason", "")
        )

class RescheduleDecisionSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=["accept", "reject"])

    def save(self):
        user = self.context["request"].user
        request_obj = get_object_or_404(ConsultationRescheduleRequest, id=self.validated_data["request_id"], status=RESCHEDULE_REQUEST_STATUS.PENDING)
        consultation = request_obj.consultation
        is_patient = (hasattr(user, "patient_profile") and consultation.patient == user.patient_profile)
        is_dentist = (hasattr(user, "dentist_profile") and consultation.dentist == user.dentist_profile)
        if not (is_patient or is_dentist):
            raise serializers.ValidationError(
                "Permission denied."
            )
        
        action = self.validated_data["action"]
        if action == "reject":
            request_obj.status = RESCHEDULE_REQUEST_STATUS.REJECTED
        elif action == "accept":
            request_obj.status = RESCHEDULE_REQUEST_STATUS.ACCEPTED 
            schedule = consultation.schedule
            schedule.re_scheduled_at = schedule.scheduled_at
            schedule.scheduled_at = request_obj.proposed_datetime
            schedule.re_scheduled_confirm = True
            schedule.save()

        request_obj.reviewed_by = user
        request_obj.reviewed_at = timezone.now()
        request_obj.save()
        return request_obj

# -----------------------------------------------------------------------------------------------------



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






# Treatment All Serializers------------------------------------------------------------------------
from .models import TreatmentPlan, TreatmentPlanProcedure, Appointment, AppointmentDecision
from core.constants import TREATMENT_PLAN_STAGE, APPOINTMENT_STATUS, APPOINTMENT_DECISION

class TreatmentPlanProcedureCreateSerializer(serializers.Serializer):
    procedure = serializers.PrimaryKeyRelatedField(queryset=Procedure.objects.all(), required=False, allow_null=True)
    title = serializers.CharField(required=False, allow_blank=True)
    estimated_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get("procedure") and not attrs.get("title"):
            raise serializers.ValidationError(
                "Procedure or title is required."
            )
        return attrs

class TreatmentPlanFileSerializer(serializers.Serializer):
    title = serializers.CharField()
    file = serializers.FileField()

class InitialTreatmentPlanCreateSerializer(serializers.Serializer):
    consultation_id = serializers.IntegerField(write_only=True)
    procedures = TreatmentPlanProcedureCreateSerializer(many=True)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)
    other_information = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        dentist = self.context["request"].user.dentist_profile
        consultation = Consultation.objects.get(id=self.validated_data["consultation_id"])
        with transaction.atomic():
            treatment_plan = TreatmentPlan.objects.create(
                consultation=consultation,
                created_by=dentist,
                version=TREATMENT_PLAN_STAGE.INITIAL,
                total_cost=validated_data["total_cost"],
                notes=validated_data.get("notes", ""),
                other_information=validated_data.get(
                    "other_information",
                    ""
                )
            )
            for item in validated_data["procedures"]:
                TreatmentPlanProcedure.objects.create(
                    treatment_plan=treatment_plan,
                    procedure=item.get("procedure"),
                    title=item.get("title"),
                    estimated_cost=item["estimated_cost"],
                    note=item.get("note", "")
                )
            Appointment.objects.create(
                consultation=consultation,
                patient=consultation.patient,
                dentist=dentist,
                initial_treatment_plan=treatment_plan,
                status=APPOINTMENT_STATUS.AWAITING_RESPONSE
            )
            consultation.status = CONSULTATION_STATUS.ESTIMATE_RECEIVED
            consultation.save(update_fields=["status"])
        return treatment_plan


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"


class AppointmentDecisionSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField(write_only=True)
    decision = serializers.ChoiceField(choices=APPOINTMENT_DECISION.choices)
    note = serializers.CharField(required=False, allow_blank=True)
    signature_image = serializers.ImageField()

    def create(self, validated_data):
        patient = self.context["request"].user.patient_profile
        appointment = Appointment.objects.get(id=validated_data["appointment_id"], patient=patient)
        decision = AppointmentDecision.objects.create(
            appointment=appointment,
            decision=validated_data["decision"],
            note=validated_data.get("note", ""),
            signature_image=validated_data["signature_image"]
        )
        if validated_data["decision"] == APPOINTMENT_DECISION.APPROVED:
            appointment.status = APPOINTMENT_STATUS.CONFIRMED
        else:
            appointment.status = APPOINTMENT_STATUS.CANCELLED
        appointment.save(update_fields=["status"])
        return decision

# -----------------------------------------------------------------------------------------------------



