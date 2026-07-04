from rest_framework import routers

from .views import VenueAPI

router = routers.SimpleRouter()
router.register("", VenueAPI)

urlpatterns = [] + router.urls
