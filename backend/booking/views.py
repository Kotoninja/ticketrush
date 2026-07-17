from typing import cast

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking
from .serializers import BookingReadSerializer, BookingWriteSerializer
from .services import BookingService
from drf_spectacular.utils import extend_schema


class BookingRetrieveView(generics.RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingReadSerializer

    def get(self, request, user_pk, seat_session_pk):
        booking_instance = get_object_or_404(
            self.get_queryset(), user=user_pk, seat_session=seat_session_pk
        )
        serializer = self.get_serializer(booking_instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class BookingCreateView(APIView):
    @extend_schema(
        request=BookingWriteSerializer, responses={201: BookingReadSerializer}
    )
    def post(self, request):

        serializer = BookingWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict, serializer.validated_data)

        new_booking = BookingService.create(
            user=validated_data["user"],
            seat_session=validated_data["seat_session"],
        )

        response_serializer = BookingReadSerializer(new_booking)
        return Response(data=response_serializer.data)


class BookingDeleteView(APIView):
    def delete(self, request, pk: None):
        if pk is None:
            return Response(
                {"error": "Method 'DELETE' not allowed without an ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        BookingService.delete(pk=pk)
        return Response(data="Successfully deleted", status=status.HTTP_200_OK)
