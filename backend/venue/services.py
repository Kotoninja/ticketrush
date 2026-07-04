from django.db import transaction
from .models import Venue


class VenueServices:
    """ """

    def __init__(self) -> None:
        return None

    def _name_validation_for_a_specific_organization(
        self, name: str, created_by_id: int
    ): ...

    @transaction.atomic
    def create_venue(self, data):
        self._name_validation_for_a_specific_organization(
            data.get("name", ""), data.get("created_by_id", "")
        )
