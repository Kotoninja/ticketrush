from django.db.models import Q
from django.utils import timezone


def availiable():
    return Q(draft_expire_time__lt=timezone.now())
