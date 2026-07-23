from celery import shared_task
from .models import Booking
from booking.services import BookingService


@shared_task
def draft_seat(pk: int):
    Booking.objects.select_related("seat_session")

    try:
        booking = Booking.objects.get(pk=pk, seat_session__status="pending")
        BookingService.delete(booking=booking)
    except Booking.DoesNotExist:
        pass
