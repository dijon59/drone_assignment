import unittest
from unittest.mock import MagicMock, patch
from datetime import timedelta
from django.utils import timezone

from src.drone.enums import DroneState
from src.drone.api.views import _calculate_battery_depletion

from .models import Drone, Medication
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.urls import get_resolver
from rest_framework import status


# def print_urls():
#     for url in get_resolver().reverse_dict:
#         if isinstance(url, str):
#             print(url)


class TestDroneAPIAndCalculateBatteryDepletion(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Set up mock Drone instance
        self.drone_1 = Drone.objects.create(
            serial_number = 'drone1',
            weight_limit=500.0,
            battery_capacity=100,
            state=DroneState.IDLE,
        )

        self.drone_2 = Drone.objects.create(
            serial_number = 'drone2',
            weight_limit=500.0,
            battery_capacity=100,
            state=DroneState.IDLE,
        )

        self.drone_3 = Drone.objects.create(
            serial_number = 'drone3',
            weight_limit=500.0,
            battery_capacity=100,
            state=DroneState.DELIVERING,
        )

        self.drone_4 = Drone.objects.create(
            serial_number = 'drone4',
            weight_limit=200.0,
            battery_capacity=20,
            state=DroneState.IDLE,
        )

        self.med1 = Medication.objects.create(
            name="Mediction1",
            weight=100,
            code='codexMed1',
        )

        self.med2 = Medication.objects.create(
            name="Mediction2",
            weight=200,
            code='codexMed2',
        )

    def test_battery_depletion_per_weight_and_time(self):
        """
        Test battery depletion based on two metrics, weight and time,

        # battery_capacity_depletion_per_g = 0.005
        # depletion_per_minutes = 0.002
        # weiht depletion: (100+200)g * battery_capacity_depletion_per_g = 1.5
        # time depletion: 30min * depletion_per_minutes = 0.06
        # expected_result = 1.56
        """
 
        past_time = timezone.now() - timedelta(minutes=30)

        self.drone_1.last_time_updated = past_time
        self.drone_1.save()

        # Load medications to drone
        self.med1.drone = self.drone_1
        self.med1.save()

        self.med2.drone = self.drone_1
        self.med2.save()

        result = _calculate_battery_depletion(self.drone_1)

        expected_result = 1.56

        self.assertAlmostEqual(result, expected_result)
    
    def test_can_not_load_medication_when_battery_lower_than_25_percent(self):

        url = reverse('drones-load-medications', kwargs={'pk': self.drone_4.pk})

        self.drone_4.battery_capacity=50
        self.drone_4.save()

        self.med1.drone = self.drone_4
        self.med1.save()

        self.med2.drone = self.drone_4
        self.med2.save()

        data = {
            'medication_ids': [self.med1.id, self.med2.id]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(str(response.data['non_field_errors'][0]), "Medication weight exceeds the drone's weight limit")
    
    def test_can_not_load_medication_that_exceed_drone_weight_limit(self):
        url = reverse('drones-load-medications', kwargs={'pk': self.drone_4.pk})


        data = {
            'medication_ids': [self.med1.id, self.med2.id]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(str(response.data['non_field_errors'][0]), 'Can not load medication, battery capacity is low')


    def test_load_medication_api(self):
        url = reverse('drones-load-medications', kwargs={'pk': self.drone_1.pk})

        data = {
            'medication_ids': [self.med1.id, self.med2.id]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['drone']['state'], DroneState.LOADED.value)

    def test_check_available_drone_api(self):
        """
        """
        url = reverse('drones-check-available-drones')
        response = self.client.get(url, format='json')
        expected_result = 2
        self.assertEqual(len(response.data['available_drones']), expected_result)

    def test_check_loaded_medications_api(self):
        """
        """
        # Load medications to drone
        self.med1.drone = self.drone_1
        self.med1.save()

        self.med2.drone = self.drone_1
        self.med2.save()

        url = reverse('drones-check-loaded-medictions', kwargs={'pk': self.drone_1.pk})

        response = self.client.get(url)

        expected_result = 2

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['loaded_medications']), expected_result)

    def test_check_battery_level_api(self):
        """
        Test battery level api,

        # Weiht depletion: (100+200)g * battery_capacity_depletion_per_g = 1.5
        # expected_result = 100 - 1.5 = 98.5 -> 98 based on round(battery_capacity, 0)
        """
        # Load medications to drone
        self.med1.drone = self.drone_1
        self.med1.save()

        self.med2.drone = self.drone_1
        self.med2.save()

        url = reverse('drones-check-battery-level', kwargs={'pk': self.drone_1.pk})

        response = self.client.get(url)

        expected_result = 98

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['drone']['battery_capacity'], expected_result)


if __name__ == "__main__":
    unittest.main()
