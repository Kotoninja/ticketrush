from booking.models import Booking
from common.models import BaseModel
from django.db import models


class Payment(BaseModel):
    BOOKING_STATUS = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    )
    booking = models.ForeignKey(to=Booking, on_delete=models.PROTECT)
    status = models.CharField(choices=BOOKING_STATUS, default="draft")
    payment_id = models.UUIDField()
