from celery import shared_task

from src.drone.api.views import calculate_battery_depletion
from .models import Drone, DroneBatteryLogHistory


@shared_task
def log_drone_battery_levels():
    drones = Drone.objects.all()
    for drone in drones:
        if drone.battery_capacity <= calculate_battery_depletion(drone):
            drone.battery_capacity = 0
            drone.save()
        else:
            print(drone.battery_capacity)
            print(calculate_battery_depletion(drone))

            drone.battery_capacity -= calculate_battery_depletion(drone)
            drone.save()

        DroneBatteryLogHistory.objects.create(
            drone=drone,
            battery_capacity=drone.battery_capacity,
        )
