# Project Structure Documentation

## Overview

This document explains the restructured Dremio OpenMetadata connector project organization.

## Directory Structure

```
dremio/
│
├── src/dremio_connector/          # Main source code package
│   ├── __init__.py                # Package initialization
│   ├── cli.py                     # Command-line interface
│   │
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── dremio_source.py       # Main DremioSource class for metadata ingestion
│   │   └── connector.py           # Connector wrapper class
│   │
│   ├── clients/                   # API client implementations
│   │   ├── __init__.py
│   │   ├── dremio_client.py       # Dremio REST API client
│   │   └── openmetadata_client.py # OpenMetadata REST API client
│   │
│   └── utils/                     # Utility modules
│       ├── __init__.py
│       ├── logger.py              # Logging configuration
│       └── config.py              # Configuration loading and validation
│
├── config/                        # Configuration files
│   └── ingestion.yaml             # Main ingestion configuration
│
├── examples/                      # Example usage scripts
│   └── basic_ingestion.py         # Simple ingestion example
│
├── tests/                         # Unit tests
│   ├── conftest.py                # Pytest configuration
│   ├── test_dremio_client.py      # Tests for DremioClient
│   └── test_openmetadata_client.py # Tests for OpenMetadataClient
│
├── docs/                          # Documentation
│   └── guides/                    # User guides
│
├── scripts/                       # Utility scripts
│
├── requirements.txt               # Python dependencies
├── setup.py                       # Package installation configuration
├── .gitignore                     # Git ignore rules
└── README.md                      # Main project documentation
```

## Module Descriptions

### `src/dremio_connector/`

Main package containing all connector code.

#### `core/`

Core business logic for metadata extraction and ingestion:

- **`dremio_source.py`**: Main `DremioSource` class implementing metadata ingestion workflow
  - Connection testing
  - Service creation in OpenMetadata
  - Source and dataset ingestion
  - VDS (Virtual Data Set) ingestion
  - Data type mapping

- **`connector.py`**: High-level connector wrapper providing simplified interface

#### `clients/`

API client implementations for external services:

- **`dremio_client.py`**: Dremio REST API client
  - Authentication via username/password
  - Source discovery
  - Dataset and VDS retrieval
  - Schema extraction
  - Recursive catalog traversal

- **`openmetadata_client.py`**: OpenMetadata REST API client
  - JWT authentication
  - Service management
  - Database and schema creation
  - Table and view creation
  - Pipeline management

#### `utils/`

Utility functions and helpers:

- **`logger.py`**: Logging configuration
  - Console and file handlers
  - Configurable log levels
  - Formatted output

- **`config.py`**: Configuration management
  - YAML/JSON loading
  - Configuration merging
  - Validation utilities

#### `cli.py`

Command-line interface providing:
- Configuration file loading
- Connection testing
- Full ingestion workflow
- Logging configuration

## Usage Patterns

### As a Library

```python
from src.dremio_connector.core.dremio_source import DremioSource

config = {...}
connector = DremioSource(config)
results = connector.ingest_metadata()
```

### As a CLI Tool

```bash
dremio-connector --config config/ingestion.yaml
```

### As an Installed Package

```bash
pip install -e .
dremio-connector --config config/ingestion.yaml
```

## Configuration

Main configuration file: `config/ingestion.yaml`

Structure follows OpenMetadata ingestion format:
- `source`: Dremio connection and ingestion options
- `sink`: OpenMetadata destination (metadata-rest)
- `workflowConfig`: OpenMetadata server configuration

## Testing

Tests are organized by module:
- `test_dremio_client.py`: Unit tests for Dremio API client
- `test_openmetadata_client.py`: Unit tests for OpenMetadata API client
- `conftest.py`: Shared pytest fixtures

Run tests:
```bash
pytest tests/
```

## Development Workflow

1. **Install in development mode**:
   ```bash
   pip install -e .
   ```

2. **Make changes** to source code in `src/`

3. **Run tests**:
   ```bash
   pytest tests/
   ```

4. **Test CLI**:
   ```bash
   dremio-connector --config config/ingestion.yaml --test-connection
   ```

## Migration from Legacy Structure

Old structure → New structure:
- `connectors/dremio/*.py` → `src/dremio_connector/clients/`
- `ingestion/*.py` → Use new `DremioSource` class
- Configuration files → Centralized in `config/`
- Scripts → Organized in `scripts/` or `examples/`

## Best Practices

1. **Import from `src.dremio_connector`**: Use absolute imports
2. **Configuration via YAML**: Keep credentials in config files (use .env for secrets)
3. **Logging**: Use provided logger utilities
4. **Testing**: Write tests for new features
5. **Documentation**: Update docs when adding features

## Future Improvements

- [ ] Add more comprehensive tests
- [ ] Implement async API calls
- [ ] Add incremental ingestion support
- [ ] Support for additional Dremio features (reflections, jobs, etc.)
- [ ] Enhanced error handling and retry logic
- [ ] Performance optimization for large catalogs
