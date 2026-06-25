from rest_framework import serializers
from .models import Procedure


class SubProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ["id", "name", "details", "base_price", "is_active",]


class ProcedureSerializer(serializers.ModelSerializer):
    sub_procedures = SubProcedureSerializer(many=True, read_only=True)

    class Meta:
        model = Procedure
        fields = ["id", "parent", "name", "type", "details", "base_price", "is_active", "sub_procedures",]


from rest_framework import serializers
from .models import LicenseRegistrationAuthority


class LicenseRegistrationAuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseRegistrationAuthority
        fields = ["id", "name", "country", "city", "address", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

