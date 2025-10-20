# ⚙️ Configuration du Connector Dremio

## 📋 Vue d'ensemble

Le connector Dremio pour OpenMetadata se c### Configuration avec Profiling Optimisé

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 50000
}
```

**Ce qui est activé :**
- ✅ Metadata ingestion
- ✅ Auto-classification (activée par défaut)
- ✅ Profiling sur 50,000 lignes sample
- ❌ DBT

### Configuration sans Classification

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "classificationEnabled": false,
  "profileSampleRows": 50000
}
```

**Ce qui est activé :**
- ✅ Metadata ingestion
- ❌ Auto-classification (désactivée)
- ✅ Profiling sur 50,000 lignes sample
- ❌ DBT

### Configuration avec DBT (sans sampling)ment via `connectionOptions`** dans l'interface UI.

**Aucun fichier YAML n'est nécessaire** - toutes les options sont passées directement dans la configuration du service.

## 🔧 Configuration Complète

### Format JSON dans l'UI

```json
{
  "url": "http://dremio-server:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 10000,
  "classificationEnabled": true,
  "dbtEnabled": true,
  "dbtCatalogPath": "/path/to/dbt/target/catalog.json",
  "dbtManifestPath": "/path/to/dbt/target/manifest.json",
  "dbtRunResultsPath": "/path/to/dbt/target/run_results.json"
}
```

## 📊 Paramètres de Configuration

### 1. Connexion Dremio (Obligatoire)

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `url` | string | URL du serveur Dremio | `http://dremio:9047` |
| `username` | string | Nom d'utilisateur | `admin` |
| `password` | string | Mot de passe | `admin123` |

### 2. Profiling avec Sampling (Optionnel)

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `profileSampleRows` | integer | Nombre de lignes à analyser | `null` (toutes) |

**Comportement :**

- **`profileSampleRows: null`** ou absent : Analyse TOUTES les lignes
  ```sql
  SELECT COUNT(*), AVG(col), ... FROM table
  ```

- **`profileSampleRows: 10000`** : Analyse seulement 10,000 lignes
  ```sql
  SELECT COUNT(*), AVG(col), ... FROM (SELECT * FROM table LIMIT 10000)
  ```

**Recommandations :**

| Taille de table | Sample recommandé |
|----------------|-------------------|
| < 100K lignes | Pas de sampling |
| 100K - 1M | 10,000 - 50,000 |
| 1M - 10M | 50,000 - 100,000 |
| > 10M | 100,000 - 500,000 |

### 3. Auto-Classification (Optionnel)

| Paramètre | Type | Description | Défaut |
|-----------|------|-------------|--------|
| `classificationEnabled` | boolean | Activer la classification automatique | `true` |

**Comportement :**

- **`classificationEnabled: true`** ou absent : Tags PII/Sensitive/Financial appliqués automatiquement
- **`classificationEnabled: false`** : Pas de classification automatique

**Tags détectés :**
- PII: Email, Phone, Name, Address, ID
- Sensitive: Credential
- Financial: CreditCard, BankAccount

### 4. Intégration DBT (Optionnel)

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `dbtEnabled` | boolean | Activer DBT | `true` |
| `dbtCatalogPath` | string | Chemin vers catalog.json | `/opt/dbt/target/catalog.json` |
| `dbtManifestPath` | string | Chemin vers manifest.json | `/opt/dbt/target/manifest.json` |
| `dbtRunResultsPath` | string | Chemin vers run_results.json (optionnel) | `/opt/dbt/target/run_results.json` |

**Note :** Si `dbtEnabled: false` ou absent, les paramètres DBT sont ignorés.

## 📝 Exemples de Configuration

### Configuration Minimale (Metadata seulement)

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123"
}
```

**Ce qui est activé :**
- ✅ Metadata ingestion
- ✅ Auto-classification (PII/Sensitive/Financial)
- ❌ Profiling (pas de sampling, toutes les lignes)
- ❌ DBT

### Configuration avec Profiling Optimisé

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 50000
}
```

**Ce qui est activé :**
- ✅ Metadata ingestion
- ✅ Auto-classification
- ✅ Profiling sur 50,000 lignes sample
- ❌ DBT

