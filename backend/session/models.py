from common.models import BaseModel
from django.db import models
from event.models import Event
from hall.models import Hall
from seat.models import Seat
from venue.models import Venue


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

    def __str__(self) -> str:
        return f"{self.event.name} / {self.hall.venue.name} / {self.hall.number} / {self.timestamp}"


class SeatSession(BaseModel):
    SEAT_STATUS: list[tuple[str, str]] = [
        ("free", "Free"),
        ("pending", "Pending"),
        ("busy", "Busy"),
    ]
    event_session = models.ForeignKey(to=EventSession, on_delete=models.PROTECT, related_name="seats")
    seat = models.ForeignKey(to=Seat, on_delete=models.PROTECT)
    status = models.CharField(choices=SEAT_STATUS, default="free")
    price = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event_session", "seat"],
                name="Unique SeatSession in definitely event_session",
            )
        ]
