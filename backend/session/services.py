from .models import EventSession, SeatSession
from django.db.models import Q


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
