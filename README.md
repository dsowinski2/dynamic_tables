
# Dynamic Tables

## Prerequisite
- Docker

## Setting up project:

```bash
git clone https://github.com/dsowinski2/dynamic_tables
cd dynamic_tables
cp .env.example .env
```
Set Postgres credential for both default and test database

```bash
docker compose up
docker compose run --rm --workdir /backend backend  python manage.py migrate
```
Project should be running on http://localhost:5001

API: http://localhost:5001/api/

## Run tests:

```bash
docker compose run --rm --workdir /backend backend  pytest .
```


## Git hooks
This project has configured [pre-commit](https://pre-commit.com/) with following hooks:
* black
* flake8
* reorder-python-imports
Configure it by running:
```bash
pip install pre-commit
pre-commit install
```

 