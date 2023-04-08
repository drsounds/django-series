# Django Series

Django app providing Graphene endpoints and query aggregation feature which allows you to easily implement statistics charts in a django app. 

# 1. Installation

First add django_series to settings.py

````python
    INSTALLED_APPS = (
      ...,
      'django_series'
    )
````

## 1.2 Set up entities

Then you must map the entities you want to allow for building stats for in settings py,
which consists of an dictionary called DJANGO_SERIES_MODELS mapping path to valid Django models with shortnames eg.

````python

    DJANGO_SERIES_MODELS = {
        'book': 'my_project.models.Book',
        'stream': 'my_project.modes.Stream'
    }

````

# 2. Usage

The core feature of this library is the *compile_time_series_chart* function which 

# License

MIT