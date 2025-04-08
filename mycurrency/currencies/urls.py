from django.urls import include, path
from rest_framework.routers import DefaultRouter

from currencies.views import CurrencyViewSet, backoffice_converter_view, convert_amount, get_exchange_rates

router = DefaultRouter()
router.register("", CurrencyViewSet)

urlpatterns = [
    path("rates/", get_exchange_rates, name="exchange_rates"),
    path("convert/", convert_amount, name="convert_amount"),
    path("", include(router.urls)),
    path("backoffice/converter/", backoffice_converter_view, name="backoffice_converter"),
]
