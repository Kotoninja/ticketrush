from rest_framework import generics
from .models import Booking
from .serializers import BookingReadSerializer
from django.shortcuts import get_object_or_404


class BookingRetrieveView(generics.RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingReadSerializer
    lookup_field = "user"
    lookup_fields = ["user", "seat_session"]

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}

        for field in self.lookup_fields:
            filter[field] = self.kwargs[field]

        obj = get_object_or_404(queryset, **filter)
        return obj
