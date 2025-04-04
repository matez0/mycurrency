from datetime import date

import pytest
from rest_framework import status

from currencies.models import CurrencyExchangeRate

pytestmark = pytest.mark.django_db

URL = "/currencies/convert/"


@pytest.fixture
def exchange_rates(currency):
    for _date, from_currency, to_currency, rate in [
        (date(2023, 10, 15), "EUR", "USD", 0.93),
        (date(2023, 10, 15), "USD", "EUR", 1.08),
        (date(2023, 10, 30), "EUR", "USD", 0.909091),
        (date(2023, 10, 30), "USD", "EUR", 1.10),
    ]:
        CurrencyExchangeRate.objects.create(
            date=_date,
            from_currency=currency[from_currency],
            to_currency=currency[to_currency],
            rate=rate,
        )


def test_success(client, exchange_rates):
    parameters = {"from_currency": "EUR", "to_currency": "USD", "amount": 1000.00}

    response = client.get(URL, parameters)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"from_currency": "EUR", "to_currency": "USD", "amount": "909.09", "rate": "0.909091"}


@pytest.mark.parametrize("missing_parameter", ["from_currency", "to_currency", "amount"])
def test_missing_parameters(client, missing_parameter):
    parameters = {"from_currency": "USD", "to_currency": "EUR", "amount": 100.00}
    del parameters[missing_parameter]

    response = client.get(URL, parameters)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert missing_parameter in response.data


@pytest.mark.parametrize("invalid_amount", ["abc", -50])
def test_invalid_amount(client, exchange_rates, invalid_amount):
    parameters = {"from_currency": "USD", "to_currency": "EUR", "amount": invalid_amount}

    response = client.get(URL, parameters)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "amount" in response.data


@pytest.mark.parametrize("currency_field", ["from_currency", "to_currency"])
def test_unsupported_currency(client, currency_field):
    unsupported_currency = "HUF"
    parameters = {"from_currency": "EUR", "to_currency": "USD", "amount": 100.00} | {
        currency_field: unsupported_currency
    }

    response = client.get(URL, parameters)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
