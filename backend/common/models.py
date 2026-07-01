from django.db import models
from django.utils import timezone
from typing import Final


class BaseModel(models.Model):
    created_at: Final = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at: Final = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
