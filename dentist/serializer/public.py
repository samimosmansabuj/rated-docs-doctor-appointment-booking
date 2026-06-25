from rest_framework import serializers
from account.models import User
from ..models import (
    Clinic,
    DentistProfile,
    DentistAddress,
    ProcedurePrice
)

class DentistUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone", "is_verified",]

class PublicClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ["id", "name", "address", "city", "country",]

class PublicDentistAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentistAddress
        fields = ["city", "country"]


class PublicProcedureSerializer(serializers.ModelSerializer):
    procedure_name = serializers.CharField(source="procedure.name", read_only=True)

    class Meta:
        model = ProcedurePrice
        fields = ["id", "procedure_name", "price", "currency",]

class PatientDentistDetailSerializer(serializers.ModelSerializer):
    user = DentistUserSerializer(read_only=True)
    clinic = PublicClinicSerializer(read_only=True)
    dentist_address = PublicDentistAddressSerializer(many=True, read_only=True)
    procedures = serializers.SerializerMethodField()

    class Meta:
        model = DentistProfile
        fields = [
            "id", "slug", "full_name", "specialty", "bio", "experience_years",
            "rating_avg","total_reviews",
            "rdv_score","response_time_avg",
            "is_verified",
            "user", "clinic","dentist_address",
            "procedures",
        ]

    def get_procedures(self, obj):
        try:
            operation = obj.operation_verification
        except:
            return []

        queryset = operation.procedures_feature.filter(is_active=True)
        return PublicProcedureSerializer(queryset, many=True).data


