
dremio/
├── � README.md                    # Ce que tu lis là
├──  docker-compose-auto.yml     # Env Dremio + OpenMetadata
├──  ingestion/                  # Le cœur du connecteur
│   ├──  example_usage.py        # Ton point d'entrée principal
│   ├── ️ dremio_to_openmetadata_ingestion.py  # Le moteur
│   ├──  requirements.txt        # Dépendances Python
│   ├──  config/
│   │   └── dremio_ingestion.yaml  # Config avancée
│   └── ️ src/
│       ├── client/
│       │   ├── dremio_client.py   # API Dremio
│       │   └── openmetadata_client.py  # API OpenMetadata
│       └── utils/
│           └── config_manager.py   # Gestion config
├── � initEnv/                    # Scripts d'init Dremio
└──  env/                        # Environnement Docker

# Dremio ↔ OpenMetadata Connector

Welcome to the Dremio ↔ OpenMetadata connector! This project provides a professional, enterprise-grade solution for automated metadata ingestion from Dremio into OpenMetadata.

---

## � Documentation

- [Français](./README-fr.md) | [Español](./README-es.md) | [العربية](./README-ar.md)

---

## � Quick Start

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd dremio
   ```
2. **Set up Python environment**
   ```powershell
   python -m venv venv_dremio
   .\venv_dremio\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Configure your connection**
   - Copy and edit `.env.example` to `.env` in the `ingestion/` directory.
   - Set your Dremio and OpenMetadata endpoints and credentials.
4. **Run health check**
   ```powershell
   python ingestion/example_usage.py --test-connections
   ```
5. **Ingest metadata**
   ```powershell
   python ingestion/example_usage.py
   ```

For advanced configuration, troubleshooting, and architecture details, see the full documentation in this file and the `docs/` directory.

---

## �️ Project Structure

- `README-fr.md`, `README-es.md`, `README-ar.md` — Language-specific quickstart and links
- `requirements.txt` — Python dependencies
- `docker-compose-auto.yml` — Infrastructure services
- `ingestion/` — Main connector code and configuration
- `initEnv/` — Dremio initialization scripts
- `env/` — Docker environment files
- `docs/` — Additional documentation

---

##  Contributing & Support

We welcome contributions in all languages! For details, see the contribution guidelines in this file and the `docs/` directory.

For support, open a GitHub issue or see the support section in this file.

---

**Built with ️ for the global data community**