from django.db.models import Q
from django.utils import timezone


def available():
    """Check if the draft's expiration time is less than the current time."""
    return Q(draft_expire_time__lt=timezone.now())
