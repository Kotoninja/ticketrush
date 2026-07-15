from common.models import BaseModel
from django.db import models

from user.models import CustomUser
from session.models import SeatSession


class Booking(BaseModel):
    BOOKING_STATUS = (
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    )

    user = models.ForeignKey(to=CustomUser, on_delete=models.PROTECT)
    seat_session = models.ForeignKey(to=SeatSession, on_delete=models.CASCADE)
    status = models.CharField(choices=BOOKING_STATUS, default="draft")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "seat_session"],
                name="user and seat_session must be unique.",
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
