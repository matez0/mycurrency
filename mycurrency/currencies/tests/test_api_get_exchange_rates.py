from datetime import date

import pytest
from rest_framework import status

from currencies.models import CurrencyExchangeRate

pytestmark = pytest.mark.django_db

URL = "/currencies/rates/"


@pytest.fixture
def exchange_rates(currency):
    for _date, from_currency, to_currency, rate in [
        (date(2023, 10, 25), "EUR", "CHF", 0.94),
        (date(2023, 10, 25), "CHF", "EUR", 1.06),
        (date(2023, 10, 26), "EUR", "USD", 0.95),
        (date(2023, 10, 27), "EUR", "USD", 0.96),
        (date(2023, 10, 26), "EUR", "GBP", 0.87),
        (date(2023, 10, 27), "EUR", "GBP", 0.88),
        (date(2023, 10, 26), "GBP", "EUR", 1.15),
        (date(2023, 10, 27), "GBP", "EUR", 1.14),
        (date(2023, 10, 30), "EUR", "USD", 0.91),
        (date(2023, 10, 30), "USD", "EUR", 1.10),
    ]:
        CurrencyExchangeRate.objects.create(
            date=_date,
            from_currency=currency[from_currency],
            to_currency=currency[to_currency],
            rate=rate,
        )


def test_success(client, exchange_rates):
    parameters = {"from_date": "2023-10-26", "to_date": "2023-10-27", "from_currency": "EUR"}

    response = client.get(URL, parameters)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data == [
        {
            "date": "2023-10-26",
            "from_currency": "EUR",
            "rates": [{"to_currency": "GBP", "rate": "0.870000"}, {"to_currency": "USD", "rate": "0.950000"}],
        },
        {
            "date": "2023-10-27",
            "from_currency": "EUR",
            "rates": [{"to_currency": "GBP", "rate": "0.880000"}, {"to_currency": "USD", "rate": "0.960000"}],
        },
    ]


def test_no_data_in_requested_interval(client):
    parameters = {"from_date": "2023-10-28", "to_date": "2023-10-29", "from_currency": "EUR"}

    response = client.get(URL, parameters)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


def test_invalid_currency(client, exchange_rates):
    parameters = {"from_date": "2023-10-26", "to_date": "2023-10-27", "from_currency": "HUF"}

    response = client.get(URL, parameters)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


def test_invalid_date_format(client):
    parameters = {"from_date": "26-10-2023", "to_date": "2023/10/27", "from_currency": "EUR"}

    response = client.get(URL, parameters)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "from_date" in response.data
    assert "to_date" in response.data
