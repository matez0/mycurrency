from django.urls import path

from currencies.views import get_exchange_rates

urlpatterns = [
    path("rates/", get_exchange_rates, name="exchange_rates"),
]
