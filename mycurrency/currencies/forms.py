from django import forms


class ConvertAmountForm(forms.Form):
    from_currency = forms.CharField(label="From currency", max_length=3)
    to_currency = forms.CharField(label="To currency", max_length=3)
    amount = forms.DecimalField(label="Amount", min_value=0)
