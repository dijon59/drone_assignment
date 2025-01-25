from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Drone(models.Model):

    drone_model_choices = [
        ('lightweight', 'Lightweight'),
        ('middleweight', 'Middleweight'),
        ('cruiserweight', 'Cruiserweight'),
        ('heavyweight', 'Heavyweight'),
    ]

    drone_states = [
        ('idle', 'IDLE'),
        ('loading', 'LOADING'),
        ('loaded', 'LOADED'),
        ('delivering', 'DELIVERING'),
        ('delivered', 'DELIVERED'),
        ('returning', 'RETURNING'),
    ]

    serial_number = models.CharField(max_length=100, unique=True)
    drone_model = models.CharField(max_length=30, choices=drone_model_choices, default='')
    weight_limit = models.FloatField(validators=[MaxValueValidator(500.0)])
    battery_capacity = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    state = models.CharField(max_length=20, choices=drone_states, default='')
    created_at = models.DateTimeField(auto_now=True)


class Medication(models.Model):
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    weight = models.FloatField()
    code = models.CharField(max_length=100)
    image = models.ImageField(upload_to='med_images/')
    created_at = models.DateTimeField(auto_now=True)
