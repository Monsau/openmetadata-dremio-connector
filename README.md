# Dremio OpenMetadata Connector

dremio/

A professional, enterprise-grade connector for automated metadata ingestion from Dremio Data Lake Platform into OpenMetadata.├── � README.md                    # Ce que tu lis là

├──  docker-compose-auto.yml     # Env Dremio + OpenMetadata

## 🌍 Documentation Languages├──  ingestion/                  # Le cœur du connecteur

│   ├──  example_usage.py        # Ton point d'entrée principal

- **English** (this file)│   ├── ️ dremio_to_openmetadata_ingestion.py  # Le moteur

- [Français](./README-fr.md)│   ├──  requirements.txt        # Dépendances Python

- [Español](./README-es.md)│   ├──  config/

- [العربية](./README-ar.md)│   │   └── dremio_ingestion.yaml  # Config avancée

│   └── ️ src/

---│       ├── client/

│       │   ├── dremio_client.py   # API Dremio

## 📖 Table of Contents│       │   └── openmetadata_client.py  # API OpenMetadata

│       └── utils/

- [Quick Start](#-quick-start)│           └── config_manager.py   # Gestion config

- [Features](#-features)├── � initEnv/                    # Scripts d'init Dremio

- [Installation](#-installation)└──  env/                        # Environnement Docker

- [Configuration](#-configuration)

- [Usage](#-usage)# Dremio ↔ OpenMetadata Connector

- [Project Structure](#-project-structure)

- [Documentation](#-documentation)Welcome to the Dremio ↔ OpenMetadata connector! This project provides a professional, enterprise-grade solution for automated metadata ingestion from Dremio into OpenMetadata.

- [Testing](#-testing)

- [Troubleshooting](#-troubleshooting)---



---## � Documentation



## 🚀 Quick Start- [Français](./README-fr.md) | [Español](./README-es.md) | [العربية](./README-ar.md)



Get started in 3 simple steps:---



```bash## � Quick Start

# 1. Navigate to project

cd c:/projets/dremio1. **Clone the repository**

   ```powershell

# 2. Quick setup (automated)   git clone <repository-url>

python scripts/quickstart.py   cd dremio

   ```

# 3. Test connection2. **Set up Python environment**

dremio-connector --config config/ingestion.yaml --test-connection   ```powershell

```   python -m venv venv_dremio

   .\venv_dremio\Scripts\Activate.ps1

**That's it!** See [QUICK_START.md](QUICK_START.md) for detailed guide.   python -m pip install --upgrade pip

   pip install -r requirements.txt

---   ```

3. **Configure your connection**

## ✨ Features   - Copy and edit `.env.example` to `.env` in the `ingestion/` directory.

   - Set your Dremio and OpenMetadata endpoints and credentials.

### Metadata Ingestion4. **Run health check**

- ✅ Discover and ingest Dremio sources (PostgreSQL, MinIO, etc.)   ```powershell

- ✅ Ingest Virtual Data Sets (VDS) as views   python ingestion/example_usage.py --test-connections

- ✅ Ingest Physical Data Sets (PDS) as tables   ```

- ✅ Column-level metadata with data types5. **Ingest metadata**

- ✅ Descriptions and display names preservation   ```powershell

   python ingestion/example_usage.py

### Architecture   ```

- ✅ Modular Python package (`src/dremio_connector/`)

- ✅ Installable CLI tool (`dremio-connector`)For advanced configuration, troubleshooting, and architecture details, see the full documentation in this file and the `docs/` directory.

- ✅ REST API clients for Dremio and OpenMetadata

- ✅ Comprehensive test suite with pytest---

- ✅ Configurable logging and error handling

## �️ Project Structure

### Configuration

- ✅ YAML-based configuration following OpenMetadata standards- `README-fr.md`, `README-es.md`, `README-ar.md` — Language-specific quickstart and links

- ✅ Connection options for Dremio and OpenMetadata- `requirements.txt` — Python dependencies

- ✅ Filter patterns for sources and VDS- `docker-compose-auto.yml` — Infrastructure services

- ✅ Tag mapping and classification support- `ingestion/` — Main connector code and configuration

- ✅ Batch processing options- `initEnv/` — Dremio initialization scripts

- `env/` — Docker environment files

---- `docs/` — Additional documentation



## 📦 Installation---



### Prerequisites##  Contributing & Support



- **Python 3.8+** (tested with 3.8 - 3.13)We welcome contributions in all languages! For details, see the contribution guidelines in this file and the `docs/` directory.

- **Dremio instance** (running on localhost:9047 or remote)

- **OpenMetadata instance** (version 1.9.7+)For support, open a GitHub issue or see the support section in this file.

- **JWT token** from OpenMetadata

---

### Automated Setup (Recommended)

**Built with ️ for the global data community**
```bash
python scripts/quickstart.py
```

This script will:
1. Create virtual environment
2. Install all dependencies
3. Set up the package
4. Guide you through configuration

### Manual Installation

```bash
# Create virtual environment
python -m venv venv_dremio

# Activate (Windows)
venv_dremio\Scripts\activate

# Activate (Linux/Mac)
source venv_dremio/bin/activate

# Install package in development mode
pip install -e .

# Or with extras
pip install -e ".[dev]"        # Development tools
pip install -e ".[database]"   # Database connectors
pip install -e ".[search]"     # Search engines
```

---

## ⚙️ Configuration

### 1. Get OpenMetadata JWT Token

1. Open OpenMetadata UI: `http://localhost:8585`
2. Go to **Settings** → **Bots** → **ingestion-bot**
3. Click **"Generate New Token"**
4. Copy the token

### 2. Edit Configuration File

Edit `config/ingestion.yaml`:

```yaml
source:
  type: custom-dremio
  serviceName: Dremio Data Lake Platform
  serviceConnection:
    config:
      type: CustomDatabase
      sourcePythonClass: dremio_connector.core.dremio_source.DremioSource
      connectionOptions:
        # Dremio Connection
        dremioHost: localhost          # ⬅️ Your Dremio host
        dremioPort: "9047"
        dremioUsername: admin          # ⬅️ Your username
        dremioPassword: admin123       # ⬅️ Your password
        
        # Ingestion Options
        include_sources: "true"
        include_vds: "true"
        include_pds: "true"

workflowConfig:
  openMetadataServerConfig:
    hostPort: http://localhost:8585/api  # ⬅️ Your OpenMetadata URL
    authProvider: openmetadata
    securityConfig:
      jwtToken: "your-jwt-token-here"    # ⬅️ Your JWT token
```

---

## 🎯 Usage

### Command Line Interface

```bash
# Test connections
dremio-connector --config config/ingestion.yaml --test-connection

# Run full ingestion
dremio-connector --config config/ingestion.yaml

# With debug logging
dremio-connector --config config/ingestion.yaml --log-level DEBUG

# Save logs to file
dremio-connector --config config/ingestion.yaml --log-file ingestion.log
```

### Programmatic Usage

```python
from src.dremio_connector.core.dremio_source import DremioSource
from src.dremio_connector.utils.logger import setup_logger

# Setup logging
logger = setup_logger(name='my_script', level='INFO')

# Configuration
config = {
    'dremioHost': 'localhost',
    'dremioPort': 9047,
    'dremioUsername': 'admin',
    'dremioPassword': 'admin123',
    'openMetadataServerConfig': {
        'hostPort': 'http://localhost:8585/api',
        'securityConfig': {'jwtToken': 'your-token'}
    },
    'serviceName': 'dremio-service',
    'include_sources': True,
    'include_vds': True,
}

# Initialize and run
connector = DremioSource(config)

# Test connections
if connector.test_connection():
    logger.info("✅ All connections successful")
    
    # Run ingestion
    results = connector.ingest_metadata()
    logger.info(f"Ingestion results: {results}")
```

See `examples/basic_ingestion.py` for more examples.

---

## 📁 Project Structure

```
dremio/
├── 📦 src/dremio_connector/      # Main source code
│   ├── core/                     # Business logic
│   │   ├── dremio_source.py      # Main source class
│   │   └── connector.py          # Connector wrapper
│   ├── clients/                  # API clients
│   │   ├── dremio_client.py      # Dremio REST API
│   │   └── openmetadata_client.py # OpenMetadata REST API
│   ├── utils/                    # Utilities
│   │   ├── logger.py             # Logging configuration
│   │   └── config.py             # Config management
│   └── cli.py                    # CLI entry point
│
├── ⚙️  config/                    # Configuration files
│   └── ingestion.yaml            # Main configuration
│
├── 📖 examples/                   # Usage examples
│   ├── basic_ingestion.py        # Simple example
│   └── README.md                 # Examples guide
│
├── 🧪 tests/                      # Unit tests
│   ├── test_dremio_client.py
│   ├── test_openmetadata_client.py
│   └── conftest.py               # Pytest configuration
│
├── 📚 docs/                       # Documentation
│   ├── PROJECT_STRUCTURE.md      # Detailed structure
│   └── MIGRATION_GUIDE.md        # Migration guide
│
├── 🛠️  scripts/                   # Utility scripts
│   └── quickstart.py             # Quick setup script
│
├── 📄 README.md                   # This file
├── 📄 QUICK_START.md             # Quick start guide
├── 📄 RESTRUCTURATION_SUMMARY.md # Restructuring summary
├── 📋 requirements.txt            # Python dependencies
└── 📦 setup.py                    # Package configuration
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Main documentation (this file) |
| [QUICK_START.md](QUICK_START.md) | Quick start visual guide |
| [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Detailed project structure |
| [examples/README.md](examples/README.md) | Examples guide |

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/

# With coverage
pytest --cov=src/dremio_connector tests/

# Specific test file
pytest tests/test_dremio_client.py -v

# With detailed output
pytest tests/ -v --tb=short
```

### Run Linters

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

---

## 🔧 Troubleshooting

### Connection Issues

**Problem**: Cannot connect to Dremio
```bash
# Check Dremio is running
curl http://localhost:9047/api/v3/catalog

# Verify credentials in config/ingestion.yaml
```

**Problem**: Cannot connect to OpenMetadata
```bash
# Check OpenMetadata is running
curl http://localhost:8585/api/v1/system/version

# Verify JWT token is valid and not expired
```

### Installation Issues

**Problem**: `dremio-connector` command not found
```bash
# Reinstall package
pip install -e .

# Or use module directly
python -m dremio_connector.cli --config config/ingestion.yaml
```

**Problem**: Import errors
```bash
# Make sure package is installed
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### Ingestion Issues

**Problem**: No sources found
- Verify Dremio has sources configured
- Check `include_sources` is set to `true` in config
- Verify user has permissions in Dremio

**Problem**: No VDS found
- Verify VDS are published in Dremio
- Check `include_vds` is set to `true` in config
- Ensure VDS are in accessible spaces

### Debug Mode

Enable debug logging for detailed information:

```bash
dremio-connector --config config/ingestion.yaml --log-level DEBUG --log-file debug.log
```

Check logs in `debug.log` file.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run tests: `pytest tests/`
6. Submit a Pull Request

---

## 📄 License

This project is licensed under the Apache License 2.0.

---

## 🆘 Support

- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Issues**: GitHub Issues
- **Quick Start**: [QUICK_START.md](QUICK_START.md)

---

## 📊 Ingestion Results

After successful ingestion, you'll find in OpenMetadata:

### Service
- **Service Name**: Dremio Data Lake Platform
- **Service Type**: CustomDatabase

### Schemas
- One schema per Dremio source (PostgreSQL, MinIO, etc.)
- One schema per VDS space (Analytics, DataLake, etc.)

### Tables and Views
- Physical tables from sources with columns and metadata
- Virtual views (VDS) with SQL definitions
- Column descriptions and data types

### Pipeline
- Automated ingestion pipeline
- Scheduled for daily updates (configurable)

---

## 🎉 Get Started Now!

```bash
# Quick start in 3 commands
cd c:/projets/dremio
python scripts/quickstart.py
dremio-connector --config config/ingestion.yaml --test-connection
```

For detailed instructions, see [QUICK_START.md](QUICK_START.md).

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-08  
**Status**: ✅ Production Ready
