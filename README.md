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
4. Start database migrations and create user
```
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createsuperuser
``` 
5. Run tests
```
in project directory run the following command:
$ python manage.py test src.drone.tests
```