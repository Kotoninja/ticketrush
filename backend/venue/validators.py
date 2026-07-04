from django.core.exceptions import ValidationError


def get_venue_exist(instance):
    from .models import Venue

    return Venue.objects.filter(name=instance.name).first()


def name_validation_for_a_exists_organization(venue_instance):
    """
    Each organization can have an infinite number of venues, but with different addresses.
    However, other organizations cannot name their venues the same way.
    """

    is_venue_exist = get_venue_exist(venue_instance)
    if is_venue_exist and is_venue_exist.created_by != venue_instance.created_by:
        raise ValidationError("This Name for the venue exists.")
