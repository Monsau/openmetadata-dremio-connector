# 🎯 Configuration Complète - Agent 4-in-1

## 📋 Tous les Paramètres Disponibles

### Configuration Complète

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 50000,
  "classificationEnabled": true,
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/target/manifest.json",
  "dbtRunResultsPath": "/opt/dbt/target/run_results.json"
}
```

## 🔧 Paramètres Détaillés

### 1️⃣ Connexion Dremio (Obligatoire)

| Paramètre | Type | Obligatoire | Description | Exemple |
|-----------|------|-------------|-------------|---------|
| `url` | string | ✅ Oui | URL du serveur Dremio | `http://dremio:9047` |
| `username` | string | ✅ Oui | Nom d'utilisateur | `admin` |
| `password` | string | ✅ Oui | Mot de passe | `admin123` |

### 2️⃣ Profiling (Optionnel)

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `profileSampleRows` | integer | `null` | Nombre de lignes pour profiling |

**Valeurs recommandées :**
- `null` ou absent = toutes les lignes
- `10000` = tables < 1M lignes
- `50000` = tables 1M-10M lignes
- `100000+` = tables > 10M lignes

### 3️⃣ Classification (Optionnel)

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `classificationEnabled` | boolean | `true` | Activer auto-classification |

**Tags appliqués quand activé :**
- PII.Email
- PII.Phone
- PII.Name
- PII.Address
- PII.ID
- Sensitive.Credential
- Financial.CreditCard
- Financial.BankAccount

### 4️⃣ DBT (Optionnel)

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `dbtEnabled` | boolean | `false` | Activer intégration DBT |
| `dbtCatalogPath` | string | - | Chemin vers catalog.json |
| `dbtManifestPath` | string | - | Chemin vers manifest.json |
| `dbtRunResultsPath` | string | - | Chemin vers run_results.json (optionnel) |

**Note :** Si `dbtEnabled: true`, alors `dbtCatalogPath` et `dbtManifestPath` sont obligatoires.

## 🎛️ Configurations par Scénario

### Scénario 1 : Metadata Seulement

**Usage :** Extraction rapide, pas de profiling ni classification

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": null,
  "classificationEnabled": false
}
```

**Résultat :**
- ✅ Metadata (databases, schemas, tables, columns)
- ❌ Profiling
- ❌ Classification
- ❌ DBT

---

### Scénario 2 : Metadata + Classification

**Usage :** Détection de données sensibles (PII, etc.)

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "classificationEnabled": true
}
```

**Résultat :**
- ✅ Metadata
- ❌ Profiling
- ✅ Classification (8 tags)
- ❌ DBT

---

### Scénario 3 : Metadata + Profiling Rapide

**Usage :** Statistiques sur échantillon (dev/test)

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 1000,
  "classificationEnabled": false
}
```

**Résultat :**
- ✅ Metadata
- ✅ Profiling (1000 lignes sample)
- ❌ Classification
- ❌ DBT

---

### Scénario 4 : Metadata + Profiling + Classification

**Usage :** Analyse complète avec performance optimisée

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 50000,
  "classificationEnabled": true
}
```

**Résultat :**
- ✅ Metadata
- ✅ Profiling (50K lignes sample)
- ✅ Classification
- ❌ DBT

---

### Scénario 5 : Metadata + DBT (sans profiling)

