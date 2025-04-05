import pytest
from rest_framework.test import APIClient

from currencies.models import Currency


# Override the client fixture of django-pytest with the one of DRF:
@pytest.fixture
def client():
    return APIClient()


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
