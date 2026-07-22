from booking.models import Booking
from django.shortcuts import get_object_or_404
from typing import TYPE_CHECKING
from .models import Payment
from booking.exceptions import BookingStatusException

if TYPE_CHECKING:
    from user.models import CustomUser
import uuid


class PaymentService:
    @staticmethod
    def create_payment(user: CustomUser, booking_pk: int | None) -> dict[str, str]:
        booking = get_object_or_404(Booking, pk=booking_pk, user=user)

        if booking.seat_session.status == "pending":
            # request to bank

            payment = Payment.objects.create(
                booking=booking, status="pending", payment_id=uuid.uuid4()
            )

            return {"payment_url": f"https://fake-bank.com/pay/{payment.payment_id}"}
        else:
            raise BookingStatusException("The booking time has expired")
