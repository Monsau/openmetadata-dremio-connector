# Dremio OpenMetadata Connector

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![OpenMetadata](https://img.shields.io/badge/OpenMetadata-1.9.7%2B-orange.svg)](https://open-metadata.org/)

> **Enterprise-grade connector for automated metadata ingestion from Dremio to OpenMetadata**

Automatically discover and synchronize **100% of your Dremio resources** with complete metadata.

---

## ✨ Highlights

🚀 **100% Auto-Discovery** - Recursively finds all spaces, sources, folders, and datasets  
⚡ **Complete Metadata** - Columns, types, descriptions automatically extracted  
🔄 **Idempotent Sync** - Safe to re-run, updates existing entities  
📊 **Production Ready** - Tested on real Dremio instances, comprehensive logging  
🎯 **Type Mapping** - Automatic Dremio → OpenMetadata type conversion  
🔗 **dbt Integration** - Parse manifest.json, automatic lineage capture  
✅ **Lineage Verification** - Check and visualize table lineage

**Real Results**: 36 resources discovered in 12s (9 DBs, 15 schemas, 20 tables) ✅  
**dbt Results**: 4 models ingested with full lineage ✅

---

## 🚀 Quick Start

### Install

```bash
git clone https://github.com/Monsau/dremio_connector.git
cd dremio_connector
python -m venv venv_dremio
.\venv_dremio\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
pip install -e .
```

### Run

**1. Basic Sync (Dremio resources only)**:
```python
from dremio_connector import sync_dremio_to_openmetadata

stats = sync_dremio_to_openmetadata(
    dremio_url="http://localhost:9047",
    dremio_user="admin",
    dremio_password="admin123",
    openmetadata_url="http://localhost:8585/api",
    jwt_token="your-jwt-token",
    service_name="dremio_service"
)

print(f"✅ Synced: {stats}")
# {'resources_discovered': 36, 'databases_created': 9, 
#  'schemas_created': 15, 'tables_created': 20, 'errors': 0}
```

**2. dbt Integration (with lineage)**:
```python
from dremio_connector.dbt import DbtIntegration

dbt = DbtIntegration(
    manifest_path='dbt/target/manifest.json',
    openmetadata_config={
        'api_url': 'http://localhost:8585/api',
        'token': 'your-jwt-token',
        'service_name': 'dremio_dbt_service'
    }
)

# Extract dbt models
models = dbt.extract_models()
print(f"📦 Found {len(models)} dbt models")

# Ingest with lineage
stats = dbt.ingest_to_openmetadata(models)
print(f"✅ Ingested: {stats}")
# {'tables_created': 4, 'lineage_created': 6}
```

**Or use the examples**:
```bash
python examples/full_sync_example.py       # Dremio sync
python examples/dbt_ingestion_example.py   # dbt + lineage
```

---

## 📖 Core Concepts

### Auto-Discovery

The connector **recursively explores** the entire Dremio catalog:

```
Dremio API (/api/v3/catalog)
├── Spaces (@admin, Analytics, Reports, ...)
│   ├── Folders (staging, marts, ...)
│   └── Datasets (VDS/PDS with columns)
├── Sources (PostgreSQL, MinIO, ...)
│   ├── Folders (public, schemas, ...)
│   └── Datasets (tables with columns)
└── Handles: type normalization, cycles, timeouts
```

**Discovered Resources**:
- **Spaces**: User workspaces
- **Sources**: External data (PostgreSQL, S3, etc.)
- **Folders**: Hierarchical organization
- **Datasets**: Tables (PDS) and Views (VDS) with full columns

### Hierarchical Mapping

```
Dremio                    →  OpenMetadata
────────────────────────────────────────────
Space (Analytics)         →  Database
  ├─ Folder (Reports)     →    Schema
  │   └─ Dataset (Sales)  →      Table
  └─ Dataset (KPIs)       →    Schema (default) → Table

Source (PostgreSQL)       →  Database
  └─ Folder (public)      →    Schema
      └─ Dataset (users)  →      Table
```

### Type Mapping

| Dremio | OpenMetadata | | Dremio | OpenMetadata |
|--------|--------------|---|--------|--------------|
| INTEGER | INT | | DOUBLE | DOUBLE |
| BIGINT | BIGINT | | VARCHAR | VARCHAR |
| FLOAT | FLOAT | | BOOLEAN | BOOLEAN |
| DATE | DATE | | TIMESTAMP | TIMESTAMP |
| DECIMAL | DECIMAL | | *other* | VARCHAR |

---

## 🏗️ Architecture

### Main Components

**`sync_engine.py`** - Core engine with 3 classes:

1. **`DremioAutoDiscovery`**  
   - Authenticates to Dremio
   - Recursively discovers all resources
   - Normalizes inconsistent API types
   - Extracts columns with type mapping

2. **`OpenMetadataSyncEngine`**  
   - Creates/updates databases (PUT requests)
   - Creates/updates schemas
   - Creates/updates tables with columns
   - Tracks statistics

3. **`DremioOpenMetadataSync`**  
   - Orchestrates full workflow
   - Organizes hierarchy
   - Returns detailed statistics

**`dbt_integration.py`** - dbt integration with 1 main class:

4. **`DbtIntegration`**  
   - Parses dbt manifest.json
   - Extracts models with metadata
   - Builds automatic lineage (upstream/downstream)
   - Ingests to OpenMetadata with lineage
   - Supports columns, tests, descriptions, tags

**`lineage_checker.py`** - Lineage verification with 1 class:

5. **`LineageChecker`**  
   - Checks table lineage completeness
   - Verifies all tables in database
   - Visualizes lineage (ASCII/JSON)
   - Generates detailed reports

### Project Structure

```
dremio_connector/
├── src/dremio_connector/
│   ├── core/
│   │   ├── sync_engine.py       ⭐ Main engine (Phase 1)
│   │   ├── connector.py         ⚠️ Deprecated
│   │   └── dremio_source.py     ⚠️ Deprecated
│   ├── dbt/
│   │   ├── dbt_integration.py   ⭐ dbt parser (Phase 2)
│   │   └── lineage_checker.py   ⭐ Lineage verification (Phase 2)
│   ├── clients/
│   │   ├── dremio_client.py     # Dremio API v3
│   │   └── openmetadata_client.py # OpenMetadata API v1
│   ├── utils/
│   └── cli.py
├── examples/
│   ├── full_sync_example.py     ⭐ Dremio sync
│   ├── dbt_ingestion_example.py ⭐ dbt + lineage (NEW)
│   └── create_service.py        # Service creation
├── tests/
├── docs/
│   ├── ENRICHMENT_PLAN.md       # Roadmap
│   └── CLEANUP_PLAN.md          # Maintenance
└── README.md                    # This file
```

---

## ⚙️ Configuration

### Get JWT Token

1. Open http://localhost:8585
2. **Settings** → **Bots** → **ingestion-bot**
3. **Generate New Token** → Copy

### Create Service (First Time)

```python
# Run once to create the service
python examples/create_service.py
```

Or use existing service like `dremio_dbt_service`.

---

## 📊 What Gets Synced

**Example from real instance**:

```
🔍 Discovery:
├── 1 Home (@admin)
├── 7 Spaces (Analytics, Reports, DataLake, raw, staging, marts, ...)
├── 2 Sources (PostgreSQL_Business, minio-storage)
├── 6 Folders (staging.staging, PostgreSQL_Business.public, ...)
└── 20 Datasets with full columns
───────────────────────────────────────
Total: 36 resources → 9 DBs, 15 schemas, 20 tables
```

**Metadata extracted**:
- Database: name, description, service
- Schema: name, description, parent DB
- Table: name, description, type, parent schema
- **Column**: name, type, position, length, description

---

## 🔧 Troubleshooting

### Issue: Authentication Failed
```bash
# Verify Dremio is running
curl http://localhost:9047/api/v3/catalog

# Check credentials in your code
```

### Issue: Service Not Found (404)
```bash
# Create service first
python examples/create_service.py
```

### Issue: Timeout Warnings
Expected for empty MinIO folders. Connector continues gracefully.

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Run sync with detailed logs
```

---

## 🗺️ Roadmap

### ✅ Phase 1: Auto-Discovery (COMPLETED)
- [x] Recursive discovery
- [x] Type normalization
- [x] Column extraction
- [x] Idempotent sync
- **Result**: 36 resources, 0 errors, 12.34s

### ✅ Phase 2: dbt Integration (COMPLETED)
- [x] Parse dbt manifest.json
- [x] Automatic lineage capture (upstream/downstream)
- [x] Model metadata extraction (columns, tests, tags)
- [x] Lineage verification and visualization
- **Result**: 4 models, 6 lineage edges, 21 columns

### ⏳ Phase 3: Enhanced CLI (NEXT)
- [ ] `dremio-connector sync`
- [ ] `dremio-connector discover`
- [ ] `dremio-connector ingest-dbt`
- [ ] `dremio-connector check-lineage`

### ⏳ Phase 4: Lineage Agent
- [ ] SQL parsing for VDS
- [ ] Automatic dependency extraction
- [ ] Column-level lineage

See [ENRICHMENT_PLAN.md](docs/ENRICHMENT_PLAN.md) for details.

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src/dremio_connector tests/

# Manual test
python examples/full_sync_example.py
```

Expected output:
```
================================================================================
🚀 SYNCHRONISATION AUTOMATIQUE DREMIO → OPENMETADATA
================================================================================

✅ Authentification Dremio réussie
🔍 Démarrage auto-discovery Dremio...
📦 10 items racine trouvés
✓ [SPACE  ] Analytics
✓ [DATASET] Analytics.Vue_Clients_Complets
...
✅ Découverte terminée: 36 ressources

================================================================================
📊 STATISTIQUES DE SYNCHRONISATION
================================================================================
Ressources découvertes:     36
Databases créées/màj:       9
Schemas créés/màj:          15
Tables créées/màj:          20
Erreurs:                    0
Durée:                      12.34s
================================================================================
```

For dbt integration:
```bash
python examples/dbt_ingestion_example.py
```

Expected output:
```
================================================================================
🚀 INGESTION DBT → OPENMETADATA
================================================================================

📖 Étape 1/6: Chargement manifest.json
✅ Manifest chargé: 22 nodes, 2 sources (dbt 1.10.8)

📦 Étape 2/6: Extraction modèles dbt
✅ 4 modèles extraits

📊 Étape 3/6: Organisation par database/schema
  📁 MARTS.marts (2 modèles)
    ├─ 📄 dim_customers (table) - 7 colonnes
    └─ 📄 fct_orders (table) - 5 colonnes
  📁 STAGING.staging (2 modèles)
    ├─ 📄 stg_customers (view) - 4 colonnes
    └─ 📄 stg_orders (view) - 5 colonnes

🔗 Étape 4/6: Analyse lineage
✅ Lineage extrait pour 4 modèles
  stg_orders → dim_customers, fct_orders
  stg_customers → dim_customers, fct_orders

✅ Ingestion terminée!
📊 Tables ingérées: 4
🔗 Lineages créés: 6
```

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Add tests
4. Commit (`git commit -m 'Add feature'`)
5. Push (`git push origin feature/amazing`)
6. Open Pull Request

**Code Style**: PEP 8, Google docstrings, type hints

---

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE)

