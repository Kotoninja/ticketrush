from common.models import BaseModel
from django.db import models
from organization.models import Organization


class Venue(BaseModel):
    created_by = models.ForeignKey(to=Organization, on_delete=models.PROTECT, null=True)
    description = models.CharField(max_length=400)
    name = models.CharField(max_length=50)
    adress = models.CharField(max_length=100)
    site_link = models.URLField()

    def __str__(self) -> str:
        org_name = self.created_by.name if self.created_by else "No Organization"
        return f"{self.name} / {org_name}"

    @property
    def feedbacks(self) -> float: ...
    @property
    def rating(self) -> int: ...
    