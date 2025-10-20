# 🚀 Dremio Connector pour OpenMetadata - Agent 4-in-1

## 📌 Vue d'ensemble

Connecteur personnalisé **unifié** pour OpenMetadata qui intègre **4 capacités** dans un seul agent :

### ✨ Les 4 Capacités

| # | Capacité | Description |
|---|----------|-------------|
| 1️⃣ | **Metadata** | Extraction complète : Databases → Schemas → Tables → Columns |
| 2️⃣ | **Profiling** | Statistiques avec sampling configurable (min, max, avg, distribution, nulls) |
| 3️⃣ | **Auto-Classification** | Tags automatiques PII/Sensitive/Financial sur les colonnes |
| 4️⃣ | **DBT Integration** | Enrichissement avec descriptions et tags DBT |

## 🎯 Avantages

✅ **Un seul agent** au lieu de 4 séparés  
✅ **Configuration 100% UI** - Pas de fichiers YAML  
✅ **Optimisé** - Profiling avec sampling paramétrable  
✅ **Sécurisé** - Classification automatique des données sensibles  
✅ **Documenté** - Intégration DBT native  

## ⚡ Quick Start

### 1. Démarrer l'environnement

```bash
git clone https://github.com/Monsau/openmetadata-dremio-connector.git
cd openmetadata-dremio-connector
docker compose up -d --build
```

### 2. Accéder à OpenMetadata

- URL : http://localhost:8585
- Login : `admin` / `admin`

### 3. Configurer le service Dremio

**Settings → Databases → + Add Database Service → Dremio**

**Connection Options :**

```json
{
  "url": "http://host.docker.internal:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 10000
}
```

### 4. Lancer l'ingestion

**Service Dremio → Ingestions → + Add Ingestion → Metadata → Run**

C'est tout ! 🎉

## 📊 Configuration

### Paramètres Obligatoires

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123"
}
```

### Paramètres Optionnels

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `profileSampleRows` | integer | Nb de lignes pour profiling | null (toutes) |
| `dbtEnabled` | boolean | Activer DBT | false |
| `dbtCatalogPath` | string | Chemin catalog.json | - |
| `dbtManifestPath` | string | Chemin manifest.json | - |
| `dbtRunResultsPath` | string | Chemin run_results.json | - |

### Exemples Complets

Voir [CONFIGURATION_EXAMPLES.md](docs/CONFIGURATION_EXAMPLES.md)

## 🏷️ Auto-Classification

Le connector détecte automatiquement 8 types de données sensibles :

### PII (Personally Identifiable Information)

- 📧 **Email** : `email`, `mail`, `e_mail`, `courriel`
- 📞 **Phone** : `phone`, `tel`, `mobile`, `telephone`
- 👤 **Name** : `first_name`, `last_name`, `full_name`, `nom`, `prenom`
- 🏠 **Address** : `address`, `street`, `city`, `postal`, `adresse`
- 🆔 **ID** : `ssn`, `social_security`, `passport`, `license`

### Sensitive

- 🔐 **Credential** : `password`, `token`, `secret`, `key`, `credential`

### Financial

- 💳 **CreditCard** : `credit_card`, `cc_number`, `card_number`
- 🏦 **BankAccount** : `account`, `iban`, `swift`, `bank_account`

**Résultat** : Tags automatiquement appliqués dans OpenMetadata UI

## 📈 Profiling avec Sampling

### Pourquoi ?

Profiler des tables de millions de lignes peut prendre des heures. Le sampling analyse seulement un échantillon.

### Configuration

```json
{
  "profileSampleRows": 50000
}
```

### SQL Généré

**Sans sampling :**
```sql
SELECT COUNT(*), AVG(price), MIN(price), MAX(price) FROM sales
```

**Avec sampling (50K lignes) :**
```sql
SELECT COUNT(*), AVG(price), MIN(price), MAX(price) 
FROM (SELECT * FROM sales LIMIT 50000)
```

### Recommandations

| Taille Table | Sample |
|--------------|--------|
| < 100K | Pas de sampling |
| 100K - 1M | 10,000 |
| 1M - 10M | 50,000 |
| > 10M | 100,000+ |

## 🔧 Intégration DBT

### Prérequis

1. Projet DBT connecté à Dremio
2. Fichiers générés :
   ```bash
   dbt compile          # → manifest.json
   dbt docs generate    # → catalog.json
   ```

### Configuration

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/target/manifest.json"
}
```

