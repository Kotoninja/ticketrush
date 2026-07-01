import uuid

from common.models import BaseModel
from django.db import models
from user.models import CustomUser


class Organization(BaseModel):
    created_by = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    reference_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, null=True
    )

    def __str__(self) -> str:
        return f"{self.name} / ref_id:{str(self.reference_id)[:10]}"