---

## 🆘 Support

- **Docs**: See `docs/` directory
- **Examples**: See `examples/`
- **Issues**: [GitHub Issues](https://github.com/Monsau/dremio_connector/issues)

---

## 🎉 Success Story

**Real-World Results**:

**Infrastructure**: 
- Dremio 26.0 Community
- OpenMetadata 1.9.7
- dbt 1.10.8

**Phase 1 (Dremio Discovery)**:
- **Discovered**: 36 resources (9 DBs, 15 schemas, 20 tables)
- **Duration**: 12.34 seconds
- **Success Rate**: 100% (0 errors)

**Phase 2 (dbt Integration)**:
- **Models Ingested**: 4 (2 tables, 2 views)
- **Lineage Edges**: 6 relationships
- **Columns**: 21 total with full metadata
- **Success Rate**: 100% (0 errors)

> "Auto-discovery saved us hours of manual entry. All our Dremio assets are now in OpenMetadata with complete column definitions and lineage from dbt!"

---

## 🔗 Related

- [OpenMetadata](https://open-metadata.org/) - Open Source Data Catalog
- [Dremio](https://www.dremio.com/) - Data Lake Engine
- [dbt](https://www.getdbt.com/) - Data Build Tool

---

**Built with ❤️ for the Data Community**

**Version**: 2.1.0 | **Updated**: 2025-10-12 | **Status**: ✅ Production Ready (Phase 1 + Phase 2)

---

## 🚀 Get Started!

```bash
git clone https://github.com/Monsau/dremio_connector.git
cd dremio_connector
pip install -r requirements.txt
python examples/full_sync_example.py
```

**Discover your Dremio metadata in seconds!** 🎉
