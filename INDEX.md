# Dremio OpenMetadata Connector - Documentation Index

## 📚 Main Documentation

### Getting Started
1. **[README.md](README.md)** - Main documentation with overview, installation, and usage
2. **[QUICK_START.md](QUICK_START.md)** - Visual quick start guide with step-by-step instructions

### Language Versions
- **[README-fr.md](README-fr.md)** - Documentation en français
- **[README-es.md](README-es.md)** - Documentación en español
- **[README-ar.md](README-ar.md)** - التوثيق بالعربية

## 🔧 Technical Documentation

### Project Structure & Architecture
- **[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Detailed project structure and module descriptions
- **[RESTRUCTURATION_SUMMARY.md](RESTRUCTURATION_SUMMARY.md)** - Summary of the restructuring with statistics

### Migration & Upgrade
- **[docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)** - Guide for migrating from legacy structure

## 📖 Guides & Examples

### Usage Examples
- **[examples/README.md](examples/README.md)** - Guide to examples directory
- **[examples/basic_ingestion.py](examples/basic_ingestion.py)** - Basic usage example

## 🛠️ Development

### Configuration
- **[config/ingestion.yaml](config/ingestion.yaml)** - Main configuration file

### Setup & Scripts
- **[scripts/quickstart.py](scripts/quickstart.py)** - Automated setup script

### Testing
- **[tests/conftest.py](tests/conftest.py)** - Pytest configuration
- **[tests/test_dremio_client.py](tests/test_dremio_client.py)** - Dremio client tests
- **[tests/test_openmetadata_client.py](tests/test_openmetadata_client.py)** - OpenMetadata client tests

## 📦 Package Information

### Installation
- **[setup.py](setup.py)** - Package configuration
- **[requirements.txt](requirements.txt)** - Python dependencies
- **[MANIFEST.in](MANIFEST.in)** - Package manifest

### Code Quality
- **[.editorconfig](.editorconfig)** - Editor configuration for consistent coding style
- **[.gitignore](.gitignore)** - Git ignore rules

## 🗂️ Directory Structure

```
dremio/
├── 📄 README.md                      # Main documentation (START HERE)
├── 📄 QUICK_START.md                 # Quick start guide
├── 📄 INDEX.md                       # This file - Documentation index
├── 📄 RESTRUCTURATION_SUMMARY.md     # Restructuring summary
│
├── 📚 docs/                          # Additional documentation
│   ├── PROJECT_STRUCTURE.md          # Project structure details
│   ├── MIGRATION_GUIDE.md            # Migration guide
│   └── guides/                       # User guides
│
├── 📦 src/dremio_connector/          # Main source code
│   ├── core/                         # Core business logic
│   ├── clients/                      # API clients
│   ├── utils/                        # Utilities
│   └── cli.py                        # CLI entry point
│
├── ⚙️  config/                        # Configuration
│   └── ingestion.yaml                # Main config file
│
├── 📖 examples/                       # Usage examples
│   ├── README.md                     # Examples guide
│   └── basic_ingestion.py            # Basic example
│
├── 🧪 tests/                          # Unit tests
│   ├── conftest.py
│   ├── test_dremio_client.py
│   └── test_openmetadata_client.py
│
└── 🛠️  scripts/                       # Utility scripts
    └── quickstart.py                 # Setup script
```

## 🎯 Quick Navigation

### I want to...

**Get started quickly**
→ Read [QUICK_START.md](QUICK_START.md)

**Understand the project structure**
→ Read [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

**Migrate from old structure**
→ Read [docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)

**See usage examples**
→ Check [examples/README.md](examples/README.md)

**Configure the connector**
→ Edit [config/ingestion.yaml](config/ingestion.yaml)

**Run tests**
→ See [README.md#testing](README.md#testing)

**Contribute to the project**
→ See [README.md#contributing](README.md#contributing)

**Troubleshoot issues**
→ See [README.md#troubleshooting](README.md#troubleshooting)

## 📞 Getting Help

1. **Check documentation** in this index
2. **Run quick setup**: `python scripts/quickstart.py`
3. **Test connection**: `dremio-connector --config config/ingestion.yaml --test-connection`
4. **Enable debug logs**: `--log-level DEBUG --log-file debug.log`
5. **Open an issue** on GitHub

## 🔄 Documentation Updates

**Last Updated**: 2025-10-08  
**Version**: 1.0.0

To update this index, edit `INDEX.md` and commit the changes.

---

**Note**: This is the complete documentation index for the Dremio OpenMetadata Connector project. All main documentation is now centralized and organized.