### Ce qui est enrichi

✅ Descriptions des tables (de `models/*.yml`)  
✅ Tags DBT (convertis en `DBT.tag_name`)  
✅ Descriptions des colonnes  
✅ Matching automatique par nom de table  

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [CONFIGURATION.md](docs/CONFIGURATION.md) | Guide complet de configuration |
| [CONFIGURATION_EXAMPLES.md](docs/CONFIGURATION_EXAMPLES.md) | Exemples copy/paste |
| [DBT_INTEGRATION.md](docs/DBT_INTEGRATION.md) | Guide détaillé DBT |
| [CLASSIFICATION_GUIDE.md](docs/CLASSIFICATION_GUIDE.md) | Patterns de classification |
| [PROFILING_GUIDE.md](docs/PROFILING_GUIDE.md) | Guide profiling |

## 🏗️ Architecture

```
OpenMetadata Ingestion
  │
  └─> DremioConnector (4-in-1)
       │
       ├─> 1. Metadata Discovery
       │    └─> yield_database()
       │    └─> yield_database_schema()
       │    └─> yield_table()
       │
       ├─> 2. Profiling (avec sampling)
       │    └─> get_profile_metrics()
       │    └─> _profile_column()
       │
       ├─> 3. Auto-Classification
       │    └─> yield_tag()
       │    └─> get_column_tag_labels()
       │
       └─> 4. DBT Enrichment
            └─> _load_dbt_catalog()
            └─> _load_dbt_manifest()
            └─> _enrich_with_dbt()
```

## 🛠️ Développement

### Structure du Code

```
dremio_connector/
├── dremio_source.py          # Agent 4-in-1 principal
├── core/
│   └── sync_engine.py        # Client Dremio REST API
├── manifest.json             # Déclaration du connector
└── __init__.py
```

### Tester localement

```bash
# Rebuild l'image
docker compose build --no-cache ingestion

# Redémarrer
docker compose up -d

# Vérifier les logs
docker logs -f openmetadata_ingestion
```

### Modifier la configuration

```bash
# Éditer
vim dremio_connector/dremio_source.py

# Rebuild et tester
docker compose build ingestion && docker compose up -d ingestion
```

## 🐛 Troubleshooting

### Profiling trop lent

```json
{
  "profileSampleRows": 1000  // Réduire le sample
}
```

### Tags ne s'affichent pas

✅ Vérifier : **Enable Auto Classification** coché dans l'ingestion  
✅ Vérifier les logs : `✅ email: Applied 1 tags`  
✅ Rafraîchir la page de la table  

### DBT files not found

```bash
# Vérifier dans le container
docker exec -it openmetadata_ingestion ls -la /opt/dbt/target/

# Monter le volume si nécessaire
# docker-compose.yml
volumes:
  - /local/dbt/project/target:/opt/dbt/target:ro
```

### Connection refused

```bash
# Tester la connexion
docker exec openmetadata_ingestion curl http://host.docker.internal:9047/apiv2/server_status
```

## 📊 Métriques de Performance

### Test sur 8 sources Dremio

| Métrique | Sans Sampling | Avec 10K Sample |
|----------|---------------|-----------------|
| Durée totale | ~45 min | ~5 min |
| Tables profilées | 16 | 16 |
| Colonnes analysées | 127 | 127 |
| Tags appliqués | 23 | 23 |

**Gain : 90% de réduction du temps** avec sampling ! 🚀

## 🆘 Support

- 📖 [Documentation Complète](docs/)
- 🐛 [Issues GitHub](https://github.com/Monsau/openmetadata-dremio-connector/issues)
- 💬 [OpenMetadata Slack](https://slack.open-metadata.org/)

## 📜 Licence

Voir [LICENSE](LICENSE)

---

**Agent 4-in-1** : Metadata + Profiling + Classification + DBT  
**Configuration** : 100% via UI, pas de YAML  
**Performance** : Sampling intelligent pour grandes tables  
**Sécurité** : Auto-classification des données sensibles  

🚀 **Ready for Production !**
