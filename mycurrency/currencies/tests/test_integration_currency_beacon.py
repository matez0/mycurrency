from datetime import date
from unittest.mock import patch

import pytest
from rest_framework import status

from currencies.models import Provider

pytestmark = pytest.mark.django_db


@pytest.fixture
def currency_beacon_plugin():
    plugin = Provider.objects.create(name="CurrencyBeacon", priority=1)

    yield

    plugin.delete()


def test_get_exchange_rates(client, currency_beacon_plugin):
    parameters = {"from_date": "2023-10-26", "to_date": "2023-10-27", "from_currency": "EUR"}

    response = client.get("/currencies/rates/", parameters)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data == [
        {
            "date": "2023-10-26",
            "from_currency": "EUR",
            "rates": [
                {"to_currency": "CHF", "rate": "0.949223"},
                {"to_currency": "GBP", "rate": "0.870725"},
                {"to_currency": "USD", "rate": "1.056321"},
            ],
        },
        {
            "date": "2023-10-27",
            "from_currency": "EUR",
            "rates": [
                {"to_currency": "CHF", "rate": "0.952976"},
                {"to_currency": "GBP", "rate": "0.871729"},
                {"to_currency": "USD", "rate": "1.056547"},
            ],
        },
    ]


def test_convert_amount(client, currency_beacon_plugin):
    parameters = {"from_currency": "EUR", "to_currency": "USD", "amount": 1000.00}

    with patch("currencies.exchange_rate_provider.date") as _date:
        _date.today.return_value = date(2015, 10, 21)

        response = client.get("/currencies/convert/", parameters)

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.data == {"from_currency": "EUR", "to_currency": "USD", "amount": "1134.32", "rate": "1.134323"}
