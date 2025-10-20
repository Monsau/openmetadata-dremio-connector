# 🔬 Guide d'Activation du Profiling Dremio

Le **Profiling** est maintenant intégré dans l'agent Metadata Dremio. Il collecte automatiquement les statistiques sur les colonnes (min, max, null count, distinct count, etc.) pour améliorer la qualité des données.

## ✅ Fonctionnalités du Profiler

### Statistiques sur les Tables
- **Nombre de lignes** (`rowCount`)
- **Nombre de colonnes** (`columnCount`)
- **Timestamp** du profiling

### Statistiques sur les Colonnes

#### Pour TOUS les types :
- **Nombre de valeurs** (`valuesCount`)
- **Nombre de NULL** (`nullCount`)
- **Proportion de NULL** (`nullProportion`)
- **Nombre de valeurs distinctes** (`distinctCount`)
- **Proportion de valeurs uniques** (`uniqueProportion`)

#### Pour les types numériques (INT, BIGINT, DOUBLE, FLOAT, DECIMAL) :
- **Minimum** (`min`)
- **Maximum** (`max`)
- **Moyenne** (`mean`)
- **Écart-type** (`stddev`)

#### Pour les types texte (VARCHAR, CHAR) :
- **Longueur minimale** (`minLength`)
- **Longueur maximale** (`maxLength`)
- **Longueur moyenne** (`meanLength`)

## 🚀 Activation du Profiling

### Option 1 : Via l'Interface UI

1. **Ouvrez OpenMetadata** : http://localhost:8585

2. **Allez dans Settings** > **Databases** > **dremio-prod**

3. **Cliquez sur l'onglet "Agents"**

4. **Trouvez votre pipeline Metadata** existant

5. **Cliquez sur Edit (⚙️)**

6. **Dans la configuration, activez "Enable Profiler"** :
   ```
   ☑️ Enable Profiler
   ```

7. **Configurez les options (optionnel)** :
   - **Profile Sample**: Pourcentage de données à analyser (100% = toutes les données)
   - **Thread Count**: Nombre de threads pour paralléliser (défaut: 5)
   - **Include Tables**: Tables spécifiques à profiler (vide = toutes)
   - **Exclude Tables**: Tables à exclure du profiling

8. **Sauvegardez** et **Re-lancez l'ingestion**

### Option 2 : Configuration YAML directe

Si vous utilisez une configuration YAML pour votre ingestion, ajoutez :

```yaml
source:
  type: CustomDatabase
  serviceName: dremio-prod
  serviceConnection:
    config:
      type: CustomDatabase
      sourcePythonClass: dremio_connector.dremio_source.DremioConnector
      connectionOptions:
        url: http://host.docker.internal:9047
        username: admin
        password: admin123
  sourceConfig:
    config:
      type: DatabaseMetadata
      # ✅ Activer le profiling
      enableProfiler: true
      profileSample: 100.0  # Profiler 100% des données
      threadCount: 5        # 5 threads parallèles
      # includeViews: true  # Inclure les vues (optionnel)
      # includeTags: false  # Ne pas inclure les tags (optionnel)
```

## 📊 Vérification des Résultats

### Dans l'UI OpenMetadata

1. **Naviguez vers une table** : 
   - Databases > staging > staging > stg_minio_customers

2. **Cliquez sur l'onglet "Profiler & Data Quality"**

3. **Vous devriez voir** :
   - 📈 **Graphique du nombre de lignes** dans le temps
   - 📊 **Statistiques par colonne** :
     - NULL count et proportion
     - Distinct values
     - Min/Max (pour les nombres)
     - Longueur min/max (pour les textes)

### Exemple de résultat attendu

Pour la table `staging.staging.stg_minio_customers` :

| Colonne | Type | Rows | Nulls | Distinct | Min | Max | Mean |
|---------|------|------|-------|----------|-----|-----|------|
| customer_id | INT | 100 | 0 (0%) | 100 | 1 | 100 | 50.5 |
| customer_name | VARCHAR | 100 | 0 (0%) | 98 | - | - | - |
| email | VARCHAR | 100 | 2 (2%) | 98 | - | - | - |
| phone | VARCHAR | 100 | 5 (5%) | 95 | - | - | - |
| city | VARCHAR | 100 | 0 (0%) | 45 | - | - | - |
| country | VARCHAR | 100 | 0 (0%) | 12 | - | - | - |

## ⚠️ Considérations Performance

### Tables volumineuses

Pour les tables avec **millions de lignes**, utilisez le sampling :

```yaml
profileSample: 10.0  # Profiler seulement 10% des données
```

Cela exécutera des requêtes comme :
```sql
SELECT ... FROM table WHERE RAND() < 0.1
```

### Optimisation

- **threadCount**: Augmentez pour paralléliser (5-10 threads)
- **includeF tables**: Limitez aux tables importantes
- **Fréquence**: Ne profilez pas trop souvent (1x par jour suffitégalement)

## 🔍 Requêtes SQL Exécutées

Le profiler exécute automatiquement ces requêtes sur Dremio :

### Pour toutes les colonnes :
```sql
SELECT 
    COUNT(*) as total_count,
    COUNT("column_name") as non_null_count,
    COUNT(DISTINCT "column_name") as distinct_count
FROM "database"."schema"."table"
```

### Pour les colonnes numériques :
```sql
SELECT 
    MIN("column_name") as min_value,
    MAX("column_name") as max_value,
    AVG(CAST("column_name" AS DOUBLE)) as mean_value,
    STDDEV(CAST("column_name" AS DOUBLE)) as stddev_value
FROM "database"."schema"."table"
```

### Pour les colonnes texte :
```sql
SELECT 
    MIN(LENGTH("column_name")) as min_length,
    MAX(LENGTH("column_name")) as max_length,
    AVG(LENGTH("column_name")) as avg_length
FROM "database"."schema"."table"
```

## ✅ Code Implémenté

Les méthodes suivantes ont été ajoutées à `DremioConnector` :

- `get_profile_metrics(table, profile_sample)` - Point d'entrée principal appelé par OpenMetadata
- `_get_row_count(dremio_path)` - Compte le nombre de lignes
- `_profile_column(dremio_path, column_name, column_type, total_rows)` - Profile une colonne spécifique

## 🎯 Prochaines Étapes

1. **Activez le profiling** dans votre agent Metadata
2. **Lancez une ingestion**
3. **Vérifiez les résultats** dans l'UI (onglet "Profiler & Data Quality")
4. **Configurez des alertes** sur la qualité des données (Data Quality Tests)
5. **Automatisez** avec des schedules réguliers (quotidiens/hebdomadaires)

## 📝 Logs de Debugging

Pour voir les logs du profiling, cherchez dans les logs d'ingestion :

```
🔬 Profiling table: dremio-prod.staging.staging.stg_minio_customers
  📊 Analyzing: staging.staging.stg_minio_customers
    📈 Profiling column: customer_id (INT)
    ✅ Column customer_id: 100/100 values, 100 distinct, 0 nulls
    📈 Profiling column: customer_name (VARCHAR)
    ✅ Column customer_name: 100/100 values, 98 distinct, 0 nulls
  ✅ Profile complete: 100 rows, 6 columns profiled
```

## 🛡️ Sécurité

- Le profiling utilise les **mêmes credentials** que l'ingestion metadata
- Toutes les requêtes SQL sont **échappées** avec des double quotes
- Les erreurs de profiling **ne bloquent pas l'ingestion** (warnings only)
- Les données sensibles **ne sont jamais stockées** (seulement les statistiques)

---

**✅ Le profiling est maintenant prêt à l'emploi !**
