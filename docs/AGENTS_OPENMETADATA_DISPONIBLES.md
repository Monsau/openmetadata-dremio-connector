# 🤖 Agents OpenMetadata Disponibles

## Vue d'ensemble

OpenMetadata propose plusieurs types d'agents/workflows pour collecter des métadonnées et enrichir votre catalogue de données. Voici la liste complète des agents disponibles **autres que DBT**.

---

## 📊 1. Metadata Ingestion Agents

Ces agents collectent les métadonnées (tables, colonnes, schémas) depuis différentes sources.

### 1.1 Databases (JDBC)

#### ✅ Dremio (DÉJÀ IMPLÉMENTÉ)
- **État** : ✅ Actif et fonctionnel
- **Type** : Custom connector via REST API
- **Capacités** : Metadata + Profiling + Classification
- **Documentation** : `AGENT_METADATA_COMPLET.md`

#### PostgreSQL
- **Type** : JDBC connector
- **Capacités** : 
  - Metadata ingestion
  - Profiling
  - Query usage
  - Lineage
- **Configuration** :
```yaml
source:
  type: Postgres
  serviceName: postgres-prod
  serviceConnection:
    config:
      type: Postgres
      username: <username>
      password: <password>
      hostPort: localhost:5432
      database: postgres
```

#### MySQL / MariaDB
- **Type** : JDBC connector
- **Capacités** : Metadata, Profiling, Usage, Lineage
- **Configuration** :
```yaml
source:
  type: Mysql
  serviceName: mysql-prod
  serviceConnection:
    config:
      type: Mysql
      username: <username>
      password: <password>
      hostPort: localhost:3306
      databaseSchema: <database>
```

#### Oracle
- **Type** : JDBC connector
- **Capacités** : Metadata, Profiling, Usage
- **Configuration** :
```yaml
source:
  type: Oracle
  serviceName: oracle-prod
  serviceConnection:
    config:
      type: Oracle
      username: <username>
      password: <password>
      hostPort: localhost:1521
      oracleConnectionType:
        oracleServiceName: <service_name>
```

#### Microsoft SQL Server
- **Type** : JDBC connector
- **Capacités** : Metadata, Profiling, Usage, Lineage
- **Configuration** :
```yaml
source:
  type: Mssql
  serviceName: mssql-prod
  serviceConnection:
    config:
      type: Mssql
      username: <username>
      password: <password>
      hostPort: localhost:1433
      database: <database>
```

#### Snowflake
- **Type** : Cloud Data Warehouse
- **Capacités** : Metadata, Profiling, Usage, Lineage, Query logs
- **Configuration** :
```yaml
source:
  type: Snowflake
  serviceName: snowflake-prod
  serviceConnection:
    config:
      type: Snowflake
      username: <username>
      password: <password>
      account: <account>
      warehouse: <warehouse>
      database: <database>
```

#### BigQuery (Google Cloud)
- **Type** : Cloud Data Warehouse
- **Capacités** : Metadata, Profiling, Usage, Lineage, Cost analysis
- **Configuration** :
```yaml
source:
  type: BigQuery
  serviceName: bigquery-prod
  serviceConnection:
    config:
      type: BigQuery
      credentials:
        gcpConfig:
          type: service_account
          projectId: <project_id>
          privateKeyId: <private_key_id>
          privateKey: <private_key>
          clientEmail: <client_email>
```

#### Redshift (AWS)
- **Type** : Cloud Data Warehouse
- **Capacités** : Metadata, Profiling, Usage, Lineage
- **Configuration** :
```yaml
source:
  type: Redshift
  serviceName: redshift-prod
  serviceConnection:
    config:
      type: Redshift
      username: <username>
      password: <password>
      hostPort: <cluster>.redshift.amazonaws.com:5439
      database: <database>
```

### 1.2 NoSQL Databases

#### MongoDB
- **Type** : Document database
- **Capacités** : Metadata, Sample data
- **Configuration** :
```yaml
source:
  type: MongoDB
  serviceName: mongodb-prod
  serviceConnection:
    config:
      type: MongoDB
      username: <username>
      password: <password>
      hostPort: localhost:27017
```

