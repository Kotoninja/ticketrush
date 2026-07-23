from typing import cast

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from payment.services import PaymentService
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import BookingStatusException
from .models import Booking
from .serializers import BookingReadSerializer, BookingWriteSerializer
from .services import BookingService


class BookingRetrieveView(APIView):
    def get(self, request, seat_session_pk):
        booking_instance = BookingService.get_object(
            request=request, seat_session=seat_session_pk
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
    # add permission

    def delete(self, request, pk: None):
        booking = get_object_or_404(Booking, pk=pk)
        BookingService.delete(booking=booking)
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
    def post(self, request, pk: int | None):
        try:
            result = PaymentService.create_payment(user=request.user, booking_pk=pk)
            return Response(result)
        except BookingStatusException as e:
            raise ValidationError({"detail": e})
