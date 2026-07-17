from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from session.models import SeatSession
from session.services import SeatSessionService
from user.models import CustomUser

from booking.models import Booking


class BookingService:
    @staticmethod
    @transaction.atomic
    def create(*, user: CustomUser, seat_session: SeatSession) -> Booking:
        if not user:
            raise ValueError("user is required")

        if not seat_session:
            raise ValueError("seat_session is required")

        SeatSessionService.set_status(seat_session.pk, status="pending")

        new_booking_instance = Booking.objects.create(
            user=user, seat_session=seat_session
        )

        return new_booking_instance

    @transaction.atomic
    def delete(*, pk: int | None) -> tuple[int, dict[str, int]]:
        try:
            booking = Booking.objects.get(pk=pk)
            print("FREEEE")
            SeatSessionService.set_status(booking.seat_session.pk, status="free")

            return booking.delete()
        except Booking.DoesNotExist:
            raise ObjectDoesNotExist(f" object with {pk} pk does not exist")
