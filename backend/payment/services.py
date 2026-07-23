from typing import TYPE_CHECKING

from booking.exceptions import BookingStatusException
from booking.models import Booking
from booking.services import BookingService
from django.shortcuts import get_object_or_404

from .models import Payment

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


class WebhookService:
    @staticmethod
    def execute(data) -> None:
        payment = get_object_or_404(Payment, payment_id=data["payment_id"])

        result = data["result"]

        match result:
            case "pending":
                pass
            case "success":
                payment.status = "paid"
                payment.save()

                BookingService.confirm(booking=payment.booking)

                # tasks for ticket
            case "failed":
                payment.status = "failed"
                payment.save()

