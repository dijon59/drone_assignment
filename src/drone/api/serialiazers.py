from decimal import Decimal
from rest_framework import serializers
from src.drone.enums import DroneState
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['drone_model'] = str(instance.drone_model)
        data['state'] = str(instance.state)
        return data


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = (
            'id',
            'name',
            'weight',
            'code',
            'image',
            'created_at',
        )


class LoadMedicationSerializer(serializers.Serializer):
    medication_ids = serializers.ListField(child=serializers.IntegerField())

    def _total_weight(self, medications: Medication) -> float:
        """
        helper function to calculate total medication weight
        """
        total_weight = Decimal(0.0)
        for med in medications:
            total_weight += med.weight
        return total_weight

    def validate(self, attrs):
        drone: Drone = self.context['drone']
        medications = Medication.objects.filter(id__in=attrs['medication_ids'])
        med_total_weight = self._total_weight(medications)

        if drone.battery_capacity < 25:
            raise serializers.ValidationError("Can not load medication, battery capacity is low")

        if drone.state != DroneState.LOADING:
            raise serializers.ValidationError("Not valid state to load medication.")

        if med_total_weight > drone.weight_limit:
            raise serializers.ValidationError("Medication weight exceeds the drone's weight limit")

        return attrs
