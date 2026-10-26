from rest_framework import serializers


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    service = serializers.CharField()
    phase = serializers.IntegerField()
    python_version = serializers.CharField()
    django_version = serializers.CharField()


class ReadinessSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["ready", "unavailable"])
    database = serializers.CharField()
    postgis_version = serializers.CharField(allow_null=True)
    message = serializers.CharField()


class ModuleSerializer(serializers.Serializer):
    name = serializers.CharField()
    phase = serializers.IntegerField()
    status = serializers.CharField()


class CapabilitiesSerializer(serializers.Serializer):
    phase = serializers.IntegerField()
    scientific_data_loaded = serializers.BooleanField()
    modules = ModuleSerializer(many=True)
