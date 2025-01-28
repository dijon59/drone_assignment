from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from .enums import DroneModel, DroneState
from enumfields import EnumField

OPTIONAL = {'null': True, 'blank': True}
DECIMAL_FIELD_PARAM = {'decimal_places': 1, 'default': 0.0, 'max_digits': 20}

class Drone(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    drone_model = EnumField(DroneModel, default=DroneModel.LIGHTWEIGHT, max_length=30)
    weight_limit = models.DecimalField(validators=[MinValueValidator(0), MaxValueValidator(500.0)], **DECIMAL_FIELD_PARAM)
    battery_capacity = models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], **DECIMAL_FIELD_PARAM)
    state = EnumField(DroneState, default=DroneState.IDLE, max_length=20)
    created_at = models.DateTimeField(auto_now=True)
    last_time_updated = models.DateTimeField(**OPTIONAL)

    def __str__(self):
        return f'Drone-{self.id} - {self.serial_number}'


class Medication(models.Model):

    drone = models.ForeignKey(Drone, on_delete=models.PROTECT, **OPTIONAL, related_name='medications')
    name = models.CharField(max_length=100, validators=[
        RegexValidator(
            regex=r'^(?=.*[a-zA-Z0-9])[a-zA-Z0-9-_]+$',
            message='Invalid Format'
        )
    ])
    weight = models.DecimalField(validators=[MinValueValidator(0.0)], **DECIMAL_FIELD_PARAM)
    code = models.CharField(max_length=100, validators=[
        RegexValidator(
            regex=r'^(?=.*[a-zA-Z0-9])[a-zA-Z0-9_]+$',
            message='Invalid Format'
        )
    ], unique=True)
    image = models.ImageField(upload_to='med_images/', **OPTIONAL)
    created_at = models.DateTimeField(auto_now=True)


class DroneBatteryLogHistory(models.Model):
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE)
    battery_capacity = models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], **DECIMAL_FIELD_PARAM)
    created_at = models.DateTimeField(auto_now=True)
