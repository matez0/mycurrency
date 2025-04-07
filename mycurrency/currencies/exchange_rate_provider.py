from collections.abc import Generator, Sequence
from datetime import date, timedelta

from django.db import transaction

from currencies.models import Currency, CurrencyExchangeRate

TIME_RESOLUTION = timedelta(days=1)


class ProviderHandler:
    """Fetches a currency exchange rate from the highest priority available provider."""

    def __call__(self, from_currency, to_currency, date) -> CurrencyExchangeRate | None:
        pass


class ExchangeRateLoader:
    """Yields currency exchange rates fetched from a provider and store them efficiently on-the-fly."""

    MAX_BULK_SIZE = 1000

    def __init__(self):
        self.exchange_rates = []
        self.provider_handler = ProviderHandler()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._bulk_create()

        return False

    def _bulk_create(self) -> None:
        CurrencyExchangeRate.objects.bulk_create(self.exchange_rates)
        self.exchange_rates.clear()

    def __call__(
        self, from_currency: Currency, from_date: date, to_date: date, to_currencies: Sequence[Currency]
    ) -> Generator[CurrencyExchangeRate, None, None]:
        to_currencies = sorted(to_currencies, key=lambda item: item.code)

        while from_date <= to_date:
            for to_currency in to_currencies:
                if exchange_rate := self.provider_handler(from_currency, to_currency, from_date):
                    self._append(exchange_rate)

                    yield exchange_rate

            from_date += TIME_RESOLUTION

    def _append(self, exchange_rate: CurrencyExchangeRate) -> None:
        self.exchange_rates.append(exchange_rate)

        if len(self.exchange_rates) >= self.MAX_BULK_SIZE:
            self._bulk_create()


@transaction.atomic
def provide_exchange_rates(
    from_currency: Currency, from_date: date, to_date: date
) -> Generator[CurrencyExchangeRate, None, None]:
    """Yields currency exchange rates in date order from the database completing the missing ones from a provider."""

    last_date = from_date - TIME_RESOLUTION
    all_to_currencies = set(Currency.objects.exclude(pk=from_currency.pk))
    to_currencies = set()

    with ExchangeRateLoader() as load_exchange_rates:
        for exchange_rate in CurrencyExchangeRate.objects.filter(
            date__range=(from_date, to_date),
            from_currency=from_currency,
        ).order_by("date"):
            if exchange_rate.date != last_date and last_date >= from_date:  # load missing currencies of last date
                if to_currencies != all_to_currencies:
                    yield from load_exchange_rates(
                        from_currency,
                        last_date,
                        last_date,
                        all_to_currencies - to_currencies,
                    )

                to_currencies = set()

            if exchange_rate.date - last_date > TIME_RESOLUTION:  # load the missing date gap
                yield from load_exchange_rates(
                    from_currency,
                    last_date + TIME_RESOLUTION,
                    exchange_rate.date - TIME_RESOLUTION,
                    all_to_currencies,
                )

            yield exchange_rate

            last_date = exchange_rate.date
            to_currencies.add(exchange_rate.to_currency)

        if to_currencies and to_currencies != all_to_currencies:  # load missing currencies of the last available date
            yield from load_exchange_rates(from_currency, last_date, last_date, all_to_currencies - to_currencies)

        if last_date < to_date:  # load the missing dates in the end
            yield from load_exchange_rates(from_currency, last_date + TIME_RESOLUTION, to_date, all_to_currencies)
