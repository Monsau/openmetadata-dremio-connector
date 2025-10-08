# Migration Guide - Legacy to New Structure

This document guides you through migrating from the old project structure to the new organized structure.

## Overview of Changes

The project has been restructured for better organization, maintainability, and Python packaging best practices.

### Key Changes

1. **Centralized Source Code**: All code moved to `src/dremio_connector/`
2. **Modular Architecture**: Clear separation between clients, core logic, and utilities
3. **Proper Python Package**: Can be installed with `pip install -e .`
4. **Unified Configuration**: Single config file format in `config/ingestion.yaml`
5. **Testing Framework**: Organized tests with pytest
6. **CLI Tool**: Installable command-line interface

## Migration Steps

### 1. Update Imports

**Old imports**:
```python
from connectors.dremio.dremio_client import DremioClient
from connectors.dremio.openmetadata_client import OpenMetadataClient
```

**New imports**:
```python
from src.dremio_connector.clients.dremio_client import DremioClient
from src.dremio_connector.clients.openmetadata_client import OpenMetadataClient
```

### 2. Use New DremioSource Class

**Old way** (manual client management):
```python
from connectors.dremio.connector import DremioConnector

connector = DremioConnector(dremio_config, om_config)
connector.ingest()
```

**New way** (unified source class):
```python
from src.dremio_connector.core.dremio_source import DremioSource

config = {
    'dremioHost': 'localhost',
    'dremioPort': 9047,
    # ... other config
}
source = DremioSource(config)
results = source.ingest_metadata()
```

### 3. Configuration Files

**Old structure** (multiple files):
```
ingestion/config/dremio_ingestion.yaml
connectors/dremio/config_manager.py
```

**New structure** (single file):
```
config/ingestion.yaml
```

The new format follows OpenMetadata standard:
```yaml
source:
  type: custom-dremio
  serviceConnection:
    config:
      connectionOptions:
        dremioHost: localhost
        dremioPort: "9047"
        # ...

workflowConfig:
  openMetadataServerConfig:
    hostPort: http://localhost:8585/api
    # ...
```

### 4. Running Ingestion

**Old way**:
```bash
python ingestion/dremio_to_openmetadata_ingestion.py
```

**New way** (CLI):
```bash
dremio-connector --config config/ingestion.yaml
```

**New way** (programmatic):
```python
from src.dremio_connector.core.dremio_source import DremioSource
from src.dremio_connector.utils.config import load_config

config = load_config('config/ingestion.yaml')
source_config = config['source']['serviceConnection']['config']['connectionOptions']
source_config.update(config['workflowConfig'])

source = DremioSource(source_config)
results = source.ingest_metadata()
```

### 5. Logging

**Old way**:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

**New way**:
```python
from src.dremio_connector.utils.logger import setup_logger

logger = setup_logger(name='my_script', level='INFO', log_file='my.log')
```

### 6. Testing

**Old structure**: No organized tests

**New structure**:
```
tests/
├── conftest.py
├── test_dremio_client.py
└── test_openmetadata_client.py
```

Run tests:
```bash
pytest tests/
```

## File Mapping

| Old Location | New Location | Status |
|-------------|-------------|--------|
| `connectors/dremio/dremio_client.py` | `src/dremio_connector/clients/dremio_client.py` | Migrated |
| `connectors/dremio/openmetadata_client.py` | `src/dremio_connector/clients/openmetadata_client.py` | Migrated |
| `connectors/dremio/connector.py` | `src/dremio_connector/core/connector.py` | Migrated |
| `ingestion/dremio_to_openmetadata_ingestion.py` | `src/dremio_connector/core/dremio_source.py` | Replaced |
| `ingestion/config/*.yaml` | `config/ingestion.yaml` | Consolidated |
| Various scripts | `examples/` and `scripts/` | Organized |

## Deprecated Components

The following components are deprecated and should not be used:

- `ingestion/dremio_ingestion_clean.py` - Use new `DremioSource` class
- `ingestion/setup_ingestion.py` - Use `scripts/quickstart.py`
- `connectors/dremio/config_manager.py` - Use `utils/config.py`
- Individual script files in root - Moved to `scripts/` or `examples/`

## Installation

### Old way:
```bash
pip install -r requirements.txt
```

### New way:
```bash
# Install dependencies and package
pip install -e .

# Or install with extras
pip install -e ".[dev]"        # Development tools
pip install -e ".[database]"   # Database connectors
pip install -e ".[search]"     # Search engines
```

## Environment Setup

### Old way:
```bash
python -m venv venv_dremio_311
venv_dremio_311\Scripts\activate
pip install -r requirements.txt
```

### New way:
```bash
# Automated setup
python scripts/quickstart.py

# Or manual
python -m venv venv_dremio
venv_dremio\Scripts\activate
pip install -e .
```

## Benefits of New Structure

1. **Better Organization**: Clear separation of concerns
2. **Easier Testing**: Organized test structure with pytest
3. **Reusable Package**: Can be installed and imported in other projects
4. **CLI Tool**: Convenient command-line interface
5. **Standard Practices**: Follows Python packaging best practices
6. **Documentation**: Comprehensive docs in `docs/` directory
7. **Type Hints**: Better IDE support and type checking
8. **Logging**: Unified logging configuration

## Troubleshooting

### Import Errors

If you get import errors:
```bash
# Make sure package is installed
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/dremio/src"
```

### CLI Not Found

If `dremio-connector` command is not found:
```bash
# Reinstall package
pip install -e .

# Or use module directly
python -m dremio_connector.cli --config config/ingestion.yaml
```

### Configuration Issues

Make sure your config file follows the new format:
```bash
# Validate config
python -c "from src.dremio_connector.utils.config import load_config; print(load_config('config/ingestion.yaml'))"
```

## Support

For questions or issues:
- Check documentation in `docs/`
- Review examples in `examples/`
- See `docs/PROJECT_STRUCTURE.md` for detailed structure info