#### Cassandra
- **Type** : Wide-column store
- **Capacités** : Metadata
- **Configuration** :
```yaml
source:
  type: Cassandra
  serviceName: cassandra-prod
  serviceConnection:
    config:
      type: Cassandra
      username: <username>
      password: <password>
      hostPort: localhost:9042
```

#### DynamoDB (AWS)
- **Type** : Key-value database
- **Capacités** : Metadata, Table schemas
- **Configuration** :
```yaml
source:
  type: DynamoDB
  serviceName: dynamodb-prod
  serviceConnection:
    config:
      type: DynamoDB
      awsConfig:
        awsAccessKeyId: <access_key>
        awsSecretAccessKey: <secret_key>
        awsRegion: us-east-1
```

### 1.3 Storage Systems

#### S3 (AWS)
- **Type** : Object storage
- **Capacités** : Metadata, File structure, Schema extraction
- **Configuration** :
```yaml
source:
  type: S3
  serviceName: s3-prod
  serviceConnection:
    config:
      type: S3
      awsConfig:
        awsAccessKeyId: <access_key>
        awsSecretAccessKey: <secret_key>
        awsRegion: us-east-1
```

#### HDFS
- **Type** : Distributed file system
- **Capacités** : Metadata, File structure
- **Configuration** :
```yaml
source:
  type: HDFS
  serviceName: hdfs-prod
  serviceConnection:
    config:
      type: HDFS
      connectionOptions:
        hdfsURL: hdfs://namenode:9000
```

#### Azure Data Lake Storage (ADLS)
- **Type** : Cloud storage
- **Capacités** : Metadata, File structure
- **Configuration** :
```yaml
source:
  type: ADLS
  serviceName: adls-prod
  serviceConnection:
    config:
      type: ADLS
      clientId: <client_id>
      clientSecret: <client_secret>
      tenantId: <tenant_id>
      accountName: <storage_account>
```

### 1.4 Data Platforms

#### Databricks
- **Type** : Unified analytics platform
- **Capacités** : Metadata, Lineage, Notebooks, Jobs
- **Configuration** :
```yaml
source:
  type: Databricks
  serviceName: databricks-prod
  serviceConnection:
    config:
      type: Databricks
      token: <access_token>
      hostPort: <workspace>.cloud.databricks.com
      httpPath: /sql/1.0/warehouses/<warehouse_id>
```

#### Apache Hive
- **Type** : Data warehouse
- **Capacités** : Metadata, Profiling, Lineage
- **Configuration** :
```yaml
source:
  type: Hive
  serviceName: hive-prod
  serviceConnection:
    config:
      type: Hive
      username: <username>
      password: <password>
      hostPort: localhost:10000
      databaseSchema: <database>
```

#### Apache Spark
- **Type** : Processing engine
- **Capacités** : Metadata, Job tracking
- **Configuration** :
```yaml
source:
  type: Spark
  serviceName: spark-prod
  serviceConnection:
    config:
      type: Spark
      hostPort: <master_url>
      connectionArguments:
        spark.app.name: OpenMetadata
```

---

## 📈 2. Data Profiler Agent

### Rôle
Analyse statistique des données pour évaluer la qualité.

### Capacités
- **Métriques de table** : Nombre de lignes, colonnes
- **Métriques de colonnes** : 
  - Null count / proportion
  - Distinct count / unique count
  - Min / Max / Mean / Median
  - Standard deviation
  - Quartiles (Q1, Q2, Q3)
- **Métriques textuelles** :
  - Longueur min/max/moyenne
  - Patterns communs
- **Métriques numériques** :
  - Distribution
  - Histogrammes

### Activation
```yaml
source:
  sourceConfig:
    config:
      type: DatabaseMetadata
      enableProfiler: true
      profileSample: 100  # % de données à échantillonner
      profileQuery: ""    # Query custom optionnelle
```

### Support
- ✅ Dremio (implémenté)
- ✅ PostgreSQL
- ✅ MySQL
- ✅ Oracle
- ✅ SQL Server
- ✅ Snowflake
- ✅ BigQuery
- ✅ Redshift
- ⚠️ NoSQL (limité)

### Documentation
Voir `PROFILING_GUIDE.md` pour Dremio

