# Plan d'Enrichissement du Connecteur Dremio

## 🎯 Objectif
Fusionner les fonctionnalités avancées du projet `dremiodbt` dans le connecteur `dremio` pour créer un connecteur enterprise-grade complet avec :
- Auto-discovery automatique de toutes les ressources Dremio
- Intégration dbt avec lineage automatique
- Agent intelligent pour la gestion du lineage
- Support complet des métadonnées (colonnes, types, descriptions)

---

## 📊 État Actuel

### Connecteur `dremio` (Base)
✅ Structure professionnelle avec packaging Python
✅ CLI fonctionnel (`dremio-connector`)
✅ Clients Dremio et OpenMetadata basiques
✅ Configuration YAML
✅ Documentation multilingue (EN/FR/ES/AR)
✅ Tests unitaires
✅ Exploration récursive des sources

❌ Discovery limité (ne trouve pas tous les datasets)
❌ Pas d'intégration dbt
❌ Pas de lineage automatique
❌ Mapping de types incomplet

### Projet `dremiodbt` (Fonctionnalités Avancées)
✅ Auto-discovery complet avec normalisation des types (type vs entityType)
✅ Intégration dbt opérationnelle
✅ Lineage dbt vérifié (stg_* → marts/*)
✅ Synchronisation complète : 36 ressources → 10 DB + 15 schemas + 11 tables
✅ Mapping de types Dremio → OpenMetadata
✅ Gestion des colonnes avec métadonnées
✅ Script de vérification du lineage

❌ Pas de packaging Python
❌ Pas de CLI
❌ Scripts standalone non réutilisables
❌ Configuration hardcodée

---

## 🚀 Plan d'Intégration

### Phase 1 : Enrichissement du DremioClient ✅ PRIORITÉ 1
**Objectif** : Remplacer la logique basique par l'auto-discovery avancé

**Fichier cible** : `src/dremio_connector/clients/dremio_client.py`

**Actions** :
1. ✅ Copier la logique de `auto-sync-dremio-openmetadata.py::DremioConnector`
2. ✅ Intégrer la méthode `discover_all_resources()` complète
3. ✅ Ajouter `_explore_item_deep()` avec normalisation des types
4. ✅ Remplacer `_extract_datasets_recursive()` actuel par la version avancée
5. ✅ Ajouter `_extract_columns()` avec mapping de types
6. ✅ Gérer les timeout et erreurs réseau
7. ✅ Ajouter visited set pour éviter les cycles

**Résultat attendu** :
```python
client = DremioClient(host, port, username, password)
client.authenticate()
resources = client.discover_all_resources()
# resources = [
#   {id, path, full_path, type: "space|source|folder|dataset", 
#    schema: [{name, type, description}]}
# ]
```

### Phase 2 : Enrichissement du OpenMetadataClient ✅ PRIORITÉ 1
**Objectif** : Ajouter les opérations PUT pour create/update idempotent

**Fichier cible** : `src/dremio_connector/clients/openmetadata_client.py`

**Actions** :
1. ✅ Copier les méthodes de `auto-sync-dremio-openmetadata.py::OpenMetadataConnector`
2. ✅ Remplacer POST par PUT pour idempotence
3. ✅ Ajouter `create_or_update_database()`
4. ✅ Ajouter `create_or_update_schema()`
5. ✅ Ajouter `create_or_update_table()` avec colonnes
6. ✅ Gérer les FQN correctement
7. ✅ Logging détaillé des opérations

**Résultat attendu** :
```python
om = OpenMetadataClient(url, token)
om.create_or_update_database(service_name, db_name, description)
om.create_or_update_schema(service_name, db_name, schema_name, description)
om.create_or_update_table(service_name, db_name, schema_name, table_name, columns)
```

### Phase 3 : Nouveau Module de Synchronisation 🔄 PRIORITÉ 2
**Objectif** : Créer un orchestrateur intelligent pour la sync complète

**Nouveau fichier** : `src/dremio_connector/core/sync_engine.py`

**Actions** :
1. ✅ Créer classe `DremioOpenMetadataSync`
2. ✅ Méthode `sync()` pour orchestration complète
3. ✅ Méthode `_organize_hierarchy()` pour structurer les ressources
4. ✅ Méthode `_sync_to_openmetadata()` pour création par batch
5. ✅ Statistiques de synchronisation
6. ✅ Gestion des erreurs avec retry logic
7. ✅ Logging détaillé des opérations

**Résultat attendu** :
```python
sync = DremioOpenMetadataSync(dremio_client, om_client, service_name)
stats = sync.sync()
# stats = {
#   "databases": 10,
#   "schemas": 15,
#   "tables": 11,
#   "errors": 0
# }
```

### Phase 4 : Module dbt Integration 🔄 PRIORITÉ 2
**Objectif** : Intégrer l'ingestion dbt avec lineage automatique

**Nouveau fichier** : `src/dremio_connector/dbt/dbt_integration.py`

**Actions** :
1. ✅ Créer classe `DbtIntegration`
2. ✅ Parser `manifest.json` pour extraire les modèles
3. ✅ Parser `catalog.json` pour les métadonnées
4. ✅ Créer configuration d'ingestion dbt programmatiquement
5. ✅ Lancer ingestion via API OpenMetadata
6. ✅ Vérifier le lineage créé
7. ✅ Générer rapport de lineage

**Nouveau fichier** : `src/dremio_connector/dbt/lineage_checker.py`

**Actions** :
1. ✅ Copier logique de `check-lineage.py`
2. ✅ Créer classe `LineageChecker`
3. ✅ Méthode `check_table_lineage(table_fqn)`
4. ✅ Méthode `check_all_lineage()` pour tous les marts
5. ✅ Visualisation ASCII du graphe de lineage
6. ✅ Export JSON/HTML du lineage

**Résultat attendu** :
```python
dbt = DbtIntegration(dbt_project_dir, om_client)
dbt.ingest_dbt_models()

lineage = LineageChecker(om_client)
lineage.check_table_lineage("service.db.schema.fct_orders")
# Output:
# stg_customers -> fct_orders
# stg_orders -> fct_orders
```

### Phase 5 : Agent Intelligent pour Lineage 🤖 PRIORITÉ 3
**Objectif** : Créer un agent qui analyse et crée le lineage automatiquement

**Nouveau fichier** : `src/dremio_connector/agents/lineage_agent.py`

**Actions** :
1. ⚠️ Créer classe `LineageAgent`
2. ⚠️ Parser SQL des VDS pour extraire dépendances
3. ⚠️ Utiliser regex/SQL parser pour identifier tables sources
4. ⚠️ Créer relations lineage via API OpenMetadata
5. ⚠️ Gérer lineage colonne par colonne (column lineage)
6. ⚠️ Détecter transformations (agregations, joins, etc.)
7. ⚠️ Mode auto-update pour refresh périodique

**Résultat attendu** :
```python
agent = LineageAgent(dremio_client, om_client)
agent.discover_lineage_from_vds()
agent.create_lineage_relationships()
# Automatically creates:
# - table-level lineage
# - column-level lineage
# - transformation metadata
```

### Phase 6 : CLI Enrichi 🖥️ PRIORITÉ 2
**Objectif** : Enrichir le CLI avec les nouvelles fonctionnalités

**Fichier cible** : `src/dremio_connector/cli.py`

**Actions** :
1. ✅ Ajouter commande `sync` pour synchronisation complète
2. ✅ Ajouter commande `check-lineage` pour vérifier le lineage
3. ✅ Ajouter commande `ingest-dbt` pour ingestion dbt
4. ✅ Ajouter commande `discover` pour discovery seul (sans sync)
5. ✅ Options de filtrage (--include-sources, --include-vds, etc.)
6. ✅ Mode dry-run pour voir ce qui serait fait
7. ✅ Export des résultats en JSON/YAML

**Résultat attendu** :
```bash
# Synchronisation complète
dremio-connector sync --config config/ingestion.yaml

# Discovery seul
dremio-connector discover --config config/ingestion.yaml --output resources.json

# Ingestion dbt
dremio-connector ingest-dbt --dbt-project dbt/ --config config/ingestion.yaml

# Vérifier lineage
dremio-connector check-lineage --table "service.db.schema.fct_orders"

# Dry-run
dremio-connector sync --config config/ingestion.yaml --dry-run
```

### Phase 7 : Configuration Avancée ⚙️ PRIORITÉ 3
**Objectif** : Enrichir la configuration YAML

**Fichier cible** : `config/ingestion.yaml`

**Actions** :
1. ⚠️ Ajouter section `dbt` pour configuration dbt
2. ⚠️ Ajouter section `lineage` pour options de lineage
3. ⚠️ Ajouter filtres avancés (regex patterns)
4. ⚠️ Options de performance (batch_size, max_workers)
5. ⚠️ Options de retry et timeout
6. ⚠️ Configuration du logging avancée

**Exemple config** :
```yaml
source:
  type: custom-dremio
  serviceName: Dremio Data Lake Platform
  serviceConnection:
    config:
      type: CustomDatabase
      connectionOptions:
        dremioHost: localhost
        dremioPort: "9047"
        dremioUsername: admin
        dremioPassword: admin123
        
        # Auto-discovery options
        discovery:
          max_depth: 5
          timeout: 10
          include_types:
            - space
            - source
            - folder
            - dataset
        
        # dbt Integration
        dbt:
          enabled: true
          project_dir: ./dbt
          profiles_dir: ./dbt
          target: prod
          ingest_lineage: true
        
        # Lineage Agent
        lineage:
          enabled: true
          auto_discover: true
          column_level: true
          parse_sql: true

workflowConfig:
  openMetadataServerConfig:
    hostPort: http://localhost:8585/api
    authProvider: openmetadata
    securityConfig:
      jwtToken: "your-token"
```

### Phase 8 : Tests et Documentation 📚 PRIORITÉ 2
**Objectif** : Tests complets et documentation mise à jour

**Actions** :
1. ✅ Tests unitaires pour `sync_engine.py`
2. ✅ Tests unitaires pour `dbt_integration.py`
3. ⚠️ Tests unitaires pour `lineage_agent.py`
4. ✅ Tests d'intégration end-to-end
5. ✅ Mise à jour README.md avec nouvelles fonctionnalités
6. ✅ Créer guide dbt (`docs/DBT_INTEGRATION.md`)
7. ✅ Créer guide lineage (`docs/LINEAGE_GUIDE.md`)
8. ✅ Mise à jour examples/

**Nouveaux exemples** :
- `examples/full_sync_example.py`
- `examples/dbt_ingestion_example.py`
- `examples/lineage_check_example.py`

---

## 📈 Métriques de Succès

### Fonctionnalité
- ✅ Discovery trouve 36+ ressources (comme dremiodbt)
- ✅ Sync crée 10 DB + 15 schemas + 11 tables
- ✅ Lineage dbt opérationnel (stg → marts)
- ⚠️ Agent lineage crée relations automatiquement
- ✅ CLI avec toutes les commandes

### Performance
- ⚠️ Discovery < 30 secondes
- ⚠️ Sync complète < 2 minutes
- ⚠️ Ingestion dbt < 10 secondes

### Qualité
- ✅ Couverture tests > 80%
- ✅ Documentation complète
- ✅ Exemples fonctionnels
- ✅ Logging détaillé

---

## 🗓️ Timeline Estimé

| Phase | Durée | Priorité | Status |
|-------|-------|----------|--------|
| Phase 1: DremioClient | 2h | P1 | 🔄 En cours |
| Phase 2: OpenMetadataClient | 1h | P1 | ⏳ À faire |
| Phase 3: Sync Engine | 2h | P2 | ⏳ À faire |
| Phase 4: dbt Integration | 3h | P2 | ⏳ À faire |
| Phase 5: Lineage Agent | 4h | P3 | ⏳ À faire |
| Phase 6: CLI Enrichi | 1h | P2 | ⏳ À faire |
| Phase 7: Config Avancée | 1h | P3 | ⏳ À faire |
| Phase 8: Tests & Docs | 3h | P2 | ⏳ À faire |
| **TOTAL** | **17h** | | |

---

## 🎯 Prochaines Actions

### Immédiat (Phase 1)
1. ✅ Backup du `dremio_client.py` actuel
2. 🔄 Intégrer `discover_all_resources()` de auto-sync
3. 🔄 Tester discovery sur localhost:9047
4. 🔄 Valider que 36+ ressources sont trouvées

### Court Terme (Phase 2-3)
1. ⏳ Enrichir OpenMetadataClient avec PUT
2. ⏳ Créer sync_engine.py
3. ⏳ Tester sync complète
4. ⏳ Valider stats de sync

### Moyen Terme (Phase 4-6)
1. ⏳ Intégrer dbt
2. ⏳ Créer lineage_agent
3. ⏳ Enrichir CLI

### Long Terme (Phase 7-8)
1. ⏳ Config avancée
2. ⏳ Tests complets
3. ⏳ Documentation finale
4. ⏳ Release 2.0.0

---

## 📝 Notes Techniques

### Différences Clés API Dremio
- **Catalog root** : `GET /api/v3/catalog` → utilise `type` + `containerType`
- **By-path** : `GET /api/v3/catalog/by-path/{path}` → utilise `entityType`
- **By-id** : `GET /api/v3/catalog/{id}` → utilise `entityType` + `children`

### Normalisation des Types
```python
# CONTAINER + SPACE → "space"
# CONTAINER + SOURCE → "source"
# CONTAINER + FOLDER → "folder"
# DATASET → "dataset"
```

### Mapping Types Dremio → OpenMetadata
```python
TYPE_MAPPING = {
    "INTEGER": "INT",
    "BIGINT": "BIGINT",
    "VARCHAR": "VARCHAR",
    "DECIMAL": "DECIMAL",
    "DOUBLE": "DOUBLE",
    "FLOAT": "FLOAT",
    "DATE": "DATE",
    "TIMESTAMP": "TIMESTAMP",
    "BOOLEAN": "BOOLEAN"
}
```

---

**Créé** : 2025-10-10  
**Auteur** : GitHub Copilot  
**Version** : 1.0  
**Status** : 🔄 En Cours
