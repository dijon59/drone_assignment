from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import RegisterDroneViewset, LoadMedicationView


router = DefaultRouter()

router.register('register-drone', RegisterDroneViewset, basename='register-drone')
# router.register('drones', DroneViewset, basename='drones')

urlpatterns = [
    path('', include(router.urls)),
    path('drones/<int:drone_id>/load-medications/', LoadMedicationView.as_view(), name='load-medications')
]
