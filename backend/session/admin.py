from django.contrib import admin

from .models import EventSession, SeatSession

admin.site.register(EventSession)
admin.site.register(SeatSession)
