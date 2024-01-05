# Flask-SQLAlchemy Rollback per Test Example

This repository shows a minimal working example of a Flask-SQLAlchemy application with pytest setup.
Most notably, tests are isolated using database transactions that can be rolled back after each test ends.
This allows each test to start with a clean test database.
The example here works with PostgreSQL, but the pattern should be applicable to all databases SQLAlchemy 2.x supports.

# Setup

```
python -m venv .venv
source .venv/bin/activate
pipenv install --dev --ignore-pipfile
initdb fsa_rollback_per_test
pytest
```
