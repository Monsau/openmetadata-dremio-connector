# 🎯 Quick Reference - Dremio Connector

## 📦 Installation Rapide

```bash
# 1. Cloner et entrer dans le projet
cd c:/projets/dremio

# 2. Démarrage automatisé (recommandé)
python scripts/quickstart.py

# OU manuel
python -m venv venv_dremio
venv_dremio\Scripts\activate
pip install -e .
```

## ⚙️ Configuration

Éditer `config/ingestion.yaml` :
```yaml
source:
  serviceConnection:
    config:
      connectionOptions:
        dremioHost: localhost        # 🔧 Modifier ici
        dremioPort: "9047"
        dremioUsername: admin        # 🔧 Modifier ici
        dremioPassword: admin123     # 🔧 Modifier ici

workflowConfig:
  openMetadataServerConfig:
    hostPort: http://localhost:8585/api  # 🔧 Modifier ici
    securityConfig:
      jwtToken: "your-token-here"        # 🔧 Modifier ici
```

## 🚀 Utilisation

### CLI (Recommandé)
```bash
# Test de connexion
dremio-connector --config config/ingestion.yaml --test-connection

# Ingestion complète
dremio-connector --config config/ingestion.yaml

# Avec logs détaillés
dremio-connector --config config/ingestion.yaml --log-level DEBUG --log-file ingestion.log
```

### Programmatique
```python
from src.dremio_connector.core.dremio_source import DremioSource

config = {
    'dremioHost': 'localhost',
    'dremioPort': 9047,
    'dremioUsername': 'admin',
    'dremioPassword': 'admin123',
    'openMetadataServerConfig': {
        'hostPort': 'http://localhost:8585/api',
        'securityConfig': {'jwtToken': 'your-token'}
    },
    'serviceName': 'dremio-service'
}

connector = DremioSource(config)
results = connector.ingest_metadata()
print(results)
```

## 📁 Structure du Projet

```
dremio/
├── 📦 src/dremio_connector/      ← Code principal
│   ├── core/                     ← Logique métier
│   ├── clients/                  ← Clients API
│   ├── utils/                    ← Utilitaires
│   └── cli.py                    ← Interface CLI
│
├── ⚙️  config/                    ← Configuration
│   └── ingestion.yaml
│
├── 📖 examples/                   ← Exemples d'utilisation
│   ├── basic_ingestion.py
│   └── README.md
│
├── 🧪 tests/                      ← Tests unitaires
│   ├── test_dremio_client.py
│   └── test_openmetadata_client.py
│
├── 📚 docs/                       ← Documentation
│   ├── PROJECT_STRUCTURE.md
│   └── MIGRATION_GUIDE.md
│
├── 🛠️  scripts/                   ← Scripts utilitaires
│   └── quickstart.py
│
├── 📄 setup.py                    ← Configuration package
├── 📋 requirements.txt            ← Dépendances
└── 📖 README.md                   ← Documentation principale
```

## 🧪 Tests

```bash
# Exécuter tous les tests
pytest tests/

# Avec coverage
pytest --cov=src/dremio_connector tests/

# Test spécifique
pytest tests/test_dremio_client.py -v
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Documentation principale |
| [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Structure détaillée |
| [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) | Guide de migration |
| [RESTRUCTURATION_SUMMARY.md](RESTRUCTURATION_SUMMARY.md) | Résumé de la restructuration |
| [examples/README.md](examples/README.md) | Guide des exemples |

## 🔍 Commandes Utiles

```bash
# Installation
pip install -e .                          # Mode développement
pip install -e ".[dev]"                   # Avec outils dev
pip install -e ".[database,search]"       # Avec extras

# Tests
pytest tests/                             # Tous les tests
pytest --cov                              # Avec couverture
pytest -v                                 # Verbose

# Linting
black src/ tests/                         # Formatage
flake8 src/ tests/                        # Lint
mypy src/                                 # Type checking

# CLI
dremio-connector --help                   # Aide
dremio-connector --config <file>          # Ingestion
dremio-connector --test-connection        # Test
dremio-connector --log-level DEBUG        # Debug
```

## 🆘 Dépannage

### Problème : Import errors
```bash
pip install -e .
```

### Problème : CLI non trouvé
```bash
pip install -e .
# OU
python -m dremio_connector.cli --config config/ingestion.yaml
```

### Problème : Connexion Dremio échoue
- Vérifier que Dremio est démarré (localhost:9047)
- Vérifier username/password dans config
- Tester manuellement : http://localhost:9047

### Problème : Connexion OpenMetadata échoue
- Vérifier que OpenMetadata est démarré (localhost:8585)
- Générer un nouveau JWT token dans OpenMetadata UI
- Vérifier le token dans config/ingestion.yaml

## 📞 Support

- **Issues** : GitHub Issues
- **Documentation** : Dossier `docs/`
- **Exemples** : Dossier `examples/`

## ✅ Checklist de Démarrage

- [ ] Environnement virtuel créé
- [ ] Dépendances installées (`pip install -e .`)
- [ ] Configuration éditée (`config/ingestion.yaml`)
- [ ] Dremio accessible (http://localhost:9047)
- [ ] OpenMetadata accessible (http://localhost:8585)
- [ ] JWT token généré
- [ ] Test de connexion réussi
- [ ] Première ingestion lancée

## 🎉 Commencer Maintenant !

```bash
# Démarrage rapide en 3 commandes
cd c:/projets/dremio
python scripts/quickstart.py
dremio-connector --config config/ingestion.yaml --test-connection
```

---

**Version** : 1.0.0  
**Dernière mise à jour** : 2025-10-08  
**Statut** : ✅ Production Ready
