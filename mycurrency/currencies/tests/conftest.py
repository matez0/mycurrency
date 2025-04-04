import pytest

from currencies.models import Currency


@pytest.fixture(autouse=True)
def currency():
    return {
        code: Currency.objects.create(code=code, name=name)
        for code, name in [
            ("EUR", "Euro"),
            ("USD", "United States Dollar"),
            ("CHF", "Swiss Franc"),
            ("GBP", "British Pound"),
        ]
    }
