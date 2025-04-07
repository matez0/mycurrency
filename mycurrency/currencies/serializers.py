from collections.abc import Generator, Iterable

from django.conf import settings
from rest_framework import serializers

from currencies.models import Currency, CurrencyExchangeRate


class CurrencyRatesRequestSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    from_currency = serializers.CharField(max_length=3)


class OrderByToCurrencyCodeSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        return super().to_representation(sorted(data, key=lambda item: item.to_currency.code))


class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    to_currency = serializers.SlugRelatedField(read_only=True, slug_field="code")

    class Meta:
        model = CurrencyExchangeRate
        fields = ("to_currency", "rate")
        list_serializer_class = OrderByToCurrencyCodeSerializer


class CurrencyRatesResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    from_currency = serializers.CharField(max_length=3)
    rates = CurrencyExchangeRateSerializer(many=True)

    @staticmethod
    def generate_raw_data(
        from_currency: str,
        exchange_rates_by_date: Iterable[CurrencyExchangeRate],
    ) -> Generator[dict, None, None]:
        """Groups the exchange rates of the same date from a date ordered sequence."""

        last_date = None
        exchange_rates = []

        for exchange_rate in exchange_rates_by_date:
            if last_date != exchange_rate.date and exchange_rates:
                yield {"date": last_date, "from_currency": from_currency, "rates": exchange_rates}

                exchange_rates = []

            exchange_rates.append(exchange_rate)
            last_date = exchange_rate.date

        if exchange_rates:
            yield {"date": last_date, "from_currency": from_currency, "rates": exchange_rates}


class CurrencyConvertRequestSerializer(serializers.Serializer):
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(decimal_places=settings.CURRENCY_AMOUNT_PRECISION, max_digits=18, min_value=0)


class CurrencyConvertResponseSerializer(CurrencyConvertRequestSerializer):
    rate = serializers.DecimalField(decimal_places=settings.CURRENCY_EXCHANGE_RATE_PRECISION, max_digits=18)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"
