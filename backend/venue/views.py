from .models import Venue
from rest_framework import viewsets
from .serializers import VenueSerializer


class VenueAPI(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
