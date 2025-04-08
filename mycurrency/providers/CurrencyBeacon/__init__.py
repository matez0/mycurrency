import os

import requests

URL = "https://api.currencybeacon.com/v1/historical"
API_KEY = os.environ["CURRENCY_BEACON_API_KEY"]


class Provider:
    """Fetches currrency exchange rate data from CurrencyBeacon."""

    def get_exchange_rate_data(self, from_currency: str, to_currency: str, date):
        params = {"api_key": API_KEY, "date": date, "base": from_currency, "symbols": to_currency}

        response = requests.get(URL, params=params)

        response.raise_for_status()

        rates = response.json()["rates"] or {}

        return rates.get(to_currency)
