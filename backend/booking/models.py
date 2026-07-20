from common.models import BaseModel
from django.db import models
from django.utils import timezone
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
    draft_expire_time = models.DateTimeField(null=True, blank=True)

    def is_available(self) -> bool:
        if self.draft_expire_time and timezone.now() > self.draft_expire_time:
            return False
        return True

    def clean(self):
        user_have_draft_event_session(self)
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        self.draft_expire_time = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)
