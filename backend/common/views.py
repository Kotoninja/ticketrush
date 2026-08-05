from django.shortcuts import render


def index(request):
    return render(request=request, template_name="common/index.html")

def bookings(request):
    return render(request=request, template_name="common/bookings.html")

def session_detail(request):
    return render(request=request, template_name="common/session.html")
