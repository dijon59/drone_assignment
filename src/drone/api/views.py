from decimal import Decimal
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
from rest_framework import status


def calculate_battery_depletion(drone: Drone):
    """
    Battery drain is calculated based on two metrics; time and weight,
    We assume that 0.005% battery depletin per 1 gram and 0.002% battery depletion per minute
    """
    total_loaded_weight = sum(med.weight for med in drone.medications.all())

    battery_capacity_depletion_per_g = Decimal(0.005) # 0.005% battery depletion 1gr
    depletion_per_minutes = Decimal(0.002)  # 0.002% battery depletion per minute

    # get time between now and last update
    btw_time_in_minutes = 0
    if drone.last_time_updated:
        btw_time = now() - drone.last_time_updated
        btw_time_in_minutes =  Decimal(btw_time.total_seconds()) / Decimal(60) 

    return (total_loaded_weight * battery_capacity_depletion_per_g) + (depletion_per_minutes * btw_time_in_minutes)


class DroneViewset(ViewSet):
    """
    A Viewset for managing drone services, consisting of the following endpoint:
    - register-drone [POST]
    - loading [PUT]
    - loading-medications [POST]
    - loaded-medications [GET]
    - available-drones [GET]
    - battery-level [GET]
    - delivering [PUT]
    - delivered [PUT]
    - returning [PUT]
    """

    @action(detail=False, methods=["post"], url_path="register-drone")
    def register_drone(self, request):
        serializer = DroneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put"], url_path="loading")
    def set_drone_to_loading(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)

        if drone.state != DroneState.IDLE:
            return Response({'error': f'Drone unable to be set to loading, needs to be set to Idle state.'}, status=status.HTTP_400_BAD_REQUEST)

        if drone.battery_capacity < 25:
            return Response({'error': 'Can not load medication, battery capacity is low.'}, status=status.HTTP_400_BAD_REQUEST)

        drone.state = DroneState.LOADING
        drone.save()

        return Response({
            'message': 'Drone is loading',
            'drone': {
                'id': drone.id,
                'state': drone.state.value,
            },
        })

    @action(detail=True, methods=["post"], url_path="load-medications")
    def load_medications(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)
        med_data = request.data
        serializer = LoadMedicationSerializer(data=med_data, context={'drone': drone})
        serializer.is_valid(raise_exception=True)

        medication_ids = med_data.get("medication_ids", [])

        # we set drone state to Loading when meds are in process to be loaded
        if medication_ids:
            drone.state = DroneState.LOADING
            drone.save()

        for med_id in medication_ids:
            medication = get_object_or_404(Medication, pk=med_id)
            medication.drone = drone
            medication.save()

        # update drone state if meds are loaded
        loaded_medications = drone.medications.all()
        if loaded_medications.count() > 0:
            drone.state = DroneState.LOADED
            drone.last_time_updated = now()
            drone.battery_capacity -= calculate_battery_depletion(drone)
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
        drones = Drone.objects.filter(state=DroneState.IDLE, battery_capacity__gte=25)

        return Response ({
            'available_drones': DroneSerializer(drones, many=True).data,
        })

    @action(detail=True, methods=["get"], url_path="battery-level")
    def check_battery_level(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)
        battery_capacity = drone.battery_capacity - calculate_battery_depletion(drone)

        return Response({
            'drone': {
                'id': drone.id,
                'serial_number': drone.serial_number,
                'battery_capacity': round(battery_capacity, 0),
            },
        })

    @action(detail=True, methods=["put"], url_path="delivering")
    def set_drone_as_delivering(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)

        if drone.state != DroneState.LOADED:
            return Response({'error': 'Drone needs to be loaded before starting deliveries'}, status=status.HTTP_400_BAD_REQUEST)

        drone.state = DroneState.DELIVERING
        drone.save()

        return Response({
            'message': 'Drone set to delivering',
            'drone': {
                'id': drone.id,
                'state': drone.state.value,
            },
        })

    @action(detail=True, methods=["put"], url_path="delivered")
    def set_drone_as_delivered(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)

        if drone.state != DroneState.DELIVERING:
            return Response({'error': 'Drone is not delivering any medications'}, status=status.HTTP_400_BAD_REQUEST)

        drone.state = DroneState.DELIVERED
        drone.medications.update(drone=None)
        drone.save()

        return Response({
            'message': 'Drone delivered medication',
            'drone': {
                'id': drone.id,
                'state': drone.state.value,
            },
        })

    @action(detail=True, methods=["put"], url_path="returning")
    def set_drone_as_returning(self, request, pk):
        drone = get_object_or_404(Drone, pk=pk)

        if drone.state != DroneState.DELIVERED:
            return Response({'error': 'Drone has not delivered any medications yet'}, status=status.HTTP_400_BAD_REQUEST)

        drone.state = DroneState.RETURNING
        drone.save()

        return Response({
            'message': 'Drone set to returning',
            'drone': {
                'id': drone.id,
                'state': drone.state.value,
            },
        })
