# Drone Assignment


## Prerequisites
- Python 3.9+


## Setup

1. Clone the repository:
```
$ git clone git@github.com:dijon59/drone_assignment.git
$ cd drone_assignment
```

2. Create virtual environment
```
$ python3 -m venv venv
$ source venv/bin/activate # on windows: venv\Scripts\activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Start database migrations and add preload data
```
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py loaddata preload_data.json
```
5. Run Redis, Celery worker and beat command
- Make sure redis is installed in your computer
- run these commands on different terminals
```
$ redid-server
$ celery -A src.project worker -l info
$ celery -A src.project beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

6. Run tests
```
in project directory run the following command:
$ python manage.py test src.drone.tests
```

## Alternatively use Run docker-compose file
- MAKE SURE YOU HAVE DOCKER AND DOCKER-COMPOSE INSTALLED IN YOUR MACHINE
- In the project directory, run the following command:
```
$ docker-compose up -d --build
```
But you will still need to run the following command in you project directory:
```
$ python manage.py loaddata preload_data.json
```

## API Information
the following are the different endpoint of the project:

- register drone [POST] : 'http://127.0.0.1:8000/drones/register-drone/' 
- loading [PUT] : 'http://127.0.0.1:8000/drones/<int:pk>/loading/' 
- load medications [POST] : 'http://127.0.0.1:8000/drones/<int:pk>/load-medications/' 
- loaded medications [GET] : 'http://127.0.0.1:8000/drones/<int:pk>/loaded-medications/' 
- available drones [GET] : 'http://127.0.0.1:8000/drones/available-drones/' 
- battery level [GET] : 'http://127.0.0.1:8000/drones/<int:pk>/battery-level/' 
- delivering [PUT] : 'http://127.0.0.1:8000/drones/<int:pk>/delivering/'
- delivered [PUT] : 'http://127.0.0.1:8000/drones/<int:pk>/delivered/'
- returning [PUT] : 'http://127.0.0.1:8000/drones/<int:pk>/returning/'
