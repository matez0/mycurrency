"""
For running the tests, set the environment variable of API key:
```
CURRENCY_BEACON_API_KEY=xxxxxxxxxxxxxxxx pytest tests.py
```
"""

from datetime import date

from . import Provider


def test_returns_exchange_rate_value():
    assert Provider().get_exchange_rate_data("EUR", "USD", date(2015, 10, 21)) == 1.13432275


def test_no_data_available():
    assert Provider().get_exchange_rate_data("EUR", "USD", date(1955, 11, 12)) is None
