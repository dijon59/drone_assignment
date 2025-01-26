from enumfields import Enum


class DroneState(Enum):
    IDLE = 'Idle'
    LOADING = 'Loading'
    LOADED = 'Loaded'
    DELIVERING = 'Delivering'
    DELIVERED = 'Delivered'
    RETURNING = 'Returning'


class DroneModel(Enum):
    LIGHTWEIGHT = 'Lightweight'
    MIDDLEWEIGHT = 'Middleweight'
    CRUISERWEIGHT = 'Cruiserweight'
    HEAVYWEIGHT = 'Heavyweight'
