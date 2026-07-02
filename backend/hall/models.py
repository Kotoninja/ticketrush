from common.models import BaseModel
from django.db import models
from venue.models import Venue


class Hall(BaseModel):
    venue = models.ForeignKey(to=Venue, on_delete=models.PROTECT, related_name="venus")
    name = models.CharField(blank=True, null=True)
    number = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["venue", "number"], name="unique_hall_venue"
            )
        ]

    def __str__(self) -> str:
        venue_name = self.venue.name if self.venue.name else "No Venue"
        return f"{venue_name} / {self.number}"
