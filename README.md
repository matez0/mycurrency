[![Python versions](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# Web platform for calculating currency exchange rates

## API endpoints

- Retrieve currency exchange rates from a specific currency to all available currencies for a given time period.
- Convert an amount from one currency to another.
- CRUD operations (list, create, retrieve, update, partial_update, destroy) for currencies.

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
