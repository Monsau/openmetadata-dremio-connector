# 🔄 Guide de Ré-ingestion - Structure Corrigée

**Date:** 20 octobre 2025  
**Status:** ⚠️ Code déployé mais ingestion non relancée

---

## ⚠️ Problème Actuel

L'interface OpenMetadata montre encore **l'ancienne structure** :
```
staging (Database)
└── default (Schema - FICTIF)
    └── staging_metadata (Table - FICTIVE)
        ├── source_id (VARCHAR)
        ├── source_name (VARCHAR)
        ├── source_type (VARCHAR)
        └── created_at (TIMESTAMP)
```

**Raison :** L'ingestion a été exécutée AVANT le déploiement du code corrigé.

---

## ✅ Code Déployé (Vérifié)

Le nouveau code qui découvre la **vraie structure Dremio** est bien déployé dans le conteneur :
- ✅ `get_database_schema_names()` - Découvre les vrais schémas
- ✅ `get_tables_name_and_type()` - Découvre les vraies tables
- ✅ `yield_table()` - Récupère les vraies colonnes
- ✅ `_map_dremio_type_to_om()` - Mappe les types Dremio

---

## 🎯 Solution : Relancer l'Ingestion

### **Option 1 : Depuis l'Interface OpenMetadata (Recommandé)**

1. **Ouvrir OpenMetadata :** http://localhost:8585

2. **Aller dans Settings :**
   - Cliquer sur l'icône ⚙️ en haut à droite
   - Ou aller à : Settings > Databases

3. **Trouver le service Dremio :**
   - Chercher "dremio-prod2" dans la liste
   - Cliquer dessus

4. **Aller dans Ingestions :**
   - Onglet "Ingestions" ou "Pipelines"
   - Vous verrez la liste des pipelines d'ingestion

5. **Supprimer l'ancienne ingestion :**
   - Cliquer sur les 3 points ⋮ à côté du pipeline
   - Sélectionner "Delete"
   - Confirmer

6. **Créer une nouvelle ingestion :**
   - Cliquer "Add Ingestion"
   - Type : "Metadata"
   - Configurer :
     - **Name :** `dremio-metadata-ingestion`
     - **Schedule :** Manual (ou Daily)
   - Cliquer "Next" puis "Save"

7. **Lancer l'ingestion :**
   - Cliquer sur "Run" (▶️)
   - Attendre la fin (quelques secondes)

8. **Vérifier les logs :**
   - Cliquer sur le pipeline
   - Onglet "Logs"
   - Chercher :
     ```
     🔍 Getting schemas for source: staging
     📦 Found X items in source staging
     🗂️  Schema: staging (type: CONTAINER)
     🔍 Getting tables for staging.staging
     📋 Table: stg_minio_customers
     📋 Table: stg_minio_sales
       ├─ Column: customer_id (INTEGER -> INT)
       ├─ Column: customer_name (VARCHAR -> VARCHAR)
     ```

---

### **Option 2 : Via Terminal (Avancé)**

Si vous ne trouvez pas l'option dans l'UI, forcer via API :

```powershell
# Supprimer les anciennes métadonnées
docker exec openmetadata_server curl -X DELETE "http://localhost:8585/api/v1/databases/name/dremio-prod2.staging" -H "Authorization: Bearer YOUR_TOKEN"

# Relancer l'ingestion via CLI
docker exec openmetadata_ingestion metadata ingest -c /path/to/config.yaml
```

---

### **Option 3 : Redémarrer le Service (Rapide mais brutal)**

```powershell
# Depuis c:\openmetadata-docker\
cd c:\openmetadata-docker
docker-compose restart openmetadata_server openmetadata_ingestion

# Attendre 30 secondes
Start-Sleep -Seconds 30

# Relancer l'ingestion dans l'UI
```

---

## 📊 Structure Attendue Après Ré-ingestion

