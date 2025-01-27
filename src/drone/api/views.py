from rest_framework import viewsets, mixins
from src.drone.enums import DroneState
from src.drone.models import Drone, Medication
from src.drone.api.serialiazers import DroneSerializer, LoadMedicationSerializer, MedicationSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from django.utils.timezone import now
from django.db.models import Q


def _calculate_battery_depletion(drone: Drone):
    """
    Battery drain is calculated based on two metrics; time and weight,
    We assume that 0.005% battery depletin per 1 gram and 0.002% battery depletion per minute
    """
    total_loaded_weight = sum(med.weight for med in drone.medications.all())

    battery_capacity_depletion_per_g = 0.005 # 0.005% battery depletion 1gr
    depletion_per_minutes = 0.002  # 0.002% battery depletion per minute

    # get time between now and last update
    btw_time_in_minutes = 0
    if drone.last_time_updated:
        btw_time = now() - drone.last_time_updated
        btw_time_in_minutes = btw_time.total_seconds() / 60 

    return (total_loaded_weight * battery_capacity_depletion_per_g) + (depletion_per_minutes * btw_time_in_minutes)


class RegisterDroneViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = DroneSerializer


class DroneViewset(ViewSet):
    """
    A Viewset for managing drone services, consisting of the following endpoint:
    - loading-medications [POST]
    - loaded-medications [GET]
    - available-drones [GET]
    - battery-level [GET]
    """

    @action(detail=True, methods=["post"], url_path="load-medications")
    def load_medications(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)
        med_data = request.data
        serializer = LoadMedicationSerializer(data=med_data, context={'drone': drone})
        serializer.is_valid(raise_exception=True)

        medication_ids = med_data.get("medication_ids", [])

        for med_id in medication_ids:
            medication = get_object_or_404(Medication, pk=med_id)
            medication.drone = drone
            medication.save()

        # update drone state if meds are loaded
        loaded_medications = drone.medications.all()
        if loaded_medications.count() > 0:
            drone.state = DroneState.LOADED
            drone.last_time_updated = now()
            drone.battery_capacity -= _calculate_battery_depletion(drone)
            drone.save()

        return Response(
            {
                "drone": {
                    "id": drone.id,
                    "serial_number": drone.serial_number,
                    "battery_capacity": drone.battery_capacity,
                    "state": drone.state.value,
                },
                "medications": MedicationSerializer(loaded_medications, many=True).data,
            },
        )

    @action(detail=True, methods=["get"], url_path="loaded-medications")
    def check_loaded_medictions(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)

        return Response({
            'drone': {
                'id': drone.id,
                'serial_number': drone.serial_number,
            },
            'loaded_medications': MedicationSerializer(drone.medications.all(), many=True).data
        })

    @action(detail=False, methods=["get"], url_path="available-drones")
    def check_available_drones(self, request):
        drones = Drone.objects.filter(Q(state=DroneState.IDLE) | Q(state=DroneState.RETURNING), battery_capacity__gte=25)

        return Response ({
            'available_drones': DroneSerializer(drones, many=True).data,
        })

    @action(detail=True, methods=["get"], url_path="battery-level")
    def check_battery_level(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)
        battery_capacity = drone.battery_capacity - _calculate_battery_depletion(drone)

        return Response({
            'drone': {
                'id': drone.id,
                'serial_number': drone.serial_number,
                'battery_capacity': round(battery_capacity, 0),
            },
        })
