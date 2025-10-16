# Cosmos

Backend service for eitr assignment

## Getting Started

### Prerequisites

- Python 3.12+
- Django 5.2+
- uv (install via `pipx install uv` or `brew install uv`)

### Bootstrap

1. Clone and enter the project directory

```bash
git clone git@github.com:jingrandev/cosmos.git
cd cosmos
```

2. Initialize the development environment

```bash
make init
```

3. Run database migrations

```bash
make migrate
```

4. Create a superuser

```bash
python manage.py createsuperuser
```

5. Start the development server

```bash
python manage.py runserver
```

### Common commands

```bash
make help               # show available targets
make init               # create venv and install dependencies
make lint               # run linters (ruff check)
make fix                # auto-fix and format (ruff fix + format)
make typecheck          # run mypy
make test               # run tests (pytest)
make cov                # run tests with coverage (terminal)
make migrations app     # create migrations for a given app
make migrate            # apply migrations
make run host:port      # run dev server, e.g. make run 0.0.0.0:8000
make cleanup            # clean caches and artifacts
make teardown           # remove local venv and setup marker
```

## API Documentation

The API documentation is available at `/docs/` when the server is running.

## License

Not open source
