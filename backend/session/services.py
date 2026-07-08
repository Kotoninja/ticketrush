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
