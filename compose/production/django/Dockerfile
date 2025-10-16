FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.deploy \
    PORT=8080

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    libmariadb3 \
    gettext \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . /app
COPY compose/production/django/start.sh /app/start.sh
RUN chmod +x /app/start.sh

RUN python manage.py collectstatic --noinput || true

EXPOSE 8080

CMD ["/app/start.sh"]
