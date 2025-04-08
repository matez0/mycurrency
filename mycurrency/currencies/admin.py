from django.contrib import admin

from currencies.models import Currency, Provider


class ProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "priority")


admin.site.register(Provider, ProviderAdmin)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


admin.site.register(Currency, CurrencyAdmin)