**Usage :** Enrichissement avec descriptions DBT

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "classificationEnabled": false,
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/target/manifest.json"
}
```

**Résultat :**
- ✅ Metadata
- ❌ Profiling
- ❌ Classification
- ✅ DBT (descriptions, tags)

---

### Scénario 6 : Configuration Complète (4-in-1)

**Usage :** Tous les features activés (recommandé pour production)

```json
{
  "url": "http://dremio:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 100000,
  "classificationEnabled": true,
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/target/manifest.json",
  "dbtRunResultsPath": "/opt/dbt/target/run_results.json"
}
```

**Résultat :**
- ✅ Metadata
- ✅ Profiling (100K lignes sample)
- ✅ Classification (8 tags)
- ✅ DBT (descriptions, tags)

## 📊 Comparaison des Scénarios

| Scénario | Metadata | Profiling | Classification | DBT | Durée* |
|----------|----------|-----------|----------------|-----|--------|
| 1. Metadata only | ✅ | ❌ | ❌ | ❌ | ~1 min |
| 2. + Classification | ✅ | ❌ | ✅ | ❌ | ~2 min |
| 3. + Profiling rapide | ✅ | ✅ (1K) | ❌ | ❌ | ~3 min |
| 4. + Classification | ✅ | ✅ (50K) | ✅ | ❌ | ~5 min |
| 5. + DBT | ✅ | ❌ | ❌ | ✅ | ~2 min |
| 6. Complet (4-in-1) | ✅ | ✅ (100K) | ✅ | ✅ | ~7 min |

*Durée indicative pour 8 sources Dremio avec 16 tables

## 🎯 Recommandations par Environnement

### Développement (Dev)

```json
{
  "url": "http://localhost:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 1000,
  "classificationEnabled": true
}
```

**Pourquoi :**
- Rapide (1000 lignes)
- Classification pour tester les tags
- Pas de DBT (souvent pas nécessaire en dev)

---

### Staging/Test

```json
{
  "url": "http://staging-dremio:9047",
  "username": "metadata_user",
  "password": "secure_password",
  "profileSampleRows": 10000,
  "classificationEnabled": true,
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/staging/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/staging/target/manifest.json"
}
```

**Pourquoi :**
- Sample moyen (10K lignes)
- Classification pour validation
- DBT pour tester l'enrichissement

---

### Production

```json
{
  "url": "https://prod-dremio.company.com:9047",
  "username": "metadata_service",
  "password": "production_password",
  "profileSampleRows": 100000,
  "classificationEnabled": true,
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/prod/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/prod/target/manifest.json",
  "dbtRunResultsPath": "/opt/dbt/prod/target/run_results.json"
}
```

**Pourquoi :**
- Large sample (100K lignes) pour représentativité
- Classification pour sécurité/compliance
- DBT complet pour documentation

## 🔍 Logs de Vérification

Après configuration, vérifier les logs :

```bash
docker logs openmetadata_ingestion -f
```

**Chercher ces lignes :**

```log
🚀 Preparing Dremio connector...
📋 Found connectionOptions: url=http://dremio:9047, username=admin
📊 Profiling sample rows: 50000
🏷️  Classification enabled: True
🔧 DBT enabled: True
```

## 🚨 Erreurs Courantes

### Classification ne fonctionne pas

**Symptôme :** Aucun tag appliqué

**Solutions :**
1. Vérifier : `"classificationEnabled": true`
2. Vérifier dans l'ingestion : **Enable Auto Classification** coché
3. Logs : Chercher `🏷️  Classification enabled: True`

### Profiling trop lent

**Symptôme :** Ingestion > 30 min

**Solution :** Réduire `profileSampleRows`
```json
{
  "profileSampleRows": 10000  // Au lieu de 100000
}
```

### DBT files not found

**Symptôme :** `⚠️  DBT catalog not found`

**Solution :** Vérifier les chemins
```bash
docker exec -it openmetadata_ingestion ls -la /opt/dbt/target/
```

## 📚 Documentation Connexe

- [CONFIGURATION.md](./CONFIGURATION.md) - Guide complet
- [CONFIGURATION_EXAMPLES.md](./CONFIGURATION_EXAMPLES.md) - Exemples copy/paste
- [DBT_INTEGRATION.md](./DBT_INTEGRATION.md) - Guide DBT
- [CLASSIFICATION_GUIDE.md](./CLASSIFICATION_GUIDE.md) - Patterns de classification

---

**Agent 4-in-1 : Configurez ce que vous voulez, quand vous voulez !** 🚀
