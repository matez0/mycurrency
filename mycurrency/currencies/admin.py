from django.contrib import admin

from currencies.models import Provider


class ProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "priority")


admin.site.register(Provider, ProviderAdmin)