---

## 🏷️ 3. Auto Classification Agent

### Rôle
Détection automatique de données sensibles (PII, GDPR, etc.)

### Capacités
- **Détection basée sur patterns** : Noms de colonnes
- **Détection basée sur données** : Regex sur valeurs
- **Classifications supportées** :
  - PII (Personally Identifiable Information)
  - Sensitive Data
  - Financial Data
  - Healthcare (PHI)
  - Custom classifications

### Tags Standard
- **PII** : Email, Phone, Name, Address, SSN, ID
- **Sensitive** : Password, Token, API Key, Secret
- **Financial** : Credit Card, Bank Account, IBAN, SWIFT
- **Healthcare** : Medical Record Number, Patient ID

### Activation
```yaml
source:
  sourceConfig:
    config:
      type: DatabaseMetadata
      enableAutoClassification: true
      classificationFilterPattern:
        includes:
          - PII
          - Sensitive
          - Financial
```

### Support
- ✅ Dremio (implémenté)
- ✅ PostgreSQL
- ✅ MySQL
- ✅ Oracle
- ✅ SQL Server
- ✅ Snowflake
- ✅ BigQuery
- ✅ Redshift

### Documentation
Voir `CLASSIFICATION_GUIDE.md` pour Dremio

---

## 📊 4. Usage Agent (Query Analytics)

### Rôle
Collecte les requêtes exécutées et analyse l'utilisation des tables.

### Capacités
- **Requêtes capturées** : 
  - Query text
  - User / Service account
  - Timestamp
  - Execution time
  - Rows scanned
- **Métriques d'utilisation** :
  - Most queried tables
  - Query patterns
  - Peak usage times
  - User activity

### Activation
```yaml
source:
  type: Usage
  serviceName: <database>-usage
  sourceConfig:
    config:
      type: DatabaseUsage
      queryLogDuration: 7  # Jours de logs à analyser
      stageFileLocation: /tmp/usage
```

### Support
- ✅ Snowflake (excellent - query history API)
- ✅ BigQuery (excellent - audit logs)
- ✅ Redshift (excellent - system tables)
- ✅ PostgreSQL (bon - pg_stat_statements)
- ⚠️ MySQL (limité)
- ⚠️ Dremio (API disponible mais pas encore implémenté)

### Exemple Snowflake
```yaml
source:
  type: Usage
  serviceName: snowflake-usage
  sourceConfig:
    config:
      type: DatabaseUsage
      queryLogDuration: 7
```

---

## 🔗 5. Lineage Agent

