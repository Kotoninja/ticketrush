from django.urls import path
from rest_framework import routers

from .views import EventSessionAPI

router = routers.SimpleRouter()
router.register("", EventSessionAPI)

urlpatterns = [] + router.urls