```
staging (Database/Source)
├── staging (Schema RÉEL)
│   ├── stg_minio_customers (Table RÉELLE)
│   │   ├── customer_id (Type réel depuis Dremio)
│   │   ├── customer_name (Type réel depuis Dremio)
│   │   ├── email (Type réel depuis Dremio)
│   │   ├── phone (Type réel depuis Dremio)
│   │   ├── city (Type réel depuis Dremio)
│   │   └── country (Type réel depuis Dremio)
│   │
│   ├── stg_minio_sales (Table RÉELLE)
│   │   ├── sale_id (Type réel)
│   │   ├── category (Type réel)
│   │   ├── product_name (Type réel)
│   │   ├── quantity (Type réel)
│   │   ├── discount (Type réel)
│   │   ├── total_amount (Type réel)
│   │   ├── unit_price (Type réel)
│   │   ├── region (Type réel)
│   │   └── sale_date (Type réel)
│   │
│   └── (autres tables...)
│
minio_storage (Database/Source)
├── (schémas réels...)
│
PostgreSQL_BusinessDB (Database/Source)
├── (schémas réels...)
│
raw (Database/Source)
├── (schémas réels...)
│
marts (Database/Source)
└── (schémas réels...)
```

---

## 🔍 Vérification Logs

Après avoir relancé l'ingestion, vérifier les logs :

```powershell
# Logs en temps réel
docker logs openmetadata_ingestion -f

# Rechercher les lignes importantes
docker logs openmetadata_ingestion --tail 500 | Select-String "(Getting schemas|Found.*items|Schema:|Table:|Column:)"
```

**Logs attendus :**
```
🔍 Getting schemas for source: staging
📦 Found 1 items in source staging
🗂️  Schema: staging (type: CONTAINER)
🔍 Getting tables for staging.staging
📦 Found 2 items in schema staging
📋 Table: stg_minio_customers (Dremio type: PHYSICAL_DATASET -> OM type: Regular)
📋 Creating table: stg_minio_customers in staging.staging
  ├─ Column: customer_id (INTEGER -> INT)
  ├─ Column: customer_name (VARCHAR -> VARCHAR)
  ├─ Column: email (VARCHAR -> VARCHAR)
  ├─ Column: phone (VARCHAR -> VARCHAR)
  ├─ Column: city (VARCHAR -> VARCHAR)
  ├─ Column: country (VARCHAR -> VARCHAR)
📋 Table: stg_minio_sales (Dremio type: PHYSICAL_DATASET -> OM type: Regular)
📋 Creating table: stg_minio_sales in staging.staging
  ├─ Column: sale_id (INTEGER -> INT)
  ├─ Column: category (VARCHAR -> VARCHAR)
  ...
```

---

## ⚠️ Si Problème Persiste

### **1. Vérifier la connexion Dremio**

```powershell
docker exec openmetadata_ingestion python -c "
import requests
response = requests.get('http://host.docker.internal:9047/api/v3/catalog', auth=('admin', 'admin123'))
print(f'Status: {response.status_code}')
if response.status_code == 200:
    print(f'Sources: {len(response.json().get(\"data\", []))}')
"
```

### **2. Tester manuellement le connecteur**

```powershell
docker exec openmetadata_ingestion python -c "
from metadata.ingestion.source.database.dremio.dremio_source import DremioConnector
from dremio_connector.core.sync_engine import DremioAutoDiscovery

client = DremioAutoDiscovery(
    url='http://host.docker.internal:9047',
    username='admin',
    password='admin123'
)
client.authenticate()

# Test get schemas
catalog = client.get_catalog_item(['staging'])
print(f'Staging children: {len(catalog.get(\"children\", []))}')
for child in catalog.get('children', []):
    print(f'  - {child.get(\"path\")}')
"
```

### **3. Logs détaillés**

```powershell
# Activer debug dans OpenMetadata
docker exec openmetadata_ingestion sed -i 's/INFO/DEBUG/g' /opt/airflow/airflow.cfg
docker restart openmetadata_ingestion
```

---

## 📝 Checklist

- [ ] Code déployé dans conteneur (✅ FAIT)
- [ ] Conteneur redémarré (✅ FAIT)
- [ ] Ancienne ingestion supprimée
- [ ] Nouvelle ingestion créée
- [ ] Ingestion lancée
- [ ] Logs vérifiés (recherche de "Getting schemas", "Schema:", "Table:", "Column:")
- [ ] Structure vérifiée dans OpenMetadata UI
- [ ] Tables réelles visibles (stg_minio_customers, stg_minio_sales)
- [ ] Colonnes réelles visibles (customer_id, customer_name, etc.)

---

**🎯 PROCHAINE ACTION : Relancer l'ingestion depuis l'interface OpenMetadata (Option 1)**
