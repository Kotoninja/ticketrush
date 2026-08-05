"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Django
    path("admin/", admin.site.urls),
    # Rest_framework
    path("api-auth/", include("rest_framework.urls")),
    # Third-party app
    path(
        "api/schema/", SpectacularAPIView.as_view(), name="schema"
    ),  # Drf-spectacular YOUR PATTERNS
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),  # Drf-spectacular Optional UI
    path("silk/", include("silk.urls", namespace="silk")),  # Django-silk
    # My app
    path("api/venue/", include("venue.urls")),
    path("api/session/", include("session.urls")),
    path("api/booking/", include("booking.urls")),
    path("api/payment/", include("payment.urls")),
    path("", include("common.urls")),
]


# Django Debug Toolbar
if not settings.TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()
