from datetime import date
from unittest.mock import Mock, call, patch

import pytest

from currencies.exchange_rate_provider import ExchangeRateLoader
from currencies.models import CurrencyExchangeRate

MUT = "currencies.exchange_rate_provider"

pytestmark = pytest.mark.django_db


@pytest.fixture
def provider_handler(currency):
    with patch(MUT + ".ProviderHandler", spec_set=True) as provider_handler:

        def save(return_value):
            provider_handler.return_value.side_effect.return_values.append(return_value)
            return return_value

        provider_handler.return_value.side_effect = lambda from_currency, to_currency, date: save(
            CurrencyExchangeRate(from_currency=from_currency, to_currency=to_currency, date=date, rate="12.34")
        )
        provider_handler.return_value.side_effect.return_values = []

        yield provider_handler


def test_yields_exchange_rates_for_given_currencies_from_provider(provider_handler: Mock, currency):
    to_currencies = [currency["CHF"], currency["GBP"], currency["USD"]]

    with ExchangeRateLoader() as load_exchange_rates:
        exchange_rates = list(
            load_exchange_rates(currency["EUR"], date(2023, 10, 16), date(2023, 10, 17), to_currencies)
        )

        assert len(exchange_rates) == len(to_currencies) * 2  # number of to-currencies times number of days
        assert exchange_rates == provider_handler.return_value.side_effect.return_values

    assert provider_handler.return_value.call_args_list == [
        call(currency["EUR"], currency["CHF"], date(2023, 10, 16)),
        call(currency["EUR"], currency["GBP"], date(2023, 10, 16)),
        call(currency["EUR"], currency["USD"], date(2023, 10, 16)),
        call(currency["EUR"], currency["CHF"], date(2023, 10, 17)),
        call(currency["EUR"], currency["GBP"], date(2023, 10, 17)),
        call(currency["EUR"], currency["USD"], date(2023, 10, 17)),
    ]
    assert len(exchange_rates) == provider_handler.return_value.call_count


def test_yields_nothing_when_no_exchange_rate_is_provided(provider_handler: Mock, currency):
    provider_handler.return_value.side_effect = provider_handler.return_value.return_value = None
    to_currencies = [currency["CHF"], currency["GBP"], currency["USD"]]

    with ExchangeRateLoader() as load_exchange_rates:
        exchange_rates = list(
            load_exchange_rates(currency["EUR"], date(2023, 10, 16), date(2023, 10, 17), to_currencies)
        )

        # number of to-currencies times number of days
        assert provider_handler.return_value.call_count == len(to_currencies) * 2
        assert not exchange_rates


def test_exchange_rates_shall_not_be_saved_under_bulk_limit_until_exit(provider_handler: Mock, currency):
    to_currencies = [currency["CHF"], currency["GBP"], currency["USD"]]

    assert ExchangeRateLoader.MAX_BULK_SIZE > len(to_currencies) * 2  # number of to-currencies times number of days

    with ExchangeRateLoader() as load_exchange_rates:
        exchange_rates = list(
            load_exchange_rates(currency["EUR"], date(2023, 10, 16), date(2023, 10, 17), to_currencies)
        )

        assert CurrencyExchangeRate.objects.count() == 0

    assert exchange_rates
    assert CurrencyExchangeRate.objects.count() == len(exchange_rates)


def test_exchange_rates_shall_be_saved_when_bulk_limit_reached(provider_handler: Mock, currency):
    to_currencies = [currency["CHF"], currency["GBP"], currency["USD"]]
    bulk_limit = 4

    assert bulk_limit < len(to_currencies) * 2  # number of to-currencies times number of days

    with patch(MUT + ".ExchangeRateLoader.MAX_BULK_SIZE", new=bulk_limit), ExchangeRateLoader() as load_exchange_rates:
        exchange_rates = list(
            load_exchange_rates(currency["EUR"], date(2023, 10, 16), date(2023, 10, 17), to_currencies)
        )

        assert CurrencyExchangeRate.objects.count() == ExchangeRateLoader.MAX_BULK_SIZE

    assert exchange_rates
    assert CurrencyExchangeRate.objects.count() == len(exchange_rates)
