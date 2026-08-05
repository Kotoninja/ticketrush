from typing import TYPE_CHECKING

from django.db.models.manager import BaseManager
from rest_framework.exceptions import ValidationError

if TYPE_CHECKING:
    from .models import Booking


def user_have_draft_event_session(booking_instance: Booking):
    """
    If a user already has a seat in an event session, then another booking cannot be created with a draft.
    """
    from .models import Booking

    Booking.objects.select_related("seat_session_event_session")

    has_draft_bookings: BaseManager[Booking] = Booking.objects.filter(
        seat_session__event_session=booking_instance.seat_session.event_session,
        status="draft",
    ).exclude(pk=booking_instance.pk)

    if has_draft_bookings.exists():
        raise ValidationError(
            f"You are already book a space until {has_draft_bookings.first().draft_expire_time}. Concurrent book are not possible. To book a new space, please end the current book early, wait until it ends, or contact support to arrange a replacement."
        )
