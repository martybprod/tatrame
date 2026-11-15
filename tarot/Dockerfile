# Image de production du Tarot — même discipline que Ta Trame : gunicorn, jamais
# app.run ; Python 3.11 figé pour que les calculs restent identiques au poste de dev.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt && pip install "gunicorn>=21"

# Code + corpus + images (data/corpus et static/img/cartes sont versionnés)
COPY . .

EXPOSE 8000

# 1 worker suffit : aucune écriture concurrente hors album, et la lecture est un
# simple lookup de corpus. Threads pour encaisser les images en parallèle.
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--timeout", "60", \
     "--bind", "0.0.0.0:8000", "--access-logfile", "-", "wsgi:app"]
