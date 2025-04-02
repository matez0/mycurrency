from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)


class CurrencyExchangeRate(models.Model):
    from_currency = models.ForeignKey(Currency, related_name="exchanges", on_delete=models.CASCADE)
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    rate = models.DecimalField(db_index=True, decimal_places=6, max_digits=18)
