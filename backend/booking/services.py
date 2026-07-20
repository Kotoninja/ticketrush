from django.db import transaction
from rest_framework.exceptions import ValidationError
from session.models import SeatSession
from session.services import SeatSessionService
from user.models import CustomUser

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
    def delete(*, user: CustomUser, pk: int | None) -> tuple[int, dict[str, int]]:
        try:
            booking = Booking.objects.get(user=user, pk=pk)
            SeatSessionService.set_status(booking.seat_session.pk, status="free")

            return booking.delete()
        except Booking.DoesNotExist:
            raise ValidationError(f" object with {pk} pk does not exist")

    @staticmethod
    @transaction.atomic
    def confirm(*, user: CustomUser, seat_session: SeatSession):
        BookingService._check_user_and_seat_session(user, seat_session)

        if Booking.objects.get(user=user, seat_session=seat_session):
            SeatSessionService.set_status(seat_session.pk, status="busy")

        raise ValidationError(
            f"Object with user - {user} and seat_session - {seat_session.pk}"
        )

    @staticmethod
    @transaction.atomic
    def canceled(*, user: CustomUser, seat_session: SeatSession):
        BookingService._check_user_and_seat_session(user, seat_session)

        if booking := Booking.objects.get(user=user, seat_session=seat_session):
            SeatSessionService.set_status(seat_session.pk, status="free")

            booking.delete()

        raise ValidationError(
            f"Object with user - {user} and seat_session - {seat_session.pk}"
        )
