from collections.abc import Sequence
from datetime import date
from unittest.mock import Mock, patch

import pytest

from currencies.exchange_rate_provider import provide_exchange_rates
from currencies.models import Currency, CurrencyExchangeRate

MUT = "currencies.exchange_rate_provider"

pytestmark = pytest.mark.django_db


@pytest.fixture
def exchange_rate_loader():
    """Mocks ExchangeRateLoader with yielding the parameters of the call."""

    with patch(MUT + ".ExchangeRateLoader", spec_set=True) as exchange_rate_loader:
        exchange_rate_loader.return_value.__enter__.return_value.side_effect = lambda *args: [args]

        yield exchange_rate_loader


def create_exchange_rates(
    _date: date, from_currency: Currency, to_currencies: Sequence[Currency]
) -> list[CurrencyExchangeRate]:
    return [
        CurrencyExchangeRate.objects.create(
            date=_date,
            from_currency=from_currency,
            to_currency=to_currency,
            rate=12.34,
        )
        for to_currency in to_currencies
    ]


def test_returns_continuous_date_range_from_db(exchange_rate_loader: Mock, currency):
    from_currency = currency["EUR"]
    to_all_currencies = set(currency.values()) - {from_currency}

    db_exchange_rates_1 = create_exchange_rates(date(2023, 10, 15), from_currency, to_all_currencies)
    db_exchange_rates_2 = create_exchange_rates(date(2023, 10, 16), from_currency, to_all_currencies)

    assert list(provide_exchange_rates(from_currency, date(2023, 10, 15), date(2023, 10, 16))) == (
        db_exchange_rates_1 + db_exchange_rates_2
    )


def test_fills_the_gap_in_date_range(exchange_rate_loader: Mock, currency):
    from_currency = currency["EUR"]
    to_all_currencies = set(currency.values()) - {from_currency}

    db_exchange_rates_1 = create_exchange_rates(date(2023, 10, 15), from_currency, to_all_currencies)
    db_exchange_rates_2 = create_exchange_rates(date(2023, 10, 18), from_currency, to_all_currencies)

    assert list(provide_exchange_rates(from_currency, date(2023, 10, 15), date(2023, 10, 18))) == (
        db_exchange_rates_1
        + [(from_currency, date(2023, 10, 16), date(2023, 10, 17), to_all_currencies)]
        + db_exchange_rates_2
    )


def test_completes_the_beginning_of_date_range(exchange_rate_loader: Mock, currency):
    from_currency = currency["EUR"]
    to_all_currencies = set(currency.values()) - {from_currency}

    db_exchange_rates_1 = create_exchange_rates(date(2023, 10, 15), from_currency, to_all_currencies)
    db_exchange_rates_2 = create_exchange_rates(date(2023, 10, 16), from_currency, to_all_currencies)

    assert list(provide_exchange_rates(from_currency, date(2023, 10, 12), date(2023, 10, 16))) == (
        [(from_currency, date(2023, 10, 12), date(2023, 10, 14), to_all_currencies)]
        + db_exchange_rates_1
        + db_exchange_rates_2
    )


def test_completes_the_end_of_date_range(exchange_rate_loader: Mock, currency):
    from_currency = currency["EUR"]
    to_all_currencies = set(currency.values()) - {from_currency}

    db_exchange_rates_1 = create_exchange_rates(date(2023, 10, 15), from_currency, to_all_currencies)
    db_exchange_rates_2 = create_exchange_rates(date(2023, 10, 16), from_currency, to_all_currencies)

    assert list(provide_exchange_rates(from_currency, date(2023, 10, 15), date(2023, 10, 18))) == (
        db_exchange_rates_1
        + db_exchange_rates_2
        + [(from_currency, date(2023, 10, 17), date(2023, 10, 18), to_all_currencies)]
    )


def test_completes_the_missing_currencies(exchange_rate_loader: Mock, currency):
    from_currency = currency["EUR"]
    to_all_currencies = set(currency.values()) - {from_currency}
    missing_1 = {currency["USD"]}
    missing_2 = {currency["CHF"], currency["GBP"]}

    db_exchange_rates_1 = create_exchange_rates(date(2023, 10, 15), from_currency, to_all_currencies - missing_1)
    db_exchange_rates_2 = create_exchange_rates(date(2023, 10, 16), from_currency, to_all_currencies - missing_2)

    assert list(provide_exchange_rates(from_currency, date(2023, 10, 15), date(2023, 10, 16))) == (
        db_exchange_rates_1
        + [(from_currency, date(2023, 10, 15), date(2023, 10, 15), missing_1)]
        + db_exchange_rates_2
        + [(from_currency, date(2023, 10, 16), date(2023, 10, 16), missing_2)]
    )
