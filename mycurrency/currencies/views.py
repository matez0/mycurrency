from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from currencies.currency_converter import (
    CurrencyConverterError,
    CurrencyExchangeRateNotAvailableError,
    convert_with_latest_exchange_rate,
)
from currencies.exchange_rate_provider import provide_exchange_rates
from currencies.forms import ConvertAmountForm
from currencies.models import Currency
from currencies.serializers import (
    CurrencyConvertRequestSerializer,
    CurrencyConvertResponseSerializer,
    CurrencyRatesRequestSerializer,
    CurrencyRatesResponseSerializer,
    CurrencySerializer,
)


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

    exchange_rates_by_date = provide_exchange_rates(from_currency, from_date, to_date)

    return Response(
        CurrencyRatesResponseSerializer(
            CurrencyRatesResponseSerializer.generate_raw_data(from_currency.code, exchange_rates_by_date),
            many=True,
        ).data
    )


@api_view(["GET"])
def convert_amount(request):
    serializer = CurrencyConvertRequestSerializer(data=request.query_params)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    from_currency_code = serializer.validated_data["from_currency"]
    to_currency_code = serializer.validated_data["to_currency"]

    try:
        converted_amount, exchange_rate = convert_with_latest_exchange_rate(
            serializer.validated_data["amount"],
            from_currency_code,
            to_currency_code,
        )

    except CurrencyExchangeRateNotAvailableError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    except CurrencyConverterError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    result = CurrencyConvertResponseSerializer(
        data={
            "from_currency": from_currency_code,
            "to_currency": to_currency_code,
            "rate": exchange_rate,
            "amount": converted_amount,
        }
    )

    if not result.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(result.data)


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all().order_by("code")
    serializer_class = CurrencySerializer


def backoffice_converter_view(request):
    context = {
        "form": None,
        "converted_amount": None,
        "error_message": None,
        "exchange_rate": None,
    }

    if request.method == "POST":
        form = context["form"] = ConvertAmountForm(request.POST)

        if form.is_valid():
            try:
                context["converted_amount"], context["exchange_rate"] = convert_with_latest_exchange_rate(
                    form.cleaned_data["amount"],
                    form.cleaned_data["from_currency"],
                    form.cleaned_data["to_currency"],
                )

            except CurrencyConverterError as exc:
                context["error_message"] = str(exc)

    else:
        context["form"] = ConvertAmountForm()

    return render(request, "backoffice_converter_page.html", context)
