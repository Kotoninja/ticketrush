from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingReadSerializer


class BookingRetrieveView(generics.RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingReadSerializer

    def get(self, request, user_pk, seat_session_pk):
        booking_instance = get_object_or_404(
            self.get_queryset(), user=user_pk, seat_session=seat_session_pk
        )
        serializer = self.get_serializer(booking_instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
