from typing import cast

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from payment.services import PaymentService
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from silk.profiling.profiler import silk_profile

from .exceptions import BookingStatusException
from .models import Booking
from .serializers import BookingReadSerializer, BookingWriteSerializer
from .services import BookingService


class BookingRetrieveView(APIView):
    @extend_schema(
        summary="Find a reservation instance by seat",
        description="Find a reservation instance by seat ID. Return a single object.",
        responses={200: BookingReadSerializer},
    )
    def get(self, request, seat_session_pk):
        booking_instance = BookingService.get_object(
            request=request, seat_session=seat_session_pk
        )
        serializer = BookingReadSerializer(booking_instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class BookingCreateView(APIView):
    @silk_profile()
    @extend_schema(
        request=BookingWriteSerializer,
        responses={201: BookingReadSerializer},
        summary="Reserve a seat session in the hall",
        description='Assign the seat status to "draft". If the reservation is not paid for within 5 minutes, the seat status will be reset and the reservation will be deleted.',
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
    # add permission
    @extend_schema(request=None, responses=None, summary="Delete reservation")
    def delete(self, request, pk: None):
        booking = get_object_or_404(Booking, pk=pk)
        BookingService.delete(booking=booking)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingListView(APIView):
    @extend_schema(
        responses={200: BookingReadSerializer},
        parameters=[
            OpenApiParameter("venue_pk", type=int, description="search by venue")
        ],
        summary="All bookings",
        description="You can also specify a venue to filter.",
    )
    def get(self, request):
        booking_list = Booking.objects.select_related(
            "seat_session__event_session__hall__venue"
        )

        venue_pk = request.query_params.get("venue_pk")

        booking_list = BookingService.get_queryset(
            request=request,
            queryset=booking_list,
            seat_session__event_session__hall__venue=venue_pk,
        )

        serializer = BookingReadSerializer(booking_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class BookingPayView(APIView):
    @extend_schema(
        request=None,
        responses=None,
        summary="Pay reservation",
        description='This is a FAKE payment. After receiving the response, insert the UUI from "payment_url" into the "/api/payment/webhook" payment_id. This will reserve a seat in the event session.',
    )
    def post(self, request, pk: int | None):
        try:
            result = PaymentService.create_payment(user=request.user, booking_pk=pk)
            return Response(result)
        except BookingStatusException as e:
            raise ValidationError({"detail": e})
