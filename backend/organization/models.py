import secrets
from common.models import BaseModel
from django.db import models
from user.models import CustomUser


def generate_reference_id() -> str:
    return secrets.token_hex()[:8]


class Organization(BaseModel):
    created_by = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    reference_id = models.CharField(
        default=generate_reference_id(),
        editable=False,
        unique=True,
        null=True,
        max_length=8,
    )

    def __str__(self) -> str:
        return f"{self.name} / ref_id:{str(self.reference_id)[:8]}"
