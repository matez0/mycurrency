[![Python versions](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# Web platform for calculating currency exchange rates

The platform uses currency exchange rates from pluggable external services,
storing them in its database for provision.

Data provider external services are prioritized, and the data from the available service
with the highest priority is selected for use.

The supported currencies can be managed in the admin panel.

## API endpoints

- Retrieve currency exchange rates from a specific currency to all available currencies for a given time period.
- Convert an amount from one currency to another.
- CRUD operations (list, create, retrieve, update, partial_update, destroy) for currencies.

## Data provider plugins

Plugins of external services can be activated or deactivated in the admin panel.

- [CurrencyBeacon](https://currencybeacon.com/api-documentation) [[source]](mycurrency/providers/CurrencyBeacon/__init__.py):

Using the plugin requires the `CURRENCY_BEACON_API_KEY` environment variable, e.g.:
```
CURRENCY_BEACON_API_KEY=xxxxxxxxxxxxxxxx pytest currencies/tests/test_integration_currency_beacon.py
```

## Online currency converter

The site enables the conversion of a given amount between the given currencies using the last available exchange rate.

It is also accessible from the admin panel.

## Django management command - loading historical data

The command loads all currency exchange rates for a given date, e.g.:
```
CURRENCY_BEACON_API_KEY=xxxxxxxxxxxxxxxx python manage.py load_historical_data 2015-10-21
```
It can be launched from a `cron` job.

## Testing

Create the virtual environment:
```
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip setuptools
pip install poetry
poetry install
```
Run the tests:
```
pytest mycurrency
```

### Running the service

For the first time or when the database models are changed, do the migrations:
```
python manage.py migrate
```
Run the service:
```
python manage.py runserver
```

To log in to the admin panel, ensure you have a superuser account created:
```
python manage.py createsuperuser
```

## Development

Before committing, please check the code style and import layout:
```
ruff check --fix
ruff format
```
For the first time or when the database models are changed, make the migration:
```
python manage.py makemigrations currencies
```
and commit the result.

## Todo:

- Defect: Handle decimal errors during conversion. Large amounts can lead to `decimal.InvalidOperation`.

- Defect: If exchange rate time series requests include today's date,
existing database entries for today are not updated.

- Use async DRF views and async queries and async HTTP requests in provider plugins.

- Configure the service with environment variables.

- Querying a date range of currency exchange rates may affect many database items.
Check how to optimize the Django query for that (prefech rate).

- Validation of the return value of the provider plugins.
Do not repeat the decimal conversion definition (serializer, model, instantiation).

- Make the provider plugin run more isolated while keeping the efficiency.

- If the provider plugins are developed by other teams, a sanity check would be useful.

- Refine database constraints like uniqueness (fields of `CurrencyExchangeRate`)
and valid data (upper case currency code, provider module name, ...).

- Containerization: python packaging and environment configuration.

- Setup `mypy` and fix type hint issues.
