# 📝 Exemples de Configuration - Copy/Paste pour l'UI

## Configuration Minimale (Metadata + Classification)

```json
{
  "url": "http://host.docker.internal:9047",
  "username": "admin",
  "password": "admin123"
}
```

## Configuration avec Profiling Sample (Recommandé)

```json
{
  "url": "http://host.docker.internal:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 10000
}
```

## Configuration sans Classification

```json
{
  "url": "http://host.docker.internal:9047",
  "username": "admin",
  "password": "admin123",
  "classificationEnabled": false,
  "profileSampleRows": 10000
}
```

## Configuration avec DBT (sans sampling)

```json
{
  "url": "http://host.docker.internal:9047",
  "username": "admin",
  "password": "admin123",
  "dbtEnabled": true,
  "dbtCatalogPath": "/opt/dbt/target/catalog.json",
  "dbtManifestPath": "/opt/dbt/target/manifest.json"
}
```

## Configuration Complète (4-in-1)

```json
{
  "url": "http://host.docker.internal:9047",
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

## Configuration Production (Grandes Tables)

```json
{
  "url": "https://prod-dremio.company.com:9047",
  "username": "metadata_service",
  "password": "secure_password_here",
  "profileSampleRows": 500000
}
```

## Configuration Dev (Fast Profiling)

```json
{
  "url": "http://localhost:9047",
  "username": "admin",
  "password": "admin123",
  "profileSampleRows": 1000
}
```

## ℹ️ Notes

### profileSampleRows

- **Non défini ou null** : Analyse TOUTES les lignes (lent pour grandes tables)
- **1000-10000** : Rapide, bon pour dev/test
- **10000-100000** : Équilibré, bon pour prod
- **> 100000** : Pour très grandes tables (> 10M lignes)

### classificationEnabled

- **Non défini ou true** : Classification automatique activée (PII/Sensitive/Financial)
- **false** : Pas de classification automatique

### DBT

- **dbtEnabled: false** ou absent : Pas d'intégration DBT
- **dbtEnabled: true** : Nécessite dbtCatalogPath ET dbtManifestPath
- **dbtRunResultsPath** : Optionnel (pour voir les résultats d'exécution)

### Chemins DBT avec Docker

Si vous utilisez Docker, montez le volume :

```yaml
# docker-compose.yml
volumes:
  - /path/local/dbt/project/target:/opt/dbt/target:ro
```

Puis utilisez : `/opt/dbt/target/catalog.json`
