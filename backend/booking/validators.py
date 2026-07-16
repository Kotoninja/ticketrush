from typing import TYPE_CHECKING

from django.db.models import Q
from rest_framework.exceptions import ValidationError

if TYPE_CHECKING:
    from .models import Booking


def user_have_draft_event_session(booking_instance: Booking):
    """
    If a user already has a seat in an event session, then another booking cannot be created with a draft.
    """
    from .models import Booking

    if Booking.objects.filter(
        Q(seat_session__event_session=booking_instance.seat_session.event_session.pk)
        & Q(status="draft")
    ):
        raise ValidationError(
            "You are already book a space until [End Date]. Concurrent book are not possible. To book a new space, please end the current book early, wait until it ends, or contact support to arrange a replacement."
        )
