from datetime import date, datetime
import logging
import multiprocessing as mp
import os

import django
from django.core.management.base import BaseCommand

# Make models importable in each subprocess
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mycurrency.settings")
django.setup()

from currencies.exchange_rate_provider import ProviderHandler  # noqa: E402
from currencies.models import Currency, CurrencyExchangeRate  # noqa: E402

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = "Load historical data of currency exchange rates."

    @staticmethod
    def date_arg(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    def add_arguments(self, parser):
        parser.add_argument("date", type=self.date_arg, help="Date in YYYY-MM-DD format")

    def handle(self, *args, **options):
        query_date = options["date"]

        with (
            BulkCreator(CurrencyExchangeRate) as create_exchange_rate,
            mp.Pool(processes=mp.cpu_count(), initializer=init_process, initargs=(query_date,)) as pool,
        ):
            for result in pool.imap_unordered(load_currency_exchange_rate, currency_pairs(), chunksize=1):
                if result:
                    self.stdout.write(f"1 {result.from_currency.code} -> {result.rate} {result.to_currency.code}")
                    create_exchange_rate(result)

        self.stdout.write(
            f"Loaded currency exchange rates: {CurrencyExchangeRate.objects.filter(date=query_date).count()}"
        )


def init_process(query_date: date):
    mp.current_process().provider_handler = ProviderHandler()
    mp.current_process().query_date = query_date


def load_currency_exchange_rate(currency_pair):
    from_currency, to_currency = currency_pair

    return mp.current_process().provider_handler(*currency_pair, mp.current_process().query_date)


class BulkCreator:
    MAX_BULK_SIZE = 1000

    def __init__(self, model):
        self.model = model
        self.items = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._bulk_create()

        return False

    def _bulk_create(self) -> None:
        self.model.objects.bulk_create(self.items, ignore_conflicts=True)
        self.items.clear()

    def __call__(self, item) -> None:
        self.items.append(item)

        if len(self.items) >= self.MAX_BULK_SIZE:
            self._bulk_create()


def currency_pairs():
    currencies = list(Currency.objects.all())

    for one in currencies:
        for other in currencies:
            if one.code != other.code:
                yield (one, other)
