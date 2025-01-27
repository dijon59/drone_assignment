from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import RegisterDroneViewset, DroneViewset


router = DefaultRouter()

router.register('register-drone', RegisterDroneViewset, basename='register-drone')
router.register('drones', DroneViewset, basename='drones')

urlpatterns = [
    path('', include(router.urls)),
]
