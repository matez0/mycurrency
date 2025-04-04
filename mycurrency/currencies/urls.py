from django.urls import path

from currencies.views import convert_amount, get_exchange_rates

urlpatterns = [
    path("rates/", get_exchange_rates, name="exchange_rates"),
    path("convert/", convert_amount, name="convert_amount"),
]