### Rôle
Traçage des transformations de données (d'où viennent les données, où vont-elles).

### Capacités
- **Table-to-table lineage** : Relations entre tables
- **Column-to-column lineage** : Transformations de colonnes
- **Query-based lineage** : Parsing des requêtes SQL
- **ETL lineage** : Tracking des pipelines

### Activation
```yaml
source:
  type: Lineage
  serviceName: <database>-lineage
  sourceConfig:
    config:
      type: DatabaseLineage
      queryLogDuration: 7
```

### Support
- ✅ Snowflake (excellent)
- ✅ BigQuery (excellent)
- ✅ Databricks (excellent)
- ✅ Redshift (bon)
- ⚠️ PostgreSQL (basique)
- ⚠️ MySQL (basique)
- ❌ Dremio (pas encore implémenté)

### Intégration DBT
Le lineage DBT est géré par l'agent DBT (voir `dags/dbt_dag.py`)

---

## 🧪 6. Data Quality Agent

### Rôle
Définition et exécution de tests de qualité de données.

### Types de Tests
- **Table Tests** :
  - Row count validation
  - Freshness check
  - Custom SQL assertions
- **Column Tests** :
  - Not null
  - Unique values
  - Values in range
  - Regex pattern matching
  - Custom SQL

### Définition des Tests
Via l'interface OpenMetadata :
1. Sélectionner une table
2. Onglet "Data Quality"
3. "Add Test" → Choisir le type
4. Configurer les paramètres

### Exécution
```yaml
source:
  type: TestSuite
  serviceName: <database>-tests
  sourceConfig:
    config:
      type: TestSuite
```

### Support
- ✅ Tous les connecteurs JDBC
- ✅ Dremio (via SQL)
- ✅ Snowflake
- ✅ BigQuery
- ✅ Redshift

---

## 📋 7. Data Insights Agent

### Rôle
Génération de métriques et rapports sur l'ensemble du catalogue.

### Métriques Collectées
- **Coverage** :
  - % de tables avec description
  - % de colonnes avec description
  - % de tables avec owner
- **Ownership** :
  - Répartition par équipe
  - Tables sans owner
- **Data Quality** :
  - Tests passés/échoués
  - Tendances qualité
- **Classification** :
  - % de colonnes classifiées
  - Distribution des tags PII

### Activation
Automatique - Pas de configuration nécessaire

### Accès
UI : Insights → Data Insights

---

## 🔔 8. Webhook / Event Notification

### Rôle
Notifications en temps réel sur les changements de métadonnées.

### Événements Supportés
- Table créée/modifiée/supprimée
- Schema changé
- Owner assigné
- Tag appliqué
- Test de qualité échoué

### Configuration
```yaml
source:
  type: EventHub
  serviceName: notifications
  sourceConfig:
    config:
      type: EventHub
      endpoints:
        - http://your-webhook-url.com/metadata-events
```

### Destinations
- Webhooks HTTP
- Slack
- Microsoft Teams
- Email
- Custom handlers

---

## 📁 9. Messaging Systems Agents

### Apache Kafka
- **Capacités** : Topics, Schemas, Consumer groups
- **Configuration** :
```yaml
source:
  type: Kafka
  serviceName: kafka-prod
  serviceConnection:
    config:
      type: Kafka
      bootstrapServers: localhost:9092
      schemaRegistryURL: http://localhost:8081
```

### Apache Pulsar
- **Capacités** : Topics, Namespaces
- **Configuration** :
```yaml
source:
  type: Pulsar
  serviceName: pulsar-prod
  serviceConnection:
    config:
      type: Pulsar
      brokerUrl: pulsar://localhost:6650
      adminUrl: http://localhost:8080
```

### RabbitMQ
- **Capacités** : Queues, Exchanges
- **Configuration** :
```yaml
source:
  type: RabbitMQ
  serviceName: rabbitmq-prod
  serviceConnection:
    config:
      type: RabbitMQ
      username: <username>
      password: <password>
      hostPort: localhost:5672
```

---

## 🔧 10. Orchestration Systems

### Apache Airflow
- **Capacités** : DAGs, Tasks, Lineage
- **Configuration** :
```yaml
source:
  type: Airflow
  serviceName: airflow-prod
  serviceConnection:
    config:
      type: Airflow
      hostPort: http://localhost:8080
      connection:
        type: Backend
```

### Dagster
- **Capacités** : Jobs, Assets, Lineage
- **Configuration** :
```yaml
source:
  type: Dagster
  serviceName: dagster-prod
  serviceConnection:
    config:
      type: Dagster
      host: localhost
      port: 3000
```

### Prefect
- **Capacités** : Flows, Tasks
- **Configuration** :
```yaml
source:
  type: Prefect
  serviceName: prefect-prod
  serviceConnection:
    config:
      type: Prefect
      hostPort: http://localhost:4200
```

---

## 📊 11. BI Tools

### Tableau
- **Capacités** : Dashboards, Workbooks, Charts, Lineage
- **Configuration** :
```yaml
source:
  type: Tableau
  serviceName: tableau-prod
  serviceConnection:
    config:
      type: Tableau
      hostPort: https://tableau.company.com
      username: <username>
      password: <password>
      siteName: <site>
```

### Power BI
- **Capacités** : Reports, Dashboards, Datasets, Lineage
- **Configuration** :
```yaml
source:
  type: PowerBI
  serviceName: powerbi-prod
  serviceConnection:
    config:
      type: PowerBI
      clientId: <client_id>
      clientSecret: <client_secret>
      tenantId: <tenant_id>
```

### Looker
- **Capacités** : Looks, Dashboards, Explores, Lineage
- **Configuration** :
```yaml
source:
  type: Looker
  serviceName: looker-prod
  serviceConnection:
    config:
      type: Looker
      clientId: <client_id>
      clientSecret: <client_secret>
      hostPort: https://looker.company.com
```

### Superset
- **Capacités** : Dashboards, Charts, Datasets
- **Configuration** :
```yaml
source:
  type: Superset
  serviceName: superset-prod
  serviceConnection:
    config:
      type: Superset
      hostPort: http://localhost:8088
      connection:
        username: <username>
        password: <password>
```

---

## 🎯 Agents Recommandés pour Votre Architecture

### Déjà Actifs ✅
1. **Dremio Metadata** - Metadata + Profiling + Classification
2. **DBT** - Transformations + Lineage + Tests

### À Ajouter 🎯

#### Haute Priorité
1. **PostgreSQL Metadata** - Pour PostgreSQL_BusinessDB
   - Pourquoi : Complète les données Dremio avec source originale
   - Bénéfice : Double validation, détection des changements
   
2. **MinIO/S3 Metadata** - Pour le bucket MinIO
   - Pourquoi : Traçage des fichiers sources (CSV, Parquet)
   - Bénéfice : Lineage complet (fichier → table)

3. **Usage Agent (Dremio)** - Query analytics
   - Pourquoi : Identifier les tables les plus utilisées
   - Bénéfice : Optimisation des performances

#### Priorité Moyenne
4. **Airflow Metadata** - DAGs actuels
   - Pourquoi : Documentation des workflows
   - Bénéfice : Lineage orchestration

5. **Superset Metadata** - Dashboards (si utilisé)
   - Pourquoi : Traçabilité des visualisations
   - Bénéfice : Lineage end-to-end

#### Priorité Basse
6. **Data Quality Agent** - Tests custom
   - Pourquoi : Validation automatique des données
   - Bénéfice : Alertes qualité

---

## 📋 Récapitulatif par Catégorie

| Catégorie | Agents Disponibles | Implémentés | À Ajouter |
|-----------|-------------------|-------------|-----------|
| **Databases** | 15+ | Dremio ✅ | PostgreSQL 🎯 |
| **Storage** | 3 | - | MinIO/S3 🎯 |
| **Profiling** | 10+ | Dremio ✅ | - |
| **Classification** | 10+ | Dremio ✅ | - |
| **Usage** | 5 | - | Dremio 🎯 |
| **Lineage** | 5 | DBT ✅ | - |
| **Data Quality** | Tous | - | Custom 💡 |
| **Orchestration** | 3 | - | Airflow 💡 |
| **BI Tools** | 4 | - | Superset 💡 |
| **Messaging** | 3 | - | - |

**Légende** :
- ✅ Déjà implémenté et actif
- 🎯 Recommandé à ajouter en priorité
- 💡 À considérer selon besoins

---

## 🚀 Prochaines Étapes

### Phase 1 : Activer les fonctionnalités Dremio (Immédiat)
1. ✅ Metadata - Déjà actif
2. ⏳ Profiling - À activer dans l'UI
3. ⏳ Classification - À activer dans l'UI

### Phase 2 : Ajouter PostgreSQL (1-2 jours)
1. Créer connecteur PostgreSQL dans OpenMetadata
2. Configurer l'ingestion metadata
3. Activer le profiling
4. Comparer avec Dremio pour validation

### Phase 3 : Ajouter MinIO/S3 (1-2 jours)
1. Configurer connecteur S3 (compatible MinIO)
2. Scanner le bucket opendata
3. Établir lineage fichiers → tables

### Phase 4 : Usage Analytics (1 semaine)
1. Implémenter collecte query logs Dremio
2. Créer agent Usage custom
3. Dashboard d'utilisation

### Phase 5 : Orchestration (optionnel)
1. Connecter Airflow actuel
2. Documenter les DAGs
3. Lineage orchestration

---

## 📚 Ressources

- **Documentation OpenMetadata** : https://docs.open-metadata.org/
- **Connectors List** : https://docs.open-metadata.org/connectors
- **API Reference** : https://docs.open-metadata.org/sdk/python

---

✅ **Document créé le** : 2025-10-20
📝 **Version** : 1.0
🎯 **Objectif** : Cartographie complète des agents disponibles pour enrichir le catalogue OpenMetadata
