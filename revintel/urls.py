"""
URL configuration for revintel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    # Home: frontend Django (dashboard)
    path("", include("dashboard.urls")),

    path("admin/", admin.site.urls),

    # Rutas adicionales de frontend Django clásico (si las amplías)
    path("reports/", include("reports.urls")),

    # API principal de ventas / analítica
    path("api/sales/", include("analytics.api_urls")),  # endpoints para Chart.js y Reflex

    # Esquema OpenAPI + documentación interactiva para *toda* la API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="api-docs",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="api-redoc",
    ),
]
