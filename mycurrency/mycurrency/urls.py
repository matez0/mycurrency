"""
URL configuration for mycurrency project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("currencies/", include("currencies.urls")),
]
