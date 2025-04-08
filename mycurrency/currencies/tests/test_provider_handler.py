from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from shutil import rmtree

from django.conf import settings
import pytest

from currencies.exchange_rate_provider import ProviderHandler
from currencies.models import CurrencyExchangeRate, Provider

pytestmark = pytest.mark.django_db


@contextmanager
def provider_plugin(priority: int = 1, exchange_rate: Decimal | None = Decimal("12.123456"), extra_code: str = ""):
    plugin_code = f"""
class Provider:
    def get_exchange_rate_data(self, from_currency, to_currency, date):
        {extra_code}
        return {exchange_rate}
"""
    plugin_name = f"mock_{priority}"
    plugin_path = settings.BASE_DIR / settings.PROVIDERS_PKG / plugin_name
    plugin = None
    try:
        plugin_path.mkdir(exist_ok=True)

        with open(plugin_path / "__init__.py", "w+") as plugin_file:
            plugin_file.write(plugin_code)

        plugin = Provider.objects.create(name=plugin_name, priority=priority)

        yield {"exchange_rate": exchange_rate}

    finally:
        plugin and plugin.delete()
        rmtree(plugin_path)


@pytest.fixture
def provider_handler_call(currency):
    from_currency = currency["EUR"]
    to_currency = currency["USD"]
    _date = date(2015, 10, 21)

    return lambda: ProviderHandler()(from_currency, to_currency, _date)


def test_calls_provider_plugin_method(currency):
    from_currency = currency["EUR"]
    to_currency = currency["USD"]
    _date = date(2015, 10, 21)

    with provider_plugin() as provider:
        result = ProviderHandler()(from_currency, to_currency, _date)

        assert isinstance(result, CurrencyExchangeRate)
        assert result.rate == provider["exchange_rate"]
        assert result.date == _date
        assert result.from_currency == from_currency
        assert result.to_currency == to_currency


def test_highest_priority_provider_shall_be_called(provider_handler_call):
    with (
        provider_plugin(priority=5, exchange_rate=123),
        provider_plugin(priority=1, exchange_rate=456) as provider,
    ):
        result = provider_handler_call()

        assert isinstance(result, CurrencyExchangeRate)
        assert result.rate == provider["exchange_rate"]


def test_next_provider_shall_be_called_in_priority_order_when_provider_returns_none(provider_handler_call):
    with (
        provider_plugin(priority=1, exchange_rate=None),
        provider_plugin(priority=2, exchange_rate=None),
        provider_plugin(priority=3) as provider,
    ):
        result = provider_handler_call()

        assert isinstance(result, CurrencyExchangeRate)
        assert result.rate == provider["exchange_rate"]


def test_returns_none_when_all_provider_returns_none(provider_handler_call):
    with (
        provider_plugin(priority=1, exchange_rate=None),
        provider_plugin(priority=2, exchange_rate=None),
    ):
        result = provider_handler_call()

        assert result is None


def test_next_provider_shall_be_called_in_priority_order_when_provider_raises_exception(provider_handler_call):
    with (
        provider_plugin(priority=1, extra_code="raise Exception"),
        provider_plugin(priority=2) as provider,
    ):
        result = provider_handler_call()

        assert isinstance(result, CurrencyExchangeRate)
        assert result.rate == provider["exchange_rate"]
