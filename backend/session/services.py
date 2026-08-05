from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from .models import EventSession, SeatSession


def attach_all_places_to_event_session(
    event_session_instance: EventSession,
) -> EventSession:
    hall_seats = event_session_instance.hall.seat_set.all()
    SeatSession.objects.bulk_create(
        [
            SeatSession(  # type: ignore
                event_session=event_session_instance,
                seat=seat,
                status="free",
                price=99.00,
            )
            for seat in hall_seats
        ]
    )

    return event_session_instance


def event_search_filter(request) -> Q:
    search = request.query_params["search"]
    base_filter: Q = Q(event__name__search=search) | Q(event__name__icontains=search)

    if venue := request.query_params.get("venue", None):
        base_filter &= Q(hall__venue=venue)

    return base_filter


class SeatSessionService:
    @staticmethod
    def set_status(seat_session_pk: int, *, status: str) -> SeatSession:
        with transaction.atomic():
            try:
                seat_session_instance: SeatSession = (
                    SeatSession.objects.select_for_update().get(pk=seat_session_pk)
                )

                if status == "pending" and seat_session_instance.status != "free":
                    raise ValidationError(
                        {"seat_session": "the place is already taken"}
                    )

                seat_session_instance.status = status
                seat_session_instance.save()
                return seat_session_instance

            except SeatSession.DoesNotExist:
                raise ObjectDoesNotExist(
                    f"Seat session with {seat_session_pk} pk not found"
                )
