# 🔧 Intégration DBT dans le Connector Dremio

## 📋 Vue d'ensemble

Le connector Dremio est maintenant un **agent 4-en-1** qui combine :

1. ✅ **Metadata Ingestion** - Collecte des métadonnées Dremio
2. ✅ **Profiling** - Statistiques sur les données avec sampling configurable
3. ✅ **Auto-Classification** - Tags PII/Sensitive/Financial automatiques
4. ✅ **DBT Integration** - Enrichissement avec les métadonnées DBT

## 🚀 Configuration

Toute la configuration se fait via `connectionOptions` dans l'UI OpenMetadata - **AUCUN fichier YAML requis**.

### Configuration Complète

```json
{
  "url": "http://dremio-server:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 10000,
  "dbtEnabled": true,
  "dbtCatalogPath": "/path/to/dbt/target/catalog.json",
  "dbtManifestPath": "/path/to/dbt/target/manifest.json",
  "dbtRunResultsPath": "/path/to/dbt/target/run_results.json"
}
```

### Paramètres

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `url` | string | ✅ Oui | URL du serveur Dremio |
| `username` | string | ✅ Oui | Nom d'utilisateur Dremio |
| `password` | string | ✅ Oui | Mot de passe Dremio |
| `profileSampleRows` | integer | ❌ Non | Nombre de lignes pour le profiling (défaut: toutes) |
| `dbtEnabled` | boolean | ❌ Non | Activer l'intégration DBT (défaut: false) |
| `dbtCatalogPath` | string | ⚠️ Si DBT | Chemin vers catalog.json |
| `dbtManifestPath` | string | ⚠️ Si DBT | Chemin vers manifest.json |
| `dbtRunResultsPath` | string | ❌ Non | Chemin vers run_results.json (optionnel) |

## 📊 Profiling avec Sampling

### Pourquoi le Sampling ?

Le profiling sur de grandes tables peut être très lent. Le sampling permet d'analyser seulement un sous-ensemble de données.

### Configuration

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 10000
}
```

### Comportement

- **Sans `profileSampleRows`** : Analyse TOUTES les lignes de chaque table
  ```sql
  SELECT COUNT(*), AVG(col), ... FROM table
  ```

- **Avec `profileSampleRows: 10000`** : Analyse seulement 10,000 lignes
  ```sql
  SELECT COUNT(*), AVG(col), ... FROM (SELECT * FROM table LIMIT 10000)
  ```

### Recommandations

| Taille de la table | Sample recommandé |
|-------------------|-------------------|
| < 100K lignes | Pas de sampling (toutes les lignes) |
| 100K - 1M lignes | 10,000 - 50,000 lignes |
| 1M - 10M lignes | 50,000 - 100,000 lignes |
| > 10M lignes | 100,000 - 500,000 lignes |

## 🔧 Intégration DBT

### Fichiers DBT Requis

DBT génère plusieurs fichiers JSON dans le dossier `target/` :

1. **catalog.json** ✅ Requis
   - Schéma des tables et colonnes
   - Métadonnées des modèles

2. **manifest.json** ✅ Requis
   - Descriptions des modèles
   - Tags DBT
   - Relations entre modèles

3. **run_results.json** ❌ Optionnel
   - Résultats d'exécution
   - Statuts des tests

### Génération des Fichiers DBT

```bash
# Dans votre projet DBT
cd /path/to/dbt/project

# Générer les fichiers
dbt compile  # Génère manifest.json
dbt docs generate  # Génère catalog.json
dbt run  # Génère run_results.json (optionnel)
```

### Configuration dans OpenMetadata

#### Via l'UI

1. Aller dans **Settings → Services → Database → Dremio**
2. Cliquer sur **Edit Service**
3. Dans **Connection Options**, ajouter :

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/target/manifest.json",
  "dbtRunResultsPath": "/opt/dbt/target/run_results.json"
}
```

#### Avec Docker Volume

Si vous utilisez Docker, montez le dossier DBT target :

```yaml
# docker-compose.yml
services:
  openmetadata_ingestion:
    volumes:
      - /local/dbt/project/target:/opt/dbt/target:ro
```

Puis configurez les chemins :

```json
{
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/target/manifest.json"
}
```

### Ce qui est Enrichi

Quand DBT est activé, le connector enrichit automatiquement :

#### 1. Descriptions des Tables

