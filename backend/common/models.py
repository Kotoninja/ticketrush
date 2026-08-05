from typing import Final

from django.db import models


class BaseModel(models.Model):
    created_at: Final = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at: Final = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
