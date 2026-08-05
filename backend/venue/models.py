from common.models import BaseModel
from django.db import models
from organization.models import Organization
from django.db import transaction

from .validators import name_validation_for_a_exists_organization


class Venue(BaseModel):
    created_by = models.ForeignKey(
        to=Organization,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="venues",
    )
    description = models.CharField(max_length=400)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    site_link = models.URLField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "address"], name="unique_venue_name_per_address"
            ),
        ]

    def clean(self):
        name_validation_for_a_exists_organization(self)
        super().clean()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.full_clean()
            super().save(*args, **kwargs)

    def __str__(self) -> str:
        org_name = self.created_by.name if self.created_by else "No Organization"
        return f"{self.name} / {org_name}"

    @property
    def feedbacks(self) -> float: ...
    @property
    def rating(self) -> int: ...
