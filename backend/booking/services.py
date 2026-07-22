from typing import cast

from celery import Task
from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError
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
            raise ValidationError({"user":"user is required"})

        if not seat_session:
            raise ValidationError({"seat_session":"seat_session is required"})

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

        filtered_kwargs: dict = {k: v for k, v in kwargs.items() if v is not None}
        queryset = queryset.filter(**filtered_kwargs)

        queryset = queryset.filter(user=request.user)
        return queryset

    @staticmethod
    @transaction.atomic
    def create(*, user: CustomUser, seat_session: SeatSession) -> Booking:
        from booking.tasks import draft_seat

        BookingService._check_user_and_seat_session(user, seat_session)

        SeatSessionService.set_status(seat_session.pk, status="pending")

        new_booking_instance = Booking.objects.create(
            user=user, seat_session=seat_session
        )

        cast(Task, draft_seat).apply_async(
            kwargs={"pk": new_booking_instance.pk}, countdown=300
        )

        return new_booking_instance

    @staticmethod
    @transaction.atomic
    def delete(*, booking: Booking) -> tuple[int, dict[str, int]]:
        SeatSessionService.set_status(booking.seat_session.pk, status="free")
        return booking.delete()

    @staticmethod
    @transaction.atomic
    def confirm(*, booking: Booking):
        booking.status = "paid"
        booking.save()
        SeatSessionService.set_status(booking.seat_session.pk, status="busy")

