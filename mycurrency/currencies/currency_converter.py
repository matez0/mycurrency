from decimal import Decimal

from django.conf import settings

from currencies.exchange_rate_provider import provide_latest_exchange_rate
from currencies.models import Currency


class CurrencyConverterError(Exception):
    pass


class CurrencyExchangeRateNotAvailableError(CurrencyConverterError):
    pass


def convert_with_latest_exchange_rate(
    amount: Decimal,
    from_currency_code: str,
    to_currency_code: str,
) -> tuple[Decimal, Decimal]:
    """Returns the converted amount and the exchange rate used for the conversion."""

    try:
        from_currency = Currency.objects.get(code=from_currency_code)
        to_currency = Currency.objects.get(code=to_currency_code)

    except Currency.DoesNotExist:
        raise CurrencyConverterError("Invalid currency.")

    else:
        if exchange_rate := provide_latest_exchange_rate(from_currency, to_currency):
            return _convert(amount, exchange_rate.rate), exchange_rate.rate

        else:
            raise CurrencyExchangeRateNotAvailableError("Exchange rate is not available.")


def _convert(amount: Decimal, rate: Decimal) -> Decimal:
    return round(amount * rate, settings.CURRENCY_AMOUNT_PRECISION)
