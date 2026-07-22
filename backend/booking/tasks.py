from celery import shared_task
from .models import Booking
from booking.services import BookingService


@shared_task
def draft_seat(pk: int):
    try:
        Booking.objects.select_related("seat_session")
        if Booking.objects.get(pk=pk).seat_session.status == "pending":
            BookingService.delete(pk=pk)
    except Booking.DoesNotExist:
        pass
