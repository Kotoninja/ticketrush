from typing import cast

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking
from .serializers import BookingReadSerializer, BookingWriteSerializer
from .services import BookingService


class BookingRetrieveView(APIView):
    def get(self, request, seat_session_pk):
        booking_instance = get_object_or_404(
            Booking.objects.all(), user=request.user, seat_session=seat_session_pk
        )
        serializer = BookingReadSerializer(booking_instance)
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
            user=request.user,
            seat_session=validated_data["seat_session"],
        )

        response_serializer = BookingReadSerializer(new_booking)
        return Response(data=response_serializer.data)


class BookingDeleteView(APIView):
    def delete(self, request, pk: None):
        BookingService.delete(user=request.user, pk=pk)
        return Response(data="Successfully deleted", status=status.HTTP_200_OK)


class BookingListView(APIView):
    @extend_schema(
        responses={200: BookingReadSerializer},
        parameters=[
            OpenApiParameter("venue_pk", type=int, description="search by venue")
        ],
    )
    def get(self, request):
        booking_list = Booking.objects.select_related(
            "seat_session__event_session__hall__venue"
        ).filter(user=request.user)

        if venue_pk := request.query_params.get("venue_pk"):
            booking_list = booking_list.filter(
                seat_session__event_session__hall__venue=venue_pk
            )

        if booking_list:
            serializer = BookingReadSerializer(booking_list, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=[], status=status.HTTP_200_OK)
