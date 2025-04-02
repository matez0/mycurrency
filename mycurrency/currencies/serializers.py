from collections.abc import Generator, Iterable

from rest_framework import serializers

from currencies.models import CurrencyExchangeRate


class CurrencyRatesRequestSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    from_currency = serializers.CharField(max_length=3)


class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    to_currency = serializers.SlugRelatedField(read_only=True, slug_field="code")

    class Meta:
        model = CurrencyExchangeRate
        fields = ("to_currency", "rate")


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
