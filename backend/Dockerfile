# Le digest de l'image et les paquets natifs sont documentés dans docs/DEPENDENCIES.md.
FROM python:3.12-slim-bookworm@sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70 AS geospatial-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Bibliothèques GeoDjango fournies ensemble par Debian Bookworm.
# Rasterio/GeoPandas utilisent leurs wheels ; aucun paquet Python GDAL non aligné.
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::Retries=3 update \
    && apt-get install -y --no-install-recommends binutils libgdal32 libgeos-c1v5 libproj25 \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /opt/venv

FROM geospatial-base AS development
WORKDIR /app/backend
COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --require-hashes -r requirements.txt \
    && python -m pip check
COPY backend/ ./
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
