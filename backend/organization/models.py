import secrets
from common.models import BaseModel
from django.db import models
from user.models import CustomUser


def generate_reference_id() -> str:
    return secrets.token_hex()[:8]


class Organization(BaseModel):
    created_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="organizations",
    )
    name = models.CharField(max_length=255, unique=True)
    reference_id = models.CharField(
        editable=False,
        unique=True,
        max_length=8,
    )

    def save(self, *args, **kwargs):
        if not self.reference_id:
            self.reference_id = generate_reference_id()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} / ref_id:{str(self.reference_id)}"
