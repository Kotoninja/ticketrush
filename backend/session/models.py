from common.models import BaseModel
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models, transaction
from django.utils import timezone
from event.models import Event
from hall.models import Hall
from rest_framework.exceptions import ValidationError as DRFValidationError
from seat.models import Seat


class EventSession(BaseModel):
    event = models.ForeignKey(to=Event, on_delete=models.PROTECT)
    hall = models.ForeignKey(
        to=Hall, on_delete=models.PROTECT, related_name="event_sessions"
    )
    timestamp = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "hall", "timestamp"],
                name="Unique session in definitely place and time",
            )
        ]

    def clean(self):
        if self.timestamp and self.timestamp <= timezone.now():
            raise DjangoValidationError(
                {
                    "timestamp": "The event session timestamp cannot be less than the current time."
                }
            )
        super().clean()

    def save(self, *args, **kwargs):
        from .services import attach_all_places_to_event_session

        try:
            self.full_clean()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)

        super().save(*args, **kwargs)

        with transaction.atomic():
            attach_all_places_to_event_session(self)

    def __str__(self) -> str:
        return f"{self.event.name} / {self.hall.venue.name} / {self.hall.number} / {self.timestamp}"


class SeatSession(BaseModel):
    SEAT_STATUS: list[tuple[str, str]] = [
        ("free", "Free"),
        ("pending", "Pending"),
        ("busy", "Busy"),
    ]

    event_session = models.ForeignKey(
        to=EventSession, on_delete=models.CASCADE, related_name="seats"
    )
    seat = models.ForeignKey(to=Seat, on_delete=models.PROTECT)
    status = models.CharField(choices=SEAT_STATUS, default="free")
    price = models.DecimalField(max_digits=4, decimal_places=2)

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event_session", "seat"],
                name="Unique SeatSession in definitely event_session",
            )
        ]
