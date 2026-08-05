from common.models import BaseModel
from django.db import models
from hall.models import Hall


class Seat(BaseModel):
    CATEGORY_LISTS: list[tuple[str, str]] = [
        ("standart", "Standart"),
        ("comfort", "Comfort"),
        ("vip", "Vip"),
    ]
    hall = models.ForeignKey(to=Hall, on_delete=models.PROTECT)
    category = models.CharField(default="Standart", choices=CATEGORY_LISTS)
    number = models.PositiveSmallIntegerField(null=True)
    coordinates = models.JSONField(blank=True, null=True)

    # add UniqueConstraint

    def __str__(self) -> str:
        hall_name = self.hall.number if self.hall else "No Hall"
        return f"Hall - {hall_name} / {self.category} / num - {self.number} / {self.coordinates}"
