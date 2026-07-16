from django.db import transaction
from session.models import SeatSession
from session.services import SeatSessionService
from user.models import CustomUser

from booking.models import Booking


class BookingService:
    @staticmethod
    def create(*, user: CustomUser, seat_session: SeatSession) -> Booking:
        with transaction.atomic():
            if not user:
                raise ValueError("user is required")

            if not seat_session:
                raise ValueError("seat_session is required")

            SeatSessionService.set_pending(seat_session_pk=seat_session.pk)

            new_booking_instance = Booking.objects.create(
                user=user, seat_session=seat_session
            )

            return new_booking_instance