### Configuration Complète (4-in-1)

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 100000,
  "classificationEnabled": true,
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/myproject/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/myproject/target/manifest.json",
  "dbtRunResultsPath": "/opt/dbt/myproject/target/run_results.json"
}
```

**Ce qui est activé :**
- ✅ Metadata ingestion
- ✅ Auto-classification
- ✅ Profiling sur 100,000 lignes sample
- ✅ DBT enrichment

### Configuration Production (Grandes Tables)

```json
{
  "url": "http://prod-dremio.company.com:9047",
  "username": "metadata_user",
  "password": "secure_password_here",
  "profileSampleRows": 500000
}
```

**Optimisations :**
- Large sample (500K lignes) pour bonne représentativité
- Pas de DBT (souvent pas nécessaire en prod)
- Credentials sécurisés

## 🎯 Configuration dans l'UI OpenMetadata

### Étape par étape

1. **Aller dans Settings**
   - Cliquer sur ⚙️ en haut à droite
   - Menu gauche → **Databases**

2. **Créer ou éditer le service Dremio**
   - Nouveau : **+ Add Database Service** → **Dremio**
   - Existant : Cliquer sur le service → **Edit Connection**

3. **Remplir Connection Options**

Dans le champ **Connection Options**, copier-coller votre configuration JSON :

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 50000
}
```

4. **Tester la connexion**
   - Cliquer sur **Test Connection**
   - Vérifier : ✅ Connection successful

5. **Sauvegarder**
   - Cliquer sur **Save**

## 🔍 Vérification de la Configuration

### Logs de Démarrage

```bash
docker logs openmetadata_ingestion -f
```

**Chercher ces lignes :**

```log
🚀 Preparing Dremio connector...
📋 Found connectionOptions: url=http://dremio:9047, username=admin
📊 Profiling sample rows: 50000
🔧 DBT enabled: True
```

### Test de Configuration

```bash
# Entrer dans le container
docker exec -it openmetadata_ingestion bash

# Tester l'import
python3 -c "
from dremio_connector.dremio_source import DremioConnector
print('✅ Connector loaded')
"

# Tester la connexion Dremio
curl http://host.docker.internal:9047/apiv2/server_status
```

## 🔒 Sécurité

### Bonnes Pratiques

1. **Ne jamais commit les credentials**
   - Utiliser des variables d'environnement si possible
   - Stocker les mots de passe dans un gestionnaire de secrets

2. **Permissions minimales**
   - Créer un user Dremio dédié pour OpenMetadata
   - Donner seulement les permissions `SELECT` et `DESCRIBE`

3. **Utiliser SSL en production**
   ```json
   {
     "url": "https://dremio-prod.company.com:9047",
     "username": "metadata_service",
     "password": "secure_password"
   }
   ```

### Exemple de User Dremio Dédié

```sql
-- Dans Dremio, créer un user spécifique
CREATE USER metadata_reader WITH PASSWORD 'secure_password';

-- Donner les permissions de lecture
GRANT SELECT ON ALL TABLES IN SCHEMA public TO metadata_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA hr TO metadata_reader;
```

## 🚨 Troubleshooting

### Profiling trop lent

**Symptôme :** L'ingestion tourne pendant des heures

**Solution :** Réduire `profileSampleRows`

```json
{
  "profileSampleRows": 10000  // Au lieu de 100000
}
```

### DBT files not found

**Symptôme :** Logs montrent `⚠️  DBT catalog not found`

**Solution 1 :** Vérifier les chemins

```bash
# Dans le container
docker exec -it openmetadata_ingestion bash
ls -la /opt/dbt/target/
```

**Solution 2 :** Monter le volume DBT

```yaml
# docker-compose.yml
services:
  openmetadata_ingestion:
    volumes:
      - /local/dbt/project/target:/opt/dbt/target:ro
```

### Connection refused

**Symptôme :** Erreur lors du test de connexion

**Solution 1 :** Vérifier l'URL

```bash
# Tester depuis le container
docker exec openmetadata_ingestion curl http://host.docker.internal:9047/apiv2/server_status
```

**Solution 2 :** Si Dremio dans Docker, utiliser le nom du service

```json
{
  "url": "http://dremio_server:9047"  // Nom du service Docker
}
```

## 📚 Ressources

- [Guide DBT Integration](./DBT_INTEGRATION.md)
- [Guide Classification](./CLASSIFICATION_GUIDE.md)
- [Guide Profiling](./PROFILING_GUIDE.md)
- [Documentation OpenMetadata](https://docs.open-metadata.org/)

---

**Configuration 100% via connectionOptions - Pas de YAML requis !** 🚀
