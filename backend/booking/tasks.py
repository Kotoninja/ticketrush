from celery import shared_task
from .models import Booking
from booking.services import BookingService


@shared_task
def draft_seat(*, pk: int):
    try:
        BookingService.delete(pk=pk)
    except Booking.DoesNotExist:
        pass
