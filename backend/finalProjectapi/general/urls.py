from django.urls import URLPattern, path

from .views import test

#URLConf
urlpatterns = [
    path('hello/',test.say_hello),
    path('json_get/',test.json_get),
]
