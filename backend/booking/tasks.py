from celery import shared_task
from .models import Booking
from booking.services import BookingService


@shared_task
def draft_seat(*, user, pk: int):
    try:
        BookingService.delete(user=user, pk=pk)
    except Booking.DoesNotExist:
        pass
