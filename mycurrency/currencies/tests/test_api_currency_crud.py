from unittest.mock import ANY

import pytest
from rest_framework import status

from currencies.models import Currency

pytestmark = pytest.mark.django_db

URL = "/currencies/"


def test_create_currency(client):
    data = {"code": "HRK", "name": "Croatian Kuna"}

    response = client.post(URL, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == data | {"id": ANY}
    item = Currency.objects.get(pk=response.data["id"])
    assert response.data == {"code": item.code, "name": item.name, "id": item.id}


def test_list_currencies(client, currency):
    response = client.get(URL)

    assert response.status_code == status.HTTP_200_OK

    results = response.data["results"]
    assert len(results) == len(currency)

    for item in currency.values():
        assert {"code": item.code, "name": item.name, "id": item.id} in results


def test_retrieve_currency(client, currency):
    currency_to_retrieve = currency["EUR"]

    response = client.get(URL + f"{currency_to_retrieve.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": currency_to_retrieve.id,
        "code": currency_to_retrieve.code,
        "name": currency_to_retrieve.name,
    }


def test_update_currency(client, currency):
    currency_to_update = currency["EUR"]

    updated_data = {"code": "HUF", "name": "Hungarian Forint"}

    response = client.put(URL + f"{currency_to_update.id}/", updated_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    currency_to_update.refresh_from_db()
    assert currency_to_update.code == updated_data["code"]
    assert currency_to_update.name == updated_data["name"]


def test_partial_update_currency(client, currency):
    currency_code = "EUR"
    currency_to_update = currency[currency_code]

    partial_data = {"name": "European currency"}

    response = client.patch(URL + f"{currency_to_update.id}/", partial_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    currency_to_update.refresh_from_db()
    assert currency_to_update.code == currency_code
    assert currency_to_update.name == partial_data["name"]


def test_delete_currency(client, currency):
    currency_to_delete = currency["USD"]

    response = client.delete(URL + f"{currency_to_delete.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Currency.DoesNotExist):
        Currency.objects.get(pk=currency_to_delete.id)
