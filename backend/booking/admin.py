from typing import Any

from django.contrib import admin
from django.forms.models import ModelForm
from django.http import HttpRequest

from .models import Booking
from .services import BookingService


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
