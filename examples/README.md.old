# Examples

This directory contains example scripts showing how to use the Dremio connector in different scenarios.

## Available Examples

### `basic_ingestion.py`

Basic example showing how to use the connector programmatically.

**Usage**:
```bash
python examples/basic_ingestion.py
```

**What it does**:
- Initializes DremioSource with configuration
- Tests connections to Dremio and OpenMetadata
- Runs metadata ingestion
- Displays results

**Configuration**:
Edit the `config` dictionary in the script with your:
- Dremio connection details
- OpenMetadata server URL and JWT token
- Service name and ingestion options

## Creating Your Own Examples

### Template

```python
from src.dremio_connector.core.dremio_source import DremioSource
from src.dremio_connector.utils.logger import setup_logger

# Setup logging
logger = setup_logger(name='my_example', level='INFO')

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
    'serviceName': 'my-service',
    'include_sources': True,
    'include_vds': True,
}

# Initialize and run
connector = DremioSource(config)
if connector.test_connection():
    results = connector.ingest_metadata()
    logger.info(f"Results: {results}")
```

### Using Configuration Files

```python
from src.dremio_connector.utils.config import load_config
from src.dremio_connector.core.dremio_source import DremioSource

# Load from YAML
config = load_config('config/ingestion.yaml')

# Extract and merge configurations
source_config = config['source']['serviceConnection']['config']['connectionOptions']
source_config.update(config['workflowConfig'])

# Run ingestion
connector = DremioSource(source_config)
results = connector.ingest_metadata()
```

## Common Scenarios

### 1. Ingest Only Sources

```python
config = {
    # ... connection details
    'include_sources': True,
    'include_vds': False,
    'include_pds': False,
}
```

### 2. Ingest Only VDS

```python
config = {
    # ... connection details
    'include_sources': False,
    'include_vds': True,
    'include_pds': False,
}
```

### 3. Filter by Pattern

```python
config = {
    # ... connection details
    'source_filter_pattern': 'prod_.*',
    'source_exclude_pattern': 'test_.*',
}
```

### 4. Custom Logging

```python
from src.dremio_connector.utils.logger import setup_logger

logger = setup_logger(
    name='my_script',
    level='DEBUG',
    log_file='ingestion.log'
)
```

### 5. Test Connection Only

```python
connector = DremioSource(config)
if connector.test_connection():
    print("✅ All connections successful")
else:
    print("❌ Connection failed")
```

## Tips

1. **Use Virtual Environment**: Always activate the virtual environment before running examples
2. **Secure Credentials**: Don't commit credentials. Use environment variables or .env files
3. **Start Small**: Test with a small dataset first before ingesting everything
4. **Check Logs**: Enable DEBUG logging to troubleshoot issues
5. **Configuration**: Keep configuration files in `config/` directory

## Need Help?

- Check main documentation: `../README.md`
- See project structure: `../docs/PROJECT_STRUCTURE.md`
- Migration guide: `../docs/MIGRATION_GUIDE.md`
