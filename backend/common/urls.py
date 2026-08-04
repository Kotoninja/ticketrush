from django.urls import path

from . import views

app_name = "ui"

urlpatterns = [
    path("", views.index, name="index"),
    path("bookings/", views.bookings, name="bookings"),
    path("session/", views.session_detail, name="session"),
]
