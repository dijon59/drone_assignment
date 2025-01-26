from django.contrib import admin
from .models import Drone, Medication


@admin.register(Drone)
class DroneModelAdmin(admin.ModelAdmin):
    list_display = ['id','serial_number', 'drone_model', 'weight_limit', 'battery_capacity', 'state']
    search_fields = ['serial_number']


@admin.register(Medication)
class MedicationModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight', 'code']