```yaml
# DBT model: models/customers.yml
models:
  - name: customers
    description: "Aggregated customer information with lifetime value"
```

➡️ La description DBT remplace la description Dremio dans OpenMetadata

#### 2. Tags DBT

```yaml
# DBT model
models:
  - name: customers
    tags:
      - pii
      - marketing
      - production
```

➡️ Les tags deviennent : `DBT.pii`, `DBT.marketing`, `DBT.production`

#### 3. Descriptions des Colonnes

```yaml
# DBT model
models:
  - name: customers
    columns:
      - name: customer_id
        description: "Unique identifier for customer"
      - name: lifetime_value
        description: "Total revenue from customer (USD)"
```

➡️ Les descriptions de colonnes sont ajoutées dans OpenMetadata

### Matching des Tables

Le connector fait le matching entre tables Dremio et modèles DBT par **nom** :

- Table Dremio : `HR.PUBLIC.employees`
- Modèle DBT : `model.my_project.employees`
- ✅ Match sur le nom `employees`

## 🔍 Logs de Debug

### Vérifier la Configuration

```bash
# Logs de l'ingestion
docker logs openmetadata_ingestion -f

# Chercher ces messages :
# 📊 Profiling sample rows: 10000
# 🔧 DBT enabled: True
# 📖 Loading DBT catalog from: /opt/dbt/target/catalog.json
# ✅ DBT catalog loaded: 25 nodes
```

### Vérifier l'Enrichissement

```bash
# Chercher ces messages :
# 🔧 Enriching HR.PUBLIC.employees with DBT model: model.my_project.employees
#   ✅ Added DBT description
#   ✅ Added 3 DBT tags
#   ✅ Added description for column: customer_id
```

## 📝 Exemple Complet

### 1. Projet DBT

```yaml
# models/schema.yml
version: 2

models:
  - name: customer_metrics
    description: "Customer-level metrics for analytics"
    tags:
      - pii
      - analytics
      - production
    columns:
      - name: customer_id
        description: "Unique customer identifier"
        tests:
          - unique
          - not_null
      - name: email
        description: "Customer email address"
        tags:
          - pii_email
      - name: total_orders
        description: "Total number of orders placed"
```

### 2. Génération DBT

```bash
cd /my/dbt/project
dbt compile
dbt docs generate
```

### 3. Configuration OpenMetadata

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 50000,
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/target/manifest.json"
}
```

### 4. Résultat dans OpenMetadata

La table `customer_metrics` aura :

- ✅ Description du modèle DBT
- ✅ Tags : `DBT.pii`, `DBT.analytics`, `DBT.production`
- ✅ Descriptions de colonnes
- ✅ Tags auto-classification : `PII.Email` sur la colonne `email`
- ✅ Profiling sur 50,000 lignes sample

## 🎯 Avantages

### Sans DBT (3-in-1)
```
Dremio → OpenMetadata
  ├─ Métadonnées basiques
  ├─ Auto-classification PII
  └─ Profiling
```

### Avec DBT (4-in-1)
```
Dremio + DBT → OpenMetadata
  ├─ Métadonnées basiques (Dremio)
  ├─ Descriptions enrichies (DBT)
  ├─ Tags métier (DBT)
  ├─ Tags techniques (Auto-classification)
  └─ Profiling optimisé (Sampling)
```

## 🔧 Troubleshooting

### DBT Files Not Found

```bash
# Vérifier que les fichiers existent
ls -la /opt/dbt/target/
# catalog.json, manifest.json doivent être présents

# Vérifier les permissions
chmod 644 /opt/dbt/target/*.json
```

### No Tables Matched

```bash
# Vérifier les noms dans manifest.json
cat /opt/dbt/target/manifest.json | jq '.nodes | keys'

# Vérifier les noms dans Dremio
SELECT * FROM sys.tables WHERE table_schema = 'PUBLIC'
```

### Profiling Too Slow

```bash
# Réduire le sample
"profileSampleRows": 1000  # Au lieu de 100000

# Ou désactiver le profiling
# Ne cocher que "Metadata" dans l'ingestion
```

## 📚 Ressources

- [Documentation DBT](https://docs.getdbt.com/)
- [OpenMetadata DBT Integration](https://docs.open-metadata.org/connectors/ingestion/workflows/dbt)
- [Dremio REST API](https://docs.dremio.com/software/rest-api/)

---

**Agent 4-in-1** : Metadata + Profiling + Classification + DBT 🚀
