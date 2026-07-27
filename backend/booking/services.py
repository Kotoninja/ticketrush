from typing import cast

from celery import Task
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
        """Check if the input data (user, location session) exists."""
        if not user:
            raise ValidationError({"user": "user is required"})

        if not seat_session:
            raise ValidationError({"seat_session": "seat_session is required"})

    @staticmethod
    def get_object(request, *args, **kwargs) -> Booking:
        """Return Booking object with user by request method and other Booking kwargs values

        Args:
            request (HttpRequest): The HTTP request containing the authenticated user.
            **kwargs : Additional keyword arguments to populate the Booking fields.

        Returns:
            Booking: A Booking instance.
        """

        object = get_object_or_404(
            Booking.objects.filter(filters.available()), user=request.user, **kwargs
        )

        return object

    @staticmethod
    def get_queryset(
        request, queryset: None | QuerySet[Booking] = None, *args, **kwargs
    ) -> QuerySet[Booking]:
        """Return a Booking queryset filter by kwargs and user

        Args:
            request (HttpRequest): The HTTP request containing the authenticated user.
            queryset (None | QuerySet[Booking], optional): Pass on your own queryset. Defaults to None.

        Returns:
            QuerySet[Booking]: Booking QuerySet
        """

        if queryset is None:
            queryset = Booking.objects.all()

        filtered_kwargs: dict = {k: v for k, v in kwargs.items() if v is not None}
        queryset = queryset.filter(**filtered_kwargs)

        queryset = queryset.filter(user=request.user)
        return queryset

    @staticmethod
    @transaction.atomic
    def create(*, user: CustomUser, seat_session: SeatSession) -> Booking:
        """Create a new Booking for a user and seat session, and schedule the draft task.

        Marks the seat session as "pending", creates the Booking record, and
        schedules the `draft_seat` Celery task to run after a 300 second
        countdown (giving the user a window to confirm before the seat is
        released or drafted).

        Args:
            user (CustomUser): The user the booking is created for.
            seat_session (SeatSession): The seat session being booked.

        Raises:
            ValidationError: If `user` or `seat_session` is missing/falsy.

        Returns:
            Booking: The newly created Booking instance.
        """
        from booking.tasks import draft_seat

        BookingService._check_user_and_seat_session(user, seat_session)

        new_booking_instance = Booking.objects.create(
            user=user, seat_session=seat_session
        )

        SeatSessionService.set_status(seat_session.pk, status="pending")

        cast(Task, draft_seat).apply_async(
            kwargs={"pk": new_booking_instance.pk}, countdown=300
        )

        return new_booking_instance

    @staticmethod
    @transaction.atomic
    def delete(*, booking: Booking) -> tuple[int, dict[str, int]]:
        """Delete a Booking and free up its associated seat session.

        Sets the related seat session's status back to "free" before deleting
        the Booking record.

        Args:
            booking (Booking): The booking to delete.

        Returns:
            tuple[int, dict[str, int]]: The result of Django's `QuerySet.delete()`/
                model `delete()` call — the total number of objects deleted and
                a dictionary mapping each model to the number of deletions.
        """
        SeatSessionService.set_status(booking.seat_session.pk, status="free")
        return booking.delete()

    @staticmethod
    @transaction.atomic
    def confirm(*, booking: Booking) -> None:
        """Confirm a Booking as paid and mark its seat session as busy.

        Updates the booking's status to "paid" (saving only that field) and
        sets the associated seat session's status to "busy".

        Args:
            booking (Booking): The booking to confirm.

        Returns:
            None
        """
        booking.status = "paid"
        booking.save(update_fields=["status"])
        SeatSessionService.set_status(booking.seat_session.pk, status="busy")
