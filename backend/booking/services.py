from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from session.models import SeatSession
from session.services import SeatSessionService
from user.models import CustomUser

from booking import filters
from booking.models import Booking


class BookingService:
    @staticmethod
    def _check_user_and_seat_session(
        user: CustomUser | None, seat_session: SeatSession | None
    ) -> None:
        if not user:
            raise ValueError("user is required")

        if not seat_session:
            raise ValueError("seat_session is required")

    @staticmethod
    def get_object(request, *args, **kwargs) -> Booking:
        object = get_object_or_404(
            Booking.objects.filter(filters.availiable()), user=request.user, **kwargs
        )

        return object

    @staticmethod
    def get_queryset(
        request, queryset: None | QuerySet[Booking] = None, *args, **kwargs
    ):
        if queryset is None:
            queryset = Booking.objects.all()

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        queryset = queryset.filter(**kwargs)

        queryset = queryset.filter(user=request.user)
        return queryset

    @staticmethod
    @transaction.atomic
    def create(*, user: CustomUser, seat_session: SeatSession) -> Booking:
        BookingService._check_user_and_seat_session(user, seat_session)

        SeatSessionService.set_status(seat_session.pk, status="pending")

        new_booking_instance = Booking.objects.create(
            user=user, seat_session=seat_session
        )

        return new_booking_instance

    @staticmethod
    @transaction.atomic
    def delete(*, pk: int | None) -> tuple[int, dict[str, int]]:
        booking = get_object_or_404(Booking, pk=pk)
        SeatSessionService.set_status(booking.seat_session.pk, status="free")
        
        return booking.delete()

    @staticmethod
    @transaction.atomic
    def confirm(*, user: CustomUser, seat_session: SeatSession):
        BookingService._check_user_and_seat_session(user, seat_session)

        if Booking.objects.filter(user=user, seat_session=seat_session).exists():
            SeatSessionService.set_status(seat_session.pk, status="busy")

        raise ValidationError(
            f"Object with user - {user} and seat_session - {seat_session.pk}"
        )
