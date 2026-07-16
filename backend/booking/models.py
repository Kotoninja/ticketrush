from common.models import BaseModel
from django.db import models
from session.models import SeatSession
from user.models import CustomUser

from .validators import user_have_draft_event_session


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

    def clean(self):
        user_have_draft_event_session(self)
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
