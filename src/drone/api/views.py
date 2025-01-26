from rest_framework import viewsets, mixins
from src.drone.models import Drone, Medication
from src.drone.api.serialiazers import DroneSerializer, LoadMedicationSerializer, MedicationSerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


class RegisterDroneViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = DroneSerializer


class LoadMedicationView(APIView):
    def post(self, request, drone_id):
        drone = get_object_or_404(Drone, pk=drone_id)
        med_data = request.data
        serializer = LoadMedicationSerializer(data=med_data, context={'drone': drone})
        serializer.is_valid(raise_exception=True)

        medication_ids = med_data.get("medication_ids", [])

        for med_id in medication_ids:
            medication = get_object_or_404(Medication, pk=med_id)
            medication.drone = drone
            medication.save()

        # update drone state if meds are loaded
        if drone.medications.all().count() > 0:
            drone.state = "LOADED"
            drone.save()

        return Response(
            {
                "drone": {
                    "id": drone.id,
                    "serial_number": drone.serial_number,
                },
                "medications": MedicationSerializer(drone.medications.all(), many=True).data,
            }
        )
