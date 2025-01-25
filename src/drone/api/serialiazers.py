from rest_framework import serializers
from src.drone.models import Drone, Medication


class DroneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drone
        fields = (
            'id',
            'serial_number',
            'drone_model',
            'weight_limit',
            'battery_capacity',
            'state',
            'created_at',
        )


class MedicationSerializer(serializers.ModelSerializer):
    drone = serializers.PrimaryKeyRelatedField(
        queryset=Drone.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Medication
        fields = (
            'id',
            'drone',
            'name',
            'weight',
            'code',
            'image',
            'created_at',
        )
