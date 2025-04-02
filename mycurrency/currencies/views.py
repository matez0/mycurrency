from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from currencies.models import Currency, CurrencyExchangeRate
from currencies.serializers import CurrencyRatesRequestSerializer, CurrencyRatesResponseSerializer


@api_view(["GET"])
def get_exchange_rates(request):
    serializer = CurrencyRatesRequestSerializer(data=request.query_params)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    from_date = serializer.validated_data["from_date"]
    to_date = serializer.validated_data["to_date"]
    from_currency_code = serializer.validated_data["from_currency"]

    try:
        from_currency = Currency.objects.get(code=from_currency_code)

    except Currency.DoesNotExist:
        return Response({"error": "Invalid currency."}, status=status.HTTP_400_BAD_REQUEST)

    exchange_rates_by_date = CurrencyExchangeRate.objects.filter(
        date__range=(from_date, to_date),
        from_currency=from_currency,
    ).order_by("date", "to_currency__code")

    return Response(
        CurrencyRatesResponseSerializer(
            CurrencyRatesResponseSerializer.generate_raw_data(from_currency.code, exchange_rates_by_date),
            many=True,
        ).data
    )
