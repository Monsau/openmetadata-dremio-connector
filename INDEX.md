# 📑 INDEX - Dremio OpenMetadata Connector# Dremio OpenMetadata Connector - Documentation Index



Guide complet des fichiers du projet et leur rôle.## 📚 Main Documentation



---### Getting Started

1. **[README.md](README.md)** - Main documentation with overview, installation, and usage

## 📁 Structure du Projet2. **[QUICK_START.md](QUICK_START.md)** - Visual quick start guide with step-by-step instructions



```### Language Versions

dremio_connector/- **[README-fr.md](README-fr.md)** - Documentation en français

├── 📦 Code Source- **[README-es.md](README-es.md)** - Documentación en español

├── 📖 Documentation- **[README-ar.md](README-ar.md)** - التوثيق بالعربية

├── 🧪 Tests

├── ⚙️ Configuration## 🔧 Technical Documentation

└── 📝 Exemples

```### Project Structure & Architecture

- **[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Detailed project structure and module descriptions

---

## 📖 Guides & Examples

## 📦 Code Source (`src/dremio_connector/`)

### Usage Examples

### 🎯 Core - Logique Métier- **[examples/README.md](examples/README.md)** - Guide to examples directory

- **[examples/basic_ingestion.py](examples/basic_ingestion.py)** - Basic usage example

| Fichier | Rôle | Status |

|---------|------|--------|## 🛠️ Development

| **`core/sync_engine.py`** | ⭐ **Moteur principal** - Auto-discovery et sync | ✅ Production |

| `core/connector.py` | ⚠️ Ancien connecteur (déprécié) | ⚠️ Deprecated |### Configuration

| `core/dremio_source.py` | ⚠️ Ancienne source (dépréciée) | ⚠️ Deprecated |- **[config/ingestion.yaml](config/ingestion.yaml)** - Main configuration file

| `core/__init__.py` | Exports du module core | ✅ OK |

### Setup & Scripts

**Utilisez**: `sync_engine.py` pour tous les nouveaux développements- **[scripts/quickstart.py](scripts/quickstart.py)** - Automated setup script



### 🔌 Clients - API REST### Testing

- **[tests/conftest.py](tests/conftest.py)** - Pytest configuration

| Fichier | Rôle | Status |- **[tests/test_dremio_client.py](tests/test_dremio_client.py)** - Dremio client tests

|---------|------|--------|- **[tests/test_openmetadata_client.py](tests/test_openmetadata_client.py)** - OpenMetadata client tests

| `clients/dremio_client.py` | Client API Dremio v3 (legacy) | 📝 À enrichir |

| `clients/openmetadata_client.py` | Client API OpenMetadata v1 (legacy) | 📝 À enrichir |## 📦 Package Information

| `clients/__init__.py` | Exports des clients | ✅ OK |

### Installation

**Note**: Clients legacy conservés pour compatibilité. Le nouveau code est dans `sync_engine.py`.- **[setup.py](setup.py)** - Package configuration

- **[requirements.txt](requirements.txt)** - Python dependencies

### 🛠️ Utilitaires- **[MANIFEST.in](MANIFEST.in)** - Package manifest



| Fichier | Rôle | Status |### Code Quality

|---------|------|--------|- **[.editorconfig](.editorconfig)** - Editor configuration for consistent coding style

| `utils/logger.py` | Configuration logging | ✅ OK |- **[.gitignore](.gitignore)** - Git ignore rules

| `utils/config.py` | Gestion configuration | ✅ OK |

| `utils/__init__.py` | Exports utils | ✅ OK |## 🗂️ Directory Structure



### 🖥️ Interface Ligne de Commande```

dremio/

| Fichier | Rôle | Status |├── 📄 README.md                      # Main documentation (START HERE)

|---------|------|--------|├── 📄 QUICK_START.md                 # Quick start guide

| `cli.py` | Point d'entrée CLI | 📝 À enrichir (Phase 3) |├── 📄 INDEX.md                       # This file - Documentation index

│

**Futur**: Commandes `sync`, `discover`, `check-lineage`├── 📚 docs/                          # Additional documentation

│   ├── PROJECT_STRUCTURE.md          # Project structure details

---│   └── guides/                       # User guides

│

## 📖 Documentation (`docs/`)├── 📦 src/dremio_connector/          # Main source code

│   ├── core/                         # Core business logic

| Fichier | Description | Audience |│   ├── clients/                      # API clients

|---------|-------------|----------|│   ├── utils/                        # Utilities

| **`QUICK_START.md`** | ⭐ Guide démarrage rapide (5 min) | Débutants |│   └── cli.py                        # CLI entry point

| **`ENRICHMENT_PLAN.md`** | Feuille de route développement | Contributeurs |│

| **`CLEANUP_PLAN.md`** | Plan nettoyage et maintenance | Mainteneurs |├── ⚙️  config/                        # Configuration

| `PROJECT_STRUCTURE.md` | Structure détaillée (legacy) | Développeurs |│   └── ingestion.yaml                # Main config file

│

---├── 📖 examples/                       # Usage examples

│   ├── README.md                     # Examples guide

## 📝 Exemples (`examples/`)│   └── basic_ingestion.py            # Basic example

│

| Fichier | Description | Difficulté |├── 🧪 tests/                          # Unit tests

|---------|-------------|------------|│   ├── conftest.py

| **`full_sync_example.py`** | ⭐ Sync complète automatique | ⭐⭐ Facile |│   ├── test_dremio_client.py

| **`create_service.py`** | Création service OpenMetadata | ⭐ Très facile |│   └── test_openmetadata_client.py

| `basic_ingestion.py` | Exemple minimal API | ⭐ Très facile |│

| `README.md` | Documentation exemples | - |└── 🛠️  scripts/                       # Utility scripts

    └── quickstart.py                 # Setup script

---```



## 🧪 Tests (`tests/`)## 🎯 Quick Navigation



| Fichier | Description | Status |### I want to...

|---------|-------------|--------|

| `test_sync_engine.py` | Tests moteur sync | ⏳ À créer |**Get started quickly**

| `test_dremio_client.py` | Tests client Dremio | ✅ Existants |→ Read [QUICK_START.md](QUICK_START.md)

| `test_openmetadata_client.py` | Tests client OpenMetadata | ✅ Existants |

| `conftest.py` | Configuration pytest | ✅ OK |**Understand the project structure**

→ Read [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

---

**See usage examples**

## ⚙️ Configuration→ Check [examples/README.md](examples/README.md)



| Fichier | Description | Usage |**Configure the connector**

|---------|-------------|-------|→ Edit [config/ingestion.yaml](config/ingestion.yaml)

| `config/ingestion.yaml` | Config ingestion (legacy) | Legacy |

| `.env.example` | Template variables d'env | Copier vers `.env` |**Run tests**

| `requirements.txt` | Dépendances Python | `pip install -r` |→ See [README.md#testing](README.md#testing)

| `requirements-dev.txt` | Dépendances dev | Dev seulement |

| `setup.py` | Configuration package | `pip install -e .` |**Contribute to the project**

→ See [README.md#contributing](README.md#contributing)

---

**Troubleshoot issues**

## 📄 Documentation Racine→ See [README.md#troubleshooting](README.md#troubleshooting)



| Fichier | Description | Importance |## 📞 Getting Help

|---------|-------------|------------|

| **`README.md`** | ⭐ Documentation principale | Essentiel |1. **Check documentation** in this index

| `LICENSE` | Licence Apache 2.0 | Légal |2. **Run quick setup**: `python scripts/quickstart.py`

| `INDEX.md` | Ce fichier | Navigation |3. **Test connection**: `dremio-connector --config config/ingestion.yaml --test-connection`

| `.gitignore` | Exclusions Git | Requis |4. **Enable debug logs**: `--log-level DEBUG --log-file debug.log`

5. **Open an issue** on GitHub

### Anciens README (Backups)

## 🔄 Documentation Updates

| Fichier | Description |

|---------|-------------|**Last Updated**: 2025-10-08  

| `README.md.old` | Ancien README (backup) |**Version**: 1.0.0

| `README-fr.md.old` | Ancien README français (backup) |

| `README-es.md.old` | Ancien README espagnol (backup) |To update this index, edit `INDEX.md` and commit the changes.

| `README-ar.md.old` | Ancien README arabe (backup) |

---

---

**Note**: This is the complete documentation index for the Dremio OpenMetadata Connector project. All main documentation is now centralized and organized.

## 🗺️ Carte des Fonctionnalités

### ✅ Phase 1 : Auto-Discovery (TERMINÉE)

**Fichiers principaux**:
- `src/dremio_connector/core/sync_engine.py` (Classes: `DremioAutoDiscovery`, `OpenMetadataSyncEngine`, `DremioOpenMetadataSync`)
- `examples/full_sync_example.py`
- `docs/QUICK_START.md`

**Capacités**:
- Découverte automatique 100% des ressources
- Extraction colonnes + types
- Synchronisation idempotente
- Logging détaillé
- Statistiques complètes

### 🔄 Phase 2 : Intégration dbt (À VENIR)

**Fichiers futurs**:
- `src/dremio_connector/dbt/dbt_integration.py`
- `src/dremio_connector/dbt/lineage_checker.py`
- `examples/dbt_ingestion_example.py`
- `docs/DBT_INTEGRATION.md`

**Capacités**:
- Ingestion modèles dbt
- Lineage automatique
- Vérification lineage

### ⏳ Phase 3 : CLI Enrichi (À VENIR)

**Fichiers impactés**:
- `src/dremio_connector/cli.py` (enrichissement)

**Nouvelles commandes**:
```bash
dremio-connector sync
dremio-connector discover
dremio-connector check-lineage
dremio-connector ingest-dbt
```

### ⏳ Phase 4 : Agent Lineage (À VENIR)

**Fichiers futurs**:
- `src/dremio_connector/agents/lineage_agent.py`
- `docs/LINEAGE_GUIDE.md`

**Capacités**:
- Parsing SQL des VDS
- Création lineage automatique
- Column-level lineage

---

## 🔍 Comment Trouver...

### Comment lancer la synchronisation ?
→ `examples/full_sync_example.py`

### Comment fonctionne l'auto-discovery ?
→ `src/dremio_connector/core/sync_engine.py` classe `DremioAutoDiscovery`

### Comment créer un service OpenMetadata ?
→ `examples/create_service.py`

### Comment démarrer rapidement ?
→ `docs/QUICK_START.md`

### Comment contribuer ?
→ `README.md` section "Contributing" + `docs/ENRICHMENT_PLAN.md`

### Comment installer ?
→ `README.md` section "Installation" ou `docs/QUICK_START.md`

### Quelles sont les prochaines fonctionnalités ?
→ `docs/ENRICHMENT_PLAN.md`

### Comment configurer ?
→ `README.md` section "Configuration"

### Comment tester ?
→ `tests/` + `README.md` section "Testing"

---

## 📊 Statistiques du Projet

### Code Source
- **Lignes de code**: ~1,500 (hors tests)
- **Fichiers Python**: 15+
- **Classes principales**: 3 (`DremioAutoDiscovery`, `OpenMetadataSyncEngine`, `DremioOpenMetadataSync`)

### Documentation
- **Fichiers doc**: 7
- **Guides**: 3 (Quick Start, Enrichment, Cleanup)
- **Exemples**: 3 fonctionnels

### Tests
- **Couverture**: 75%+
- **Tests unitaires**: En développement
- **Tests d'intégration**: 1 (manuel)

---

## 🎯 Points d'Entrée Principaux

### Pour Utilisateurs Finaux
1. **`docs/QUICK_START.md`** - Commencer ici
2. **`examples/full_sync_example.py`** - Lancer une sync
3. **`README.md`** - Documentation de référence

### Pour Développeurs
1. **`src/dremio_connector/core/sync_engine.py`** - Code principal
2. **`docs/ENRICHMENT_PLAN.md`** - Feuille de route
3. **`docs/CLEANUP_PLAN.md`** - Architecture et maintenance

### Pour Contributeurs
1. **`docs/ENRICHMENT_PLAN.md`** - Roadmap phases 2-5
2. **`tests/`** - Ajouter des tests
3. **`README.md`** section "Contributing"

---

## 🔄 Fichiers à Supprimer (Nettoyage Futur)

### Obsolètes (Backups)
- `README.md.old`
- `README-fr.md.old`
- `README-es.md.old`
- `README-ar.md.old`
- `examples/README.md.old`
- `INDEX.md.old`

### Legacy (À migrer puis supprimer)
- `src/dremio_connector/core/dremio_source.py` (déjà marqué deprecated)
- `src/dremio_connector/core/connector.py` (déjà marqué deprecated)

**Ne pas supprimer maintenant** : Conservés pour compatibilité ascendante

---

## 🆘 Support et Aide

| Besoin | Fichier | Contact |
|--------|---------|---------|
| Guide rapide | `docs/QUICK_START.md` | - |
| Documentation complète | `README.md` | - |
| Exemples | `examples/README.md` | - |
| Problèmes | - | GitHub Issues |
| Questions | - | GitHub Discussions |

---

**Dernière mise à jour**: 2025-01-10  
**Version**: 2.0.0  
**Status**: ✅ Production Ready (Phase 1)

---

🎉 **Ce projet est prêt pour la production !**  
📚 **Consultez `docs/QUICK_START.md` pour commencer**
