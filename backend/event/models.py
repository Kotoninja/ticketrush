from datetime import timedelta

from common.models import BaseModel
from django.core.validators import MaxValueValidator
from django.db import models


class Event(BaseModel):
    AGE_AVAILABLE_LIST: list[tuple[str, str]] = [
        ("0", "0+"),
        ("6", "6+"),
        ("12", "12+"),
        ("16", "16+"),
        ("18", "18+"),
    ]
    CATEGORY_LIST: list[tuple[str, str]] = [
        ("theater", "Theater"),
        ("cinema", "Cinema"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=100)
    small_description = models.CharField(blank=True, null=True)
    description = models.CharField(blank=True, null=True)
    duration = models.DurationField(validators=[MaxValueValidator(timedelta(days=1))])
    age_available = models.CharField(choices=AGE_AVAILABLE_LIST)
    category = models.CharField(choices=CATEGORY_LIST)

    def __str__(self) -> str:
        return self.name
