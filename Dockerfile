# Image de base OpenMetadata 1.9.7
FROM docker.getcollate.io/openmetadata/ingestion:1.9.7

# Copie les fichiers du connecteur
WORKDIR /opt/airflow
COPY dremio_connector/ dremio_connector/
COPY setup.py .
COPY requirements.txt .
COPY pyproject.toml .

# Installation du package en mode développement (en tant qu'airflow)
RUN pip install --no-deps -e .
