# 📖 Examples - Dremio OpenMetadata Connector# Examples



Examples pratiques démontrant l'utilisation du connecteur.This directory contains example scripts showing how to use the Dremio connector in different scenarios.



## 📂 Exemples Disponibles## Available Examples



### ⭐ `full_sync_example.py` - Synchronisation Complète### `basic_ingestion.py`

Synchronisation automatique complète de Dremio vers OpenMetadata.

Basic example showing how to use the connector programmatically.

**Usage**:

```bash**Usage**:

python examples/full_sync_example.py```bash

```python examples/basic_ingestion.py

```

**Résultat Attendu**: 36 ressources découvertes, 9 DBs, 15 schemas, 20 tables

**What it does**:

### 🔧 `create_service.py` - Création du Service- Initializes DremioSource with configuration

Crée le service Dremio dans OpenMetadata (à faire une fois).- Tests connections to Dremio and OpenMetadata

- Runs metadata ingestion

**Usage**:- Displays results

```bash

python examples/create_service.py**Configuration**:

```Edit the `config` dictionary in the script with your:

- Dremio connection details

### 📝 `basic_ingestion.py` - Exemple Simple- OpenMetadata server URL and JWT token

Exemple minimaliste pour apprendre l'API.- Service name and ingestion options



**Code**:## Creating Your Own Examples

```python

from dremio_connector import sync_dremio_to_openmetadata### Template



stats = sync_dremio_to_openmetadata(```python

    dremio_url="http://localhost:9047",from src.dremio_connector.core.dremio_source import DremioSource

    dremio_user="admin",from src.dremio_connector.utils.logger import setup_logger

    dremio_password="admin123",

    openmetadata_url="http://localhost:8585/api",# Setup logging

    jwt_token="your-token",logger = setup_logger(name='my_example', level='INFO')

    service_name="dremio_service"

)# Configuration

```config = {

    'dremioHost': 'localhost',

## 🎓 Patterns d'Utilisation    'dremioPort': 9047,

    'dremioUsername': 'admin',

### Sync Manuel (Une fois)    'dremioPassword': 'admin123',

```bash    'openMetadataServerConfig': {

python examples/create_service.py        'hostPort': 'http://localhost:8585/api',

python examples/full_sync_example.py        'securityConfig': {'jwtToken': 'your-token'}

```    },

    'serviceName': 'my-service',

### Sync Automatique (Quotidien)    'include_sources': True,

```bash    'include_vds': True,

# Windows Task Scheduler ou Linux Cron}

0 2 * * * /path/to/python /path/to/examples/full_sync_example.py

```# Initialize and run

connector = DremioSource(config)

## 📚 Documentationif connector.test_connection():

    results = connector.ingest_metadata()

- [Quick Start](../docs/QUICK_START.md) - Guide pas à pas    logger.info(f"Results: {results}")

- [README Principal](../README.md) - Documentation complète```



---### Using Configuration Files



**Besoin d'aide?** Consultez le [README](../README.md#-troubleshooting)```python

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
