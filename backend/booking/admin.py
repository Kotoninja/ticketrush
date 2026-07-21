from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.forms.models import ModelForm
from django.http import HttpRequest

from .models import Booking
from .services import BookingService
from django.db import transaction


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    def save_model(
        self, request: HttpRequest, obj: Any, form: ModelForm, change: bool
    ) -> None:
        if change:
            super().save_model(request, obj, form, change)
        else:
            booking = BookingService.create(
                user=form.cleaned_data["user"],
                seat_session=form.cleaned_data["seat_session"],
            )

            obj.pk = booking.pk

    @transaction.atomic
    def delete_queryset(self, request: HttpRequest, queryset: QuerySet) -> None:
        for queryset_pk in queryset.values_list("pk", flat=True):
            print(queryset_pk)
            BookingService.delete(pk=queryset_pk)

        queryset.delete()
