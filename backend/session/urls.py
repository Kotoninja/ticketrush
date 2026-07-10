from rest_framework import routers
from django.urls import path
from .views import EventSessionAPI, index

router = routers.SimpleRouter()
router.register("", EventSessionAPI)

urlpatterns = [path("index/", index  )] + router.urls
