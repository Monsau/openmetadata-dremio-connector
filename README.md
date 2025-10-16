# 🚀 Dremio Connector pour OpenMetadata#
🚀 DREMIO + OPENMETADATA - INTÉGRATION COMPLÈTE



> Connecteur personnalisé pour extraire les métadonnées de Dremio vers OpenMetadata avec 4 agents intégrés.



---> Connecteur personnalisé pour extraire les métadonnées de Dremio vers OpenMetadata avec 4 agents intégrés.



## 📌 Vue d'ensemble



Ce projet fournit un **connecteur OpenMetadata pour Dremio** avec :---> Connecteur personnalisé pour extraire les métadonnées de Dremio vers OpenMetadata avec 4 agents intégrés.



- **Topologie complète** : Databases → Schemas → Tables

- **4 agents automatiques** : Metadata, Profiler, Lineage, dbt

- **Auto-découverte** : Les agents apparaissent dans l'UI OpenMetadata## 📌 Vue d'ensemble

- **Compatible** : OpenMetadata 1.9.7



---

Ce projet fournit un connecteur OpenMetadata pour Dremio avec :---Connecteur personnalisé OpenMetadata pour Dremio avec support de la topologie complète (Databases → Schemas → Tables) et 4 agents intégrés auto-découverts.

## ✨ Les 4 Agents

- **Topologie complète** : Databases → Schemas → Tables

| Agent | Rôle |

|-------|------|- **4 agents automatiques** : Metadata, Profiler, Lineage, dbt

| 🔍 **Metadata** | Extrait noms, types, descriptions des tables |

| 📊 **Profiler** | Analyse statistiques, distributions, qualité des données |- **Auto-découverte** : Les agents apparaissent dans l'UI OpenMetadata

| 🔗 **Lineage** | Trace les dépendances entre tables (sources → cibles) |

| 🎨 **dbt** | Intègre modèles, tests et documentation dbt |- **Compatible** : OpenMetadata 1.9.7## 📌 Vue d'ensemble



---



## 📋 Prérequis---



Avant de commencer, assurez-vous d'avoir :



| Composant | Version | Note |## ✨ Les 4 AgentsCe projet fournit un connecteur OpenMetadata pour Dremio avec :## ✨ FonctionnalitésConnecteur personnalisé OpenMetadata pour Dremio avec support de la topologie complète et 4 agents intégrés.Environnement complet **Dremio 26** + **OpenMetadata 1.9.7** avec **OpenSearch** pour l'ingestion et la gestion des métadonnées.

|-----------|---------|------|

| Docker | 20.x+ | Obligatoire |

| Docker Compose | 2.x+ | Obligatoire |

| Dremio | 24.x+ | Doit être accessible || Agent | Rôle |- **Topologie complète** : Databases → Schemas → Tables

| RAM disponible | 8GB min | 16GB recommandé |

|-------|------|

**Ports utilisés :**

- `3306` : MySQL (OpenMetadata DB)| 🔍 **Metadata** | Extrait noms, types, descriptions des tables |- **4 agents automatiques** : Metadata, Profiler, Lineage, dbt

- `8080` : Airflow (orchestration)

- `8585` : OpenMetadata UI| 📊 **Profiler** | Analyse statistiques, distributions, qualité des données |

- `9201` : Elasticsearch (search)

| 🔗 **Lineage** | Trace les dépendances entre tables (sources → cibles) |- **Auto-découverte** : Les agents apparaissent dans l'UI OpenMetadata

---

| 🎨 **dbt** | Intègre modèles, tests et documentation dbt |

## 🚀 Installation rapide

- **Compatible** : OpenMetadata 1.9.7- ✅ **Topologie complète** : Extraction de Databases → Schemas → Tables

### Étape 1 : Cloner et démarrer

---

```bash

# Cloner le dépôt

git clone https://github.com/Monsau/openmetadata-dremio-connector.git

cd openmetadata-dremio-connector## 📋 Prérequis



# Lancer l'environnement complet---- ✅ **4 Agents intégrés** :

docker compose up -d --build

```Avant de commencer, assurez-vous d'avoir :



### Étape 2 : Attendre le démarrage



Le premier démarrage prend **2-3 minutes**. Surveillez les logs :| Composant | Version | Note |



```bash|-----------|---------|------|## ✨ Les 4 Agents  - **MetadataAgent** : Extraction des métadonnées (noms, types, descriptions)## 🎯 Fonctionnalités## � **Architecture**

# Vérifier l'état

docker ps| Docker | 20.x+ | Obligatoire |



# Suivre les logs OpenMetadata| Docker Compose | 2.x+ | Obligatoire |

docker logs -f openmetadata_server

| Dremio | 24.x+ | Doit être accessible |

# Suivre les logs Airflow

docker logs -f openmetadata_ingestion| RAM disponible | 8GB min | 16GB recommandé || Agent | Rôle |  - **ProfilerAgent** : Profilage des données (statistiques, distribution)

```



✅ **Prêt quand vous voyez :**

- `OpenMetadata :: Version :: 1.9.7` dans les logs du serveur**Ports utilisés :**|-------|------|

- `Airflow Webserver: Running` dans les logs d'ingestion

- `3306` : MySQL (OpenMetadata DB)

### Étape 3 : Vérifier l'installation

- `8080` : Airflow (orchestration)| 🔍 **Metadata** | Extrait noms, types, descriptions des tables |  - **LineageAgent** : Traçabilité des données (sources, transformations)

```bash

# Tester le connecteur- `8585` : OpenMetadata UI

docker exec openmetadata_ingestion python -c "from dremio_connector.dremio_source import DatabaseServiceSource; print('✅ Connecteur chargé')"

- `9201` : Elasticsearch (search)| 📊 **Profiler** | Analyse statistiques, distributions, qualité des données |

# Tester les agents

docker exec openmetadata_ingestion python -c "from dremio_connector.agents.metadata_agent import MetadataAgent; print('✅ Agents disponibles')"

```

---| 🔗 **Lineage** | Trace les dépendances entre tables (sources → cibles) |  - **DbtAgent** : Intégration dbt (modèles, tests, documentation)

---



## 🎯 Configuration via l'interface UI

## 🚀 Installation rapide| 🎨 **dbt** | Intègre modèles, tests et documentation dbt |

### 🔐 Étape 1 : Connexion



1. Ouvrir : **http://localhost:8585**

2. Se connecter :### Étape 1 : Cloner et démarrer- ✅ **Auto-découverte** : Les agents apparaissent automatiquement dans l'UI OpenMetadata- ✅ **Topologie complète** : Databases → Schemas → Tables```

   - Username : `admin`

   - Password : `admin`



---```bash---



### 📦 Étape 2 : Créer le service Dremio# Cloner le dépôt



1. Cliquer sur **⚙️ Settings** (en haut à droite)git clone https://github.com/Monsau/openmetadata-dremio-connector.git- ✅ **Yield natif** : Utilise le système de yield d'OpenMetadata (pas de post-processing)

2. Menu gauche → **Databases**

3. Bouton **+ Add Database Service**cd openmetadata-dremio-connector

4. Sélectionner **Dremio** dans la liste

## 📋 Prérequis

**Configuration du service :**

# Lancer l'environnement complet

```yaml

# Informations généralesdocker compose up -d --build- ✅ **100% compatible** : OpenMetadata 1.9.7- ✅ **4 Agents intégrés** :dremio/

Name: dremio-prod

Display Name: Dremio Production```



# ConnexionAvant de commencer, assurez-vous d'avoir :

Host: host.docker.internal    # Si Dremio est en local

Port: 9047### Étape 2 : Attendre le démarrage

Username: admin

Password: admin123



# OptionsLe premier démarrage prend **2-3 minutes**. Surveillez les logs :

Use SSL: false

```| Composant | Version | Note |



5. Cliquer **Save**```bash



---# Vérifier l'état|-----------|---------|------|## 📋 Prérequis  - MetadataAgent : Extraction des métadonnées├── env/                     # 🔧 Environnement Dremio



### 🔄 Étape 3 : Ingestion Metadata (obligatoire)docker ps



> Cette étape extrait la structure : databases, schemas, tables, colonnes| Docker | 20.x+ | Obligatoire |



1. Page du service **Dremio** → onglet **Ingestions**# Suivre les logs OpenMetadata

2. Cliquer **+ Add Ingestion**

3. Sélectionner **Metadata**docker logs -f openmetadata_server| Docker Compose | 2.x+ | Obligatoire |



**Configuration :**



```yaml# Suivre les logs Airflow| Dremio | 24.x+ | Doit être accessible |

Name: dremio-metadata

docker logs -f openmetadata_ingestion

# Filtres d'inclusion (optionnel)

Database Pattern: *           # * = tout```| RAM disponible | 8GB min | 16GB recommandé |- **Docker** & **Docker Compose** installés  - ProfilerAgent : Profilage des données│   ├── docker-compose.yml   # Dremio + PostgreSQL + OpenSearch + MinIO

Schema Pattern: *

Table Pattern: *



# Filtres d'exclusion (optionnel)✅ **Prêt quand vous voyez :**

Exclude Databases: sys, INFORMATION_SCHEMA

Exclude Schemas: tmp_*- `OpenMetadata :: Version :: 1.9.7` dans les logs du serveur



# Planification- `Airflow Webserver: Running` dans les logs d'ingestion**Ports utilisés :**- **Dremio** en cours d'exécution (par défaut sur `localhost:9047`)

Schedule Type: Manual         # ou Daily, Weekly

```



4. Cliquer **Save**### Étape 3 : Vérifier l'installation- `3306` : MySQL (OpenMetadata DB)

5. Cliquer **▶️ Run** pour démarrer



⏱️ **Durée** : 1-5 minutes selon la taille de votre catalogue Dremio

```bash- `8080` : Airflow (orchestration)- **8GB RAM minimum** (16GB recommandé)  - LineageAgent : Traçabilité des données│   └── data/                # Données d'initialisation

---

# Tester le connecteur

### 📊 Étape 4 : Ingestion Profiler (optionnel)

docker exec openmetadata_ingestion python -c "from dremio_connector.dremio_source import DatabaseServiceSource; print('✅ Connecteur chargé')"- `8585` : OpenMetadata UI

> Analyse la qualité des données : statistiques, null values, distributions



1. Page du service **Dremio** → onglet **Ingestions**

2. Cliquer **+ Add Ingestion**# Tester les agents- `9201` : Elasticsearch (search)- **Ports disponibles** : 3306, 8080, 8585, 9201

3. Sélectionner **Profiler**

docker exec openmetadata_ingestion python -c "from dremio_connector.agents.metadata_agent import MetadataAgent; print('✅ Agents disponibles')"

**Configuration :**

```

```yaml

Name: dremio-profiler



# Échantillonnage------  - DbtAgent : Intégration dbt├── ingestion/               # � Module d'ingestion OpenMetadata

Profile Sample: 100%          # ou 50%, 10% pour grandes tables

Max Sample Rows: 10000        # Limite par table



# Options## 🎯 Configuration via l'interface UI

Enable Sample Data: true      # Affiche exemples de données

Thread Count: 5               # Parallélisation

Timeout: 3600                 # 1 heure max

### 🔐 Étape 1 : Connexion## 🚀 Installation rapide## 🚀 Installation

# Filtres (optionnel)

Include Tables: sales_*, customer_*

```

1. Ouvrir : **http://localhost:8585**

4. Cliquer **Save** puis **▶️ Run**

2. Se connecter :

⏱️ **Durée** : Variable (dépend du volume de données)

   - Username : `admin`### Étape 1 : Cloner et démarrer- ✅ **Auto-découverte** : Les agents sont découverts automatiquement dans l'UI OpenMetadata│   ├── docker-compose.yml   # OpenMetadata + OpenSearch

---

   - Password : `admin`

### 🔗 Étape 5 : Ingestion Lineage (optionnel)



> Trace les dépendances entre tables (sources → transformations → cibles)

---

1. Page du service **Dremio** → onglet **Ingestions**

2. Cliquer **+ Add Ingestion**```bash### 1️⃣ Cloner le projet

3. Sélectionner **Lineage**

### 📦 Étape 2 : Créer le service Dremio

**Configuration :**

# Cloner le dépôt

```yaml

Name: dremio-lineage1. Cliquer sur **⚙️ Settings** (en haut à droite)



# Options de traçabilité2. Menu gauche → **Databases**git clone https://github.com/Monsau/dremio_connector.git- ✅ **Yield natif** : Utilise le système de yield d'OpenMetadata (pas de post-processing)│   └── dremio_ingestion.py  # Script d'ingestion principal

Query Log Duration: 7         # Jours d'historique à analyser

```3. Bouton **+ Add Database Service**



4. Cliquer **Save** puis **▶️ Run**4. Sélectionner **Dremio** dans la listecd dremio_connector



---



### 🎨 Étape 6 : Ingestion dbt (optionnel)**Configuration du service :**```bash



> Intègre vos modèles, tests et documentation dbt



**Prérequis** : Vous devez avoir un projet dbt connecté à Dremio```yaml# Lancer l'environnement complet



1. Page du service **Dremio** → onglet **Ingestions**# Informations générales

2. Cliquer **+ Add Ingestion**

3. Sélectionner **dbt**Name: dremio-proddocker compose up -d --buildgit clone https://github.com/Monsau/dremio_connector.git└── requirements.txt         # Dépendances Python



**Configuration :**Display Name: Dremio Production



```yaml```

Name: dremio-dbt

# Connexion

# Chemin vers votre projet dbt

dbt Project Directory: /path/to/dbt/projectHost: host.docker.internal    # Si Dremio est en localcd dremio_connector

dbt Catalog File: target/catalog.json

dbt Manifest File: target/manifest.jsonPort: 9047

```

Username: admin### Étape 2 : Attendre le démarrage

4. Cliquer **Save** puis **▶️ Run**

Password: admin123

---

```## 📋 Prérequis```

## 🔍 Explorer les résultats

# Options

### Voir les métadonnées extraites

Use SSL: falseLe premier démarrage prend **2-3 minutes**. Surveillez les logs :

1. Menu principal → **🔍 Explore**

2. Filtrer par **Service** : `dremio-prod````



Vous verrez :

- 📁 **Databases** : Toutes vos bases Dremio

- 📂 **Schemas** : Organisation par schémas5. Cliquer **Save**

- 📋 **Tables** : Liste de toutes les tables avec métadonnées

```bash

### Consulter les profils de données

---

1. Cliquer sur une **table**

2. Onglet **Profiler**# Vérifier l'état### 2️⃣ Lancer l'environnement



Vous verrez :### 🔄 Étape 3 : Ingestion Metadata (obligatoire)

- Nombre total de lignes

- Statistiques par colonne (min, max, moyenne, médiane)docker ps

- Distribution des valeurs

- Pourcentage de valeurs nulles> Cette étape extrait la structure : databases, schemas, tables, colonnes

- Exemples de données



### Visualiser le lineage

1. Page du service **Dremio** → onglet **Ingestions**

1. Cliquer sur une **table**

2. Onglet **Lineage**2. Cliquer **+ Add Ingestion**# Suivre les logs OpenMetadata



Vous verrez :3. Sélectionner **Metadata**

- Graphe visuel des dépendances

- Tables sources (upstream)docker logs -f openmetadata_server```bash- Docker & Docker Compose### **Services Déployés**

- Tables dérivées (downstream)

- Transformations appliquées**Configuration :**



---



## 🛠️ Utilisation via script (alternative)```yaml



Si vous préférez automatiser, utilisez `activate_agents.py` :Name: dremio-metadata# Suivre les logs Airflowdocker compose up -d --build



```bash

# Activer uniquement Metadata

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \# Filtres d'inclusion (optionnel)docker logs -f openmetadata_ingestion

  --metadata \

  --dremio-user admin \Database Pattern: *           # * = tout

  --dremio-pass admin123

Schema Pattern: *``````- Dremio en cours d'exécution (par défaut sur localhost:9047)- **Dremio 26** : Moteur de requête (port 9047)

# Activer Metadata + Profiler

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \Table Pattern: *

  --metadata --profiler \

  --dremio-user admin \

  --dremio-pass admin123

# Filtres d'exclusion (optionnel)

# Activer tous les agents

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \Exclude Databases: sys, INFORMATION_SCHEMA✅ **Prêt quand vous voyez :**

  --all \

  --dremio-user admin \Exclude Schemas: tmp_*

  --dremio-pass admin123

```- `OpenMetadata :: Version :: 1.9.7` dans les logs du serveur



---# Planification



## 🐛 DépannageSchedule Type: Manual         # ou Daily, Weekly- `Airflow Webserver: Running` dans les logs d'ingestionCette commande va :- **PostgreSQL** : Base de données business (port 5434)  



### Problème : Le serveur ne démarre pas```



**Symptômes :**

- `docker ps` montre `openmetadata_server` en `Restarting`

- Logs affichent des erreurs MySQL4. Cliquer **Save**



**Solutions :**5. Cliquer **▶️ Run** pour démarrer### Étape 3 : Vérifier l'installation- 🔨 **Builder** l'image custom avec le connecteur Dremio



```bash

# 1. Vérifier que MySQL est prêt

docker exec openmetadata_mysql mysql -uroot -ppassword -e "SHOW DATABASES;"⏱️ **Durée** : 1-5 minutes selon la taille de votre catalogue Dremio



# 2. Redémarrer proprement

docker compose down -v

docker compose up -d --build---```bash- 🗄️ **Initialiser** MySQL (base de données OpenMetadata)## 🚀 Installation- **OpenSearch** : Recherche et analytics (port 9201)



# 3. Vérifier les logs détaillés

docker logs openmetadata_server --tail 200

```### 📊 Étape 4 : Ingestion Profiler (optionnel)# Tester le connecteur



---



### Problème : Le connecteur n'apparaît pas dans l'UI> Analyse la qualité des données : statistiques, null values, distributionsdocker exec openmetadata_ingestion python -c "from dremio_connector.dremio_source import DatabaseServiceSource; print('✅ Connecteur chargé')"- 🔍 **Lancer** Elasticsearch (moteur de recherche)



**Symptômes :**

- "Dremio" absent de la liste des connecteurs

- Erreur lors de la création du service1. Page du service **Dremio** → onglet **Ingestions**



**Solutions :**2. Cliquer **+ Add Ingestion**



```bash3. Sélectionner **Profiler**# Tester les agents- 🔄 **Migrer** automatiquement la base de données- **MinIO** : Stockage objet S3 (ports 9000/9001)

# 1. Vérifier que l'image custom est utilisée

docker images | grep custom-dremio



# 2. Vérifier l'installation du package**Configuration :**docker exec openmetadata_ingestion python -c "from dremio_connector.agents.metadata_agent import MetadataAgent; print('✅ Agents disponibles')"

docker exec openmetadata_ingestion pip list | grep dremio-connector



# 3. Rebuild complet de l'image

docker compose down```yaml```- 🖥️ **Démarrer** le serveur OpenMetadata (port 8585)

docker compose build --no-cache ingestion

docker compose up -dName: dremio-profiler

```



---

# Échantillonnage

### Problème : Les agents ne sont pas découverts

Profile Sample: 100%          # ou 50%, 10% pour grandes tables---- ⚙️ **Démarrer** Airflow avec le connecteur custom (port 8080)### 1. Cloner le projet- **OpenMetadata 1.9.7** : Plateforme de métadonnées (port 8585)

**Symptômes :**

- Seulement "Metadata" apparaît dans l'UIMax Sample Rows: 10000        # Limite par table

- Profiler/Lineage/dbt absents



**Explication :**

Les agents sont découverts automatiquement après la création du service.# Options



**Solutions :**Enable Sample Data: true      # Affiche exemples de données## 🎯 Configuration via l'interface UI



```bashThread Count: 5               # Parallélisation

# 1. Vérifier manuellement les imports

docker exec openmetadata_ingestion python -c "Timeout: 3600                 # 1 heure max

from dremio_connector.agents.metadata_agent import MetadataAgent

from dremio_connector.agents.profiler_agent import ProfilerAgent

from dremio_connector.agents.lineage_agent import LineageAgent

from dremio_connector.agents.dbt_agent import DbtAgent# Filtres (optionnel)### 🔐 Étape 1 : Connexion### 3️⃣ Attendre le démarrage complet

print('✅ Tous les agents OK')

"Include Tables: sales_*, customer_*



# 2. Attendre 1-2 minutes```

# Le système peut prendre du temps pour détecter les agents



# 3. Vérifier les logs Airflow

docker logs openmetadata_ingestion | grep -i agent4. Cliquer **Save** puis **▶️ Run**1. Ouvrir : **http://localhost:8585**

```



---

⏱️ **Durée** : Variable (dépend du volume de données)2. Se connecter :

### Problème : Erreur de connexion à Dremio



**Symptômes :**

- L'ingestion échoue immédiatement---   - Username : `admin`Le premier démarrage prend **2-3 minutes**. Vérifiez l'état des services :```bash## ⚡ **Démarrage Rapide**

- Erreur "Connection refused" ou "Timeout"



**Solutions :**

### 🔗 Étape 5 : Ingestion Lineage (optionnel)   - Password : `admin`

```bash

# 1. Tester la connectivité depuis le container

docker exec openmetadata_ingestion curl http://host.docker.internal:9047/apiv2/server_status

> Trace les dépendances entre tables (sources → transformations → cibles)

# 2. Si Dremio est dans Docker, vérifier le réseau

docker network ls

docker network inspect openmetadata-dremio-connector_app_net

1. Page du service **Dremio** → onglet **Ingestions**---

# 3. Vérifier les credentials Dremio

# Se connecter manuellement à http://localhost:90472. Cliquer **+ Add Ingestion**

```

3. Sélectionner **Lineage**```bashgit clone https://github.com/Monsau/dremio_connector.git

**Configuration réseau :**

- Si Dremio est sur **localhost** : utiliser `host.docker.internal`

- Si Dremio est dans **Docker** : utiliser le nom du service ou l'IP

- Si Dremio est **distant** : utiliser l'IP publique**Configuration :**### 📦 Étape 2 : Créer le service Dremio



---



### Problème : Ingestion très lente```yaml# Vérifier que tous les containers sont UP et healthy



**Symptômes :**Name: dremio-lineage

- L'ingestion tourne pendant des heures

- Timeout sur certaines tables1. Cliquer sur **⚙️ Settings** (en haut à droite)



**Solutions :**# Options de traçabilité



1. **Réduire l'échantillonnage du Profiler** :Query Log Duration: 7         # Jours d'historique à analyser2. Menu gauche → **Databases**docker pscd dremio_connector### **1. Démarrer l'environnement Dremio**

   ```yaml

   Profile Sample: 10%        # Au lieu de 100%```

   Max Sample Rows: 1000      # Au lieu de 10000

   ```3. Bouton **+ Add Database Service**



2. **Filtrer les tables** :4. Cliquer **Save** puis **▶️ Run**

   ```yaml

   Include Tables: prod_*, dim_*, fact_*4. Sélectionner **Dremio** dans la liste

   Exclude Tables: tmp_*, staging_*

   ```---



3. **Augmenter le timeout** :

   ```yaml

   Timeout: 7200              # 2 heures au lieu de 1### 🎨 Étape 6 : Ingestion dbt (optionnel)

   Thread Count: 10           # Plus de parallélisme

   ```**Configuration du service :**# Suivre les logs du serveur``````powershell



---> Intègre vos modèles, tests et documentation dbt



## ⚙️ Configuration avancée



### Changer les ports**Prérequis** : Vous devez avoir un projet dbt connecté à Dremio



Éditer `docker-compose.yml` :```yamldocker logs -f openmetadata_server



```yaml1. Page du service **Dremio** → onglet **Ingestions**

services:

  openmetadata-server:2. Cliquer **+ Add Ingestion**# Informations générales

    ports:

      - "8585:8585"  # Changer le premier 8585 → votre port3. Sélectionner **dbt**

  

  ingestion:Name: dremio-prodcd env

    ports:

      - "8080:8080"  # Changer le premier 8080 → votre port**Configuration :**

```

Display Name: Dremio Production

Puis redémarrer :

```yaml

```bash

docker compose downName: dremio-dbt# Suivre les logs d'Airflow

docker compose up -d

```



---# Chemin vers votre projet dbt# Connexion



### Persister les donnéesdbt Project Directory: /path/to/dbt/project



Les volumes Docker sont créés automatiquement. Pour voir l'utilisation :dbt Catalog File: target/catalog.jsonHost: host.docker.internal    # Si Dremio est en localdocker logs -f openmetadata_ingestion### 2. Lancer l'environnementdocker-compose up -d



```bashdbt Manifest File: target/manifest.json

# Lister les volumes

docker volume ls | grep openmetadata```Port: 9047



# Voir l'espace utilisé

docker system df -v

4. Cliquer **Save** puis **▶️ Run**Username: admin```

# Sauvegarder un volume

docker run --rm -v openmetadata-dremio-connector_mysql_data:/data -v $(pwd):/backup \

  busybox tar czf /backup/mysql_backup.tar.gz /data

```---Password: admin123



---



### Nettoyer complètement## 🔍 Explorer les résultats```



```bash

# ⚠️ ATTENTION : Supprime toutes les données

### Voir les métadonnées extraites# Options

# Arrêter et supprimer conteneurs + volumes

docker compose down -v



# Supprimer l'image custom1. Menu principal → **🔍 Explore**Use SSL: false✅ **C'est prêt quand** :

docker rmi openmetadata/ingestion:custom-dremio

2. Filtrer par **Service** : `dremio-prod`

# Supprimer les volumes orphelins

docker volume prune -f```

```

Vous verrez :

---

- 📁 **Databases** : Toutes vos bases Dremio- `openmetadata_server` affiche : `OpenMetadata :: Version :: 1.9.7````bash**Accès** : http://localhost:9047 (admin/admin123)

## 📖 Documentation complémentaire

- 📂 **Schemas** : Organisation par schémas

| Document | Description |

|----------|-------------|- 📋 **Tables** : Liste de toutes les tables avec métadonnées5. Cliquer **Save**

| [START_HERE.md](START_HERE.md) | Guide de démarrage détaillé |

| [AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md) | Architecture technique des agents |



---### Consulter les profils de données- `openmetadata_ingestion` affiche : `Airflow Webserver: Running on http://0.0.0.0:8080`



## 📊 Récapitulatif des ports



| Service | Port | URL | Description |1. Cliquer sur une **table**---

|---------|------|-----|-------------|

| MySQL | 3306 | - | Base de données OpenMetadata |2. Onglet **Profiler**

| Elasticsearch | 9201 | http://localhost:9201 | Moteur de recherche |

| OpenMetadata | 8585 | http://localhost:8585 | Interface web principale |docker compose up -d

| Airflow | 8080 | http://localhost:8080 | Orchestrateur d'ingestion |

Vous verrez :

---

- Nombre total de lignes### 🔄 Étape 3 : Ingestion Metadata (obligatoire)

## 🎉 Résultat attendu

- Statistiques par colonne (min, max, moyenne, médiane)

Après une installation réussie :

- Distribution des valeurs### 4️⃣ Vérifier l'installation du connecteur

| Vérification | URL | Credentials |

|--------------|-----|-------------|- Pourcentage de valeurs nulles

| ✅ OpenMetadata accessible | http://localhost:8585 | admin / admin |

| ✅ Airflow accessible | http://localhost:8080 | admin / admin |- Exemples de données> Cette étape extrait la structure : databases, schemas, tables, colonnes

| ✅ Connecteur Dremio visible | UI → Settings → Databases | - |

| ✅ 4 agents disponibles | UI → Service → Ingestions | - |

| ✅ Métadonnées Dremio importées | UI → Explore | - |

### Visualiser le lineage```### **2. Démarrer OpenMetadata**

---



## 🆘 Support

1. Cliquer sur une **table**1. Page du service **Dremio** → onglet **Ingestions**

En cas de problème :

2. Onglet **Lineage**

1. ✅ Vérifier les [Issues GitHub](https://github.com/Monsau/openmetadata-dremio-connector/issues)

2. ✅ Consulter la [documentation OpenMetadata](https://docs.open-metadata.org/)2. Cliquer **+ Add Ingestion**```bash

3. ✅ Ouvrir une nouvelle issue avec :

   - Version d'OpenMetadata (1.9.7)Vous verrez :

   - Logs complets (`docker logs <container>`)

   - Configuration du service Dremio (sans les passwords)- Graphe visuel des dépendances3. Sélectionner **Metadata**



---- Tables sources (upstream)



**🚀 Bon déploiement !**- Tables dérivées (downstream)# Vérifier que le connecteur Dremio est chargé```powershell


- Transformations appliquées

**Configuration :**

---

docker exec openmetadata_ingestion python -c "from dremio_connector.dremio_source import DatabaseServiceSource; print('✅ Connecteur OK')"

## 🛠️ Utilisation via script (alternative)

```yaml

Si vous préférez automatiser, utilisez `activate_agents.py` :

Name: dremio-metadataCela va :cd ingestion  

```bash

# Activer uniquement Metadata

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \

  --metadata \# Filtres d'inclusion (optionnel)# Vérifier que les agents sont disponibles

  --dremio-user admin \

  --dremio-pass admin123Database Pattern: *           # * = tout



# Activer Metadata + ProfilerSchema Pattern: *docker exec openmetadata_ingestion python -c "from dremio_connector.agents.metadata_agent import MetadataAgent; print('✅ Agents OK')"- Initialiser MySQL (port 3306)docker-compose up -d

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \

  --metadata --profiler \Table Pattern: *

  --dremio-user admin \

  --dremio-pass admin123```



# Activer tous les agents# Filtres d'exclusion (optionnel)

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \

  --all \Exclude Databases: sys, INFORMATION_SCHEMA- Lancer Elasticsearch (port 9201)```

  --dremio-user admin \

  --dremio-pass admin123Exclude Schemas: tmp_*

```

## 🎯 Utilisation via l'Interface UI (Recommandé)

---

# Planification

## 🐛 Dépannage

Schedule Type: Manual         # ou Daily, Weekly- Migrer la base de données OpenMetadata**Accès** : http://localhost:8585 (admin/admin)

### Problème : Le serveur ne démarre pas

```

**Symptômes :**

- `docker ps` montre `openmetadata_server` en `Restarting`### 🔐 Étape 1 : Se connecter à OpenMetadata

- Logs affichent des erreurs MySQL

4. Cliquer **Save**

**Solutions :**

5. Cliquer **▶️ Run** pour démarrer- Démarrer le serveur OpenMetadata (port 8585)

```bash

# 1. Vérifier que MySQL est prêt

docker exec openmetadata_mysql mysql -uroot -ppassword -e "SHOW DATABASES;"

⏱️ **Durée** : 1-5 minutes selon la taille de votre catalogue Dremio1. Ouvrir votre navigateur : **http://localhost:8585**

# 2. Redémarrer proprement

docker compose down -v

docker compose up -d --build

---2. Se connecter avec les credentials par défaut :- Démarrer Airflow avec le connecteur custom (port 8080)### **3. Lancer l'ingestion**

# 3. Vérifier les logs détaillés

docker logs openmetadata_server --tail 200

```

### 📊 Étape 4 : Ingestion Profiler (optionnel)   - **Username** : `admin`

---



### Problème : Le connecteur n'apparaît pas dans l'UI

> Analyse la qualité des données : statistiques, null values, distributions   - **Password** : `admin````powershell

**Symptômes :**

- "Dremio" absent de la liste des connecteurs

- Erreur lors de la création du service

1. Page du service **Dremio** → onglet **Ingestions**

**Solutions :**

2. Cliquer **+ Add Ingestion**

```bash

# 1. Vérifier que l'image custom est utilisée3. Sélectionner **Profiler**### 📦 Étape 2 : Créer le service Dremio### 3. Attendre le démarrage (environ 2-3 minutes)cd ingestion

docker images | grep custom-dremio



# 2. Vérifier l'installation du package

docker exec openmetadata_ingestion pip list | grep dremio-connector**Configuration :**



# 3. Rebuild complet de l'image

docker compose down

docker compose build --no-cache ingestion```yaml1. Aller dans **Settings** (⚙️ en haut à droite)python dremio_ingestion.py

docker compose up -d

```Name: dremio-profiler



---2. Cliquer sur **Databases** dans le menu de gauche



### Problème : Les agents ne sont pas découverts# Échantillonnage



**Symptômes :**Profile Sample: 100%          # ou 50%, 10% pour grandes tables3. Cliquer sur **+ Add Database Service**```bash```

- Seulement "Metadata" apparaît dans l'UI

- Profiler/Lineage/dbt absentsMax Sample Rows: 10000        # Limite par table



**Explication :**4. Sélectionner **Dremio** dans la liste

Les agents sont découverts automatiquement après la création du service.

# Options

**Solutions :**

Enable Sample Data: true      # Affiche exemples de données5. Configurer le service :# Vérifier que tous les services sont healthy

```bash

# 1. Vérifier manuellement les importsThread Count: 5               # Parallélisation

docker exec openmetadata_ingestion python -c "

from dremio_connector.agents.metadata_agent import MetadataAgentTimeout: 3600                 # 1 heure max

from dremio_connector.agents.profiler_agent import ProfilerAgent

from dremio_connector.agents.lineage_agent import LineageAgent

from dremio_connector.agents.dbt_agent import DbtAgent

print('✅ Tous les agents OK')# Filtres (optionnel)```yamldocker ps## 🎯 **Fonctionnalités**

"

Include Tables: sales_*, customer_*

# 2. Attendre 1-2 minutes

# Le système peut prendre du temps pour détecter les agents```Name: dremio-connector



# 3. Vérifier les logs Airflow

docker logs openmetadata_ingestion | grep -i agent

```4. Cliquer **Save** puis **▶️ Run**Display Name: Dremio Connector with Agents



---



### Problème : Erreur de connexion à Dremio⏱️ **Durée** : Variable (dépend du volume de données)



**Symptômes :**

- L'ingestion échoue immédiatement

- Erreur "Connection refused" ou "Timeout"---# Configuration de connexion# Vérifier les logs### **✅ Environment (env/)**



**Solutions :**



```bash### 🔗 Étape 5 : Ingestion Lineage (optionnel)Host: host.docker.internal  # ou l'IP de votre Dremio

# 1. Tester la connectivité depuis le container

docker exec openmetadata_ingestion curl http://host.docker.internal:9047/apiv2/server_status



# 2. Si Dremio est dans Docker, vérifier le réseau> Trace les dépendances entre tables (sources → transformations → cibles)Port: 9047docker logs openmetadata_server- Déploiement Docker complet Dremio (4 services)

docker network ls

docker network inspect openmetadata-dremio-connector_app_net



# 3. Vérifier les credentials Dremio1. Page du service **Dremio** → onglet **Ingestions**Username: admin

# Se connecter manuellement à http://localhost:9047

```2. Cliquer **+ Add Ingestion**



**Configuration réseau :**3. Sélectionner **Lineage**Password: admin123docker logs openmetadata_ingestion- Données business pré-chargées (2000+ enregistrements)

- Si Dremio est sur **localhost** : utiliser `host.docker.internal`

- Si Dremio est dans **Docker** : utiliser le nom du service ou l'IP

- Si Dremio est **distant** : utiliser l'IP publique

**Configuration :**

---



### Problème : Ingestion très lente

```yaml# Options avancées (optionnel)```- Configuration MinIO S3 automatique

**Symptômes :**

- L'ingestion tourne pendant des heuresName: dremio-lineage

- Timeout sur certaines tables

Use SSL: false

**Solutions :**

# Options de traçabilité

1. **Réduire l'échantillonnage du Profiler** :

   ```yamlQuery Log Duration: 7         # Jours d'historique à analyser```- OpenSearch prêt pour ingestion

   Profile Sample: 10%        # Au lieu de 100%

   Max Sample Rows: 1000      # Au lieu de 10000```

   ```



2. **Filtrer les tables** :

   ```yaml4. Cliquer **Save** puis **▶️ Run**

   Include Tables: prod_*, dim_*, fact_*

   Exclude Tables: tmp_*, staging_*6. Cliquer sur **Save**### 4. Accéder à OpenMetadata

   ```

---

3. **Augmenter le timeout** :

   ```yaml

   Timeout: 7200              # 2 heures au lieu de 1

   Thread Count: 10           # Plus de parallélisme### 🎨 Étape 6 : Ingestion dbt (optionnel)

   ```

### 🔄 Étape 3 : Créer l'ingestion Metadata### **✅ Ingestion (ingestion/)**

---

> Intègre vos modèles, tests et documentation dbt

## ⚙️ Configuration avancée



### Changer les ports

**Prérequis** : Vous devez avoir un projet dbt connecté à Dremio

Éditer `docker-compose.yml` :

1. Sur la page du service **Dremio**, cliquer sur **Ingestions**Ouvrir http://localhost:8585- Service OpenMetadata 1.9.7 complet

```yaml

services:1. Page du service **Dremio** → onglet **Ingestions**

  openmetadata-server:

    ports:2. Cliquer **+ Add Ingestion**2. Cliquer sur **+ Add Ingestion**

      - "8585:8585"  # Changer le premier 8585 → votre port

  3. Sélectionner **dbt**

  ingestion:

    ports:3. Sélectionner **Metadata**- Classification intelligente des colonnes

      - "8080:8080"  # Changer le premier 8080 → votre port

```**Configuration :**



Puis redémarrer :4. Configurer l'ingestion :



```bash```yaml

docker compose down

docker compose up -dName: dremio-dbt**Login par défaut :**- Profiling statistique avancé

```



---

# Chemin vers votre projet dbt```yaml

### Persister les données

dbt Project Directory: /path/to/dbt/project

Les volumes Docker sont créés automatiquement. Pour voir l'utilisation :

dbt Catalog File: target/catalog.jsonName: dremio-metadata-ingestion- Username: `admin`- Tests de qualité automatisés

```bash

# Lister les volumesdbt Manifest File: target/manifest.json

docker volume ls | grep openmetadata

```

# Voir l'espace utilisé

docker system df -v



# Sauvegarder un volume4. Cliquer **Save** puis **▶️ Run**# Configuration- Password: `admin`- Interface web complète

docker run --rm -v openmetadata-dremio-connector_mysql_data:/data -v $(pwd):/backup \

  busybox tar czf /backup/mysql_backup.tar.gz /data

```

---Include Filters:

---



### Nettoyer complètement

## 🔍 Explorer les résultats  - Database: *

```bash

# ⚠️ ATTENTION : Supprime toutes les données



# Arrêter et supprimer conteneurs + volumes### Voir les métadonnées extraites  - Schema: *

docker compose down -v



# Supprimer l'image custom

docker rmi openmetadata/ingestion:custom-dremio1. Menu principal → **🔍 Explore**  - Table: *## 📚 Utilisation## 🚀 **Utilisation**



# Supprimer les volumes orphelins2. Filtrer par **Service** : `dremio-prod`

docker volume prune -f

```



---Vous verrez :



## 📖 Documentation complémentaire- 📁 **Databases** : Toutes vos bases Dremio# Schedule (optionnel)



| Document | Description |- 📂 **Schemas** : Organisation par schémas

|----------|-------------|

| [START_HERE.md](START_HERE.md) | Guide de démarrage détaillé |- 📋 **Tables** : Liste de toutes les tables avec métadonnéesSchedule Type: Manual  # ou Daily, Weekly, etc.

| [AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md) | Architecture technique des agents |



---

### Consulter les profils de données```### Via l'interface UI (Recommandé)### **Exploration des Données**

## 📊 Récapitulatif des ports



| Service | Port | URL | Description |

|---------|------|-----|-------------|1. Cliquer sur une **table**

| MySQL | 3306 | - | Base de données OpenMetadata |

| Elasticsearch | 9201 | http://localhost:9201 | Moteur de recherche |2. Onglet **Profiler**

| OpenMetadata | 8585 | http://localhost:8585 | Interface web principale |

| Airflow | 8080 | http://localhost:8080 | Orchestrateur d'ingestion |5. Cliquer sur **Save**1. **Dremio** : Créer des datasets virtuels, requêtes SQL



---Vous verrez :



## 🎉 Résultat attendu- Nombre total de lignes6. Cliquer sur **▶️ Run** pour lancer l'ingestion



Après une installation réussie :- Statistiques par colonne (min, max, moyenne, médiane)



| Vérification | URL | Credentials |- Distribution des valeursSuivre le guide : [START_HERE.md](START_HERE.md)2. **OpenMetadata** : Explorer le catalogue, voir les profils

|--------------|-----|-------------|

| ✅ OpenMetadata accessible | http://localhost:8585 | admin / admin |- Pourcentage de valeurs nulles

| ✅ Airflow accessible | http://localhost:8080 | admin / admin |

| ✅ Connecteur Dremio visible | UI → Settings → Databases | - |- Exemples de données### 📊 Étape 4 : Créer l'ingestion Profiler (Optionnel)

| ✅ 4 agents disponibles | UI → Service → Ingestions | - |

| ✅ Métadonnées Dremio importées | UI → Explore | - |



---### Visualiser le lineage3. **Lignage** : Suivre les transformations de données



## 🆘 Support



En cas de problème :1. Cliquer sur une **table**1. Sur la page du service **Dremio**, onglet **Ingestions**



1. ✅ Vérifier les [Issues GitHub](https://github.com/Monsau/openmetadata-dremio-connector/issues)2. Onglet **Lineage**

2. ✅ Consulter la [documentation OpenMetadata](https://docs.open-metadata.org/)

3. ✅ Ouvrir une nouvelle issue avec :2. Cliquer sur **+ Add Ingestion**1. Aller dans Settings → Services

   - Version d'OpenMetadata (1.9.7)

   - Logs complets (`docker logs <container>`)Vous verrez :

   - Configuration du service Dremio (sans les passwords)

- Graphe visuel des dépendances3. Sélectionner **Profiler**

---

- Tables sources (upstream)

**🚀 Bon déploiement !**

- Tables dérivées (downstream)4. Configurer :2. Créer un service "Database" de type "Dremio"### **Architecture Technique**

- Transformations appliquées



---

```yaml3. Configurer la connexion à Dremio- **Orchestration** : Docker Compose

## 🛠️ Utilisation via script (alternative)

Name: dremio-profiler-ingestion

Si vous préférez automatiser, utilisez `activate_agents.py` :

4. Créer les ingestions (Metadata, Profiler, Lineage)- **Compute** : Dremio OSS 26.0

```bash

# Activer uniquement Metadata# Options de profilage

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \

  --metadata \Profile Sample: 100%  # ou moins pour de grandes tables- **Storage** : MinIO (S3), PostgreSQL 15

  --dremio-user admin \

  --dremio-pass admin123Enable Sample Data: true



# Activer Metadata + ProfilerThread Count: 5### Via le script Python- **Search** : OpenSearch 2.12.0

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \

  --metadata --profiler \```

  --dremio-user admin \

  --dremio-pass admin123- **Metadata** : OpenMetadata 1.9.7



# Activer tous les agents5. Cliquer sur **Save** puis **▶️ Run**

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \

  --all \```bash- **Language** : Python 3.9+

  --dremio-user admin \

  --dremio-pass admin123### 🔗 Étape 5 : Créer l'ingestion Lineage (Optionnel)

```

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \

---

1. Sur la page du service **Dremio**, onglet **Ingestions**

## 🐛 Dépannage

2. Cliquer sur **+ Add Ingestion**  --metadata \## 📊 **Ports Utilisés**

### Problème : Le serveur ne démarre pas

3. Sélectionner **Lineage**

**Symptômes :**

- `docker ps` montre `openmetadata_server` en `Restarting`4. Configurer selon vos besoins  --dremio-user admin \

- Logs affichent des erreurs MySQL

5. Cliquer sur **Save** puis **▶️ Run**

**Solutions :**

  --dremio-pass admin123 \| Service | Port | Interface |

```bash

# 1. Vérifier que MySQL est prêt### 🎨 Étape 6 : Créer l'ingestion dbt (Optionnel)

docker exec openmetadata_mysql mysql -uroot -ppassword -e "SHOW DATABASES;"

  --om-token <your-token>|---------|------|-----------|

# 2. Redémarrer proprement

docker compose down -vSi vous utilisez dbt avec Dremio :

docker compose up -d --build

```| Dremio | 9047 | Web UI |

# 3. Vérifier les logs détaillés

docker logs openmetadata_server --tail 2001. Sur la page du service **Dremio**, onglet **Ingestions**

```

2. Cliquer sur **+ Add Ingestion**| PostgreSQL | 5434 | Database |

---

3. Sélectionner **dbt**

### Problème : Le connecteur n'apparaît pas dans l'UI

4. Configurer le chemin vers vos fichiers dbt## 🏗️ Architecture| OpenSearch | 9201 | REST API |

**Symptômes :**

- "Dremio" absent de la liste des connecteurs5. Cliquer sur **Save** puis **▶️ Run**

- Erreur lors de la création du service

| MinIO | 9000/9001 | Console |

**Solutions :**

## 📊 Vérification des résultats

```bash

# 1. Vérifier que l'image custom est utilisée```| OpenMetadata | 8585 | Web UI |

docker images | grep custom-dremio

### Explorer les métadonnées ingérées

# 2. Vérifier l'installation du package

docker exec openmetadata_ingestion pip list | grep dremio-connectordremio_connector/



# 3. Rebuild complet de l'image1. Aller dans **Explore** (🔍 dans le menu principal)

docker compose down

docker compose build --no-cache ingestion2. Filtrer par **Service** : `dremio-connector`├── dremio_source.py          # Source principale avec yield## 🔍 **Monitoring**

docker compose up -d

```3. Vous devriez voir :



---   - 📁 Toutes vos **databases** Dremio├── manifest.json             # Déclaration du connecteur



### Problème : Les agents ne sont pas découverts   - 📂 Tous vos **schemas**



**Symptômes :**   - 📋 Toutes vos **tables**├── agents/                   # 4 agents### **Vérification des Services**

- Seulement "Metadata" apparaît dans l'UI

- Profiler/Lineage/dbt absents



**Explication :**### Voir les profils de données│   ├── metadata_agent.py```powershell

Les agents sont découverts automatiquement après la création du service.



**Solutions :**

1. Cliquer sur n'importe quelle **table**│   ├── profiler_agent.py# Statut des containers

```bash

# 1. Vérifier manuellement les imports2. Aller dans l'onglet **Profiler**

docker exec openmetadata_ingestion python -c "

from dremio_connector.agents.metadata_agent import MetadataAgent3. Vous verrez :│   ├── lineage_agent.pydocker ps

from dremio_connector.agents.profiler_agent import ProfilerAgent

from dremio_connector.agents.lineage_agent import LineageAgent   - Nombre de lignes

from dremio_connector.agents.dbt_agent import DbtAgent

print('✅ Tous les agents OK')   - Statistiques par colonne (min, max, moyenne, etc.)│   └── dbt_agent.py

"

   - Distribution des valeurs

# 2. Attendre 1-2 minutes

# Le système peut prendre du temps pour détecter les agents   - Données nulles├── clients/                  # Clients API# Santé Dremio



# 3. Vérifier les logs Airflow

docker logs openmetadata_ingestion | grep -i agent

```### Voir la traçabilité (Lineage)│   ├── dremio_client.pycurl http://localhost:9047/apiv2/server_status



---



### Problème : Erreur de connexion à Dremio1. Cliquer sur une **table**│   └── openmetadata_client.py



**Symptômes :**2. Aller dans l'onglet **Lineage**

- L'ingestion échoue immédiatement

- Erreur "Connection refused" ou "Timeout"3. Vous verrez le graphe des dépendances└── utils/                    # Utilitaires# Santé OpenMetadata  



**Solutions :**



```bash## 🛠️ Utilisation via Script Python (Alternative)```curl http://localhost:8585/api/v1/system/version

# 1. Tester la connectivité depuis le container

docker exec openmetadata_ingestion curl http://host.docker.internal:9047/apiv2/server_status



# 2. Si Dremio est dans Docker, vérifier le réseauSi vous préférez automatiser, utilisez le script `activate_agents.py` :

docker network ls

docker network inspect dremio_connector_app_net



# 3. Vérifier les credentials Dremio```bash## 🔧 Configuration# Santé OpenSearch

# Se connecter manuellement à http://localhost:9047

```# Activer uniquement l'agent Metadata



**Configuration réseau :**docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \curl http://localhost:9201/_cluster/health

- Si Dremio est sur **localhost** : utiliser `host.docker.internal`

- Si Dremio est dans **Docker** : utiliser le nom du service ou l'IP  --metadata \

- Si Dremio est **distant** : utiliser l'IP publique

  --dremio-user admin \### docker-compose.yml```

---

  --dremio-pass admin123

### Problème : Ingestion très lente



**Symptômes :**

- L'ingestion tourne pendant des heures# Activer tous les agents

- Timeout sur certaines tables

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py \Le fichier contient :## 🛠️ **Prérequis**

**Solutions :**

  --all \

1. **Réduire l'échantillonnage du Profiler** :

   ```yaml  --dremio-user admin \- **mysql** : Base de données OpenMetadata (port 3306)

   Profile Sample: 10%        # Au lieu de 100%

   Max Sample Rows: 1000      # Au lieu de 10000  --dremio-pass admin123

   ```

```- **elasticsearch** : Moteur de recherche (port 9201)- **Docker Desktop** (Windows/Mac/Linux)

2. **Filtrer les tables** :

   ```yaml

   Include Tables: prod_*, dim_*, fact_*

   Exclude Tables: tmp_*, staging_*## 🐛 Dépannage- **execute-migrate-all** : Migration automatique de la DB- **Python 3.9+** avec pip

   ```



3. **Augmenter le timeout** :

   ```yaml### ❌ Le serveur ne démarre pas- **openmetadata-server** : Serveur API (port 8585)- **8GB RAM minimum** (16GB recommandé)

   Timeout: 7200              # 2 heures au lieu de 1

   Thread Count: 10           # Plus de parallélisme

   ```

```bash- **ingestion** : Airflow + Connecteur custom (port 8080)- **10GB espace disque libre**

---

# Vérifier les logs

## ⚙️ Configuration avancée

docker logs openmetadata_server --tail 100

### Changer les ports



Éditer `docker-compose.yml` :

# Vérifier que MySQL est prêt### Variables d'environnement## � **Dépannage**

```yaml

services:docker exec openmetadata_mysql mysql -uroot -ppassword -e "SHOW DATABASES;"

  openmetadata-server:

    ports:

      - "8585:8585"  # Changer le premier 8585 → votre port

  # Redémarrer proprement

  ingestion:

    ports:docker compose down -vModifier dans `docker-compose.yml` si nécessaire :### **Redémarrage Complet**

      - "8080:8080"  # Changer le premier 8080 → votre port

```docker compose up -d --build



Puis redémarrer :```- Connexion Dremio par défaut : localhost:9047```powershell



```bash

docker compose down

docker compose up -d### ❌ Le connecteur n'apparaît pas dans l'UI- Credentials OpenMetadata : admin/admin# Arrêter tous les services

```



---

```bashcd env && docker-compose down

### Persister les données

# Vérifier que l'image custom est bien utilisée

Les volumes Docker sont créés automatiquement. Pour voir l'utilisation :

docker images | grep custom-dremio## 🐛 Dépannagecd ../ingestion && docker-compose down

```bash

# Lister les volumes

docker volume ls | grep dremio

# Vérifier que le connecteur est installé

# Voir l'espace utilisé

docker system df -vdocker exec openmetadata_ingestion pip list | grep dremio-connector



# Sauvegarder un volume### Les services ne démarrent pas# Redémarrer

docker run --rm -v dremio_connector_mysql_data:/data -v $(pwd):/backup \

  busybox tar czf /backup/mysql_backup.tar.gz /data# Rebuild de l'image

```

docker compose downcd ../env && docker-compose up -d

---

docker compose build --no-cache ingestion

### Nettoyer complètement

docker compose up -d```bashcd ../ingestion && docker-compose up -d

```bash

# ⚠️ ATTENTION : Supprime toutes les données```



# Arrêter et supprimer conteneurs + volumesdocker compose logs openmetadata_server```

docker compose down -v

### ❌ Les agents ne sont pas découverts

# Supprimer l'image custom

docker rmi openmetadata/ingestion:custom-dremiodocker compose logs ingestion



# Supprimer les volumes orphelinsLes agents sont **automatiquement découverts** par OpenMetadata. Si vous ne les voyez pas :

docker volume prune -f

``````## 🎉 **Résultat Final**



---1. Vérifier que le service Dremio est bien créé dans l'UI



## 📖 Documentation complémentaire2. Vérifier les logs d'Airflow :



| Document | Description |   ```bash

|----------|-------------|

| [START_HERE.md](START_HERE.md) | Guide de démarrage détaillé |   docker logs openmetadata_ingestion | grep -i dremio### Le connecteur n'apparaît pas dans l'UIAprès déploiement réussi :

| [AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md) | Architecture technique des agents |

   ```

---

3. Attendre 1-2 minutes que le système détecte les agents- **~2000 enregistrements** dans PostgreSQL

## 📊 Récapitulatif des ports



| Service | Port | URL | Description |

|---------|------|-----|-------------|### ❌ Erreur de connexion à Dremio```bash- **~15 tables** disponibles dans Dremio

| MySQL | 3306 | - | Base de données OpenMetadata |

| Elasticsearch | 9201 | http://localhost:9201 | Moteur de recherche |

| OpenMetadata | 8585 | http://localhost:8585 | Interface web principale |

| Airflow | 8080 | http://localhost:8080 | Orchestrateur d'ingestion |Si l'ingestion échoue avec une erreur de connexion :# Vérifier que le connecteur est bien installé- **Métadonnées complètes** dans OpenMetadata



---



## 🎉 Résultat attendu1. Vérifier que Dremio est accessible :docker exec openmetadata_ingestion python -c "from dremio_connector.dremio_source import DatabaseServiceSource; print('✅ OK')"- **Classification automatique** de ~100 colonnes



Après une installation réussie :   ```bash



| Vérification | URL | Credentials |   curl http://localhost:9047/apiv2/server_status```- **Lignage complet** des transformations

|--------------|-----|-------------|

| ✅ OpenMetadata accessible | http://localhost:8585 | admin / admin |   ```

| ✅ Airflow accessible | http://localhost:8080 | admin / admin |

| ✅ Connecteur Dremio visible | UI → Settings → Databases | - |- **Interface web** accessible pour exploration

| ✅ 4 agents disponibles | UI → Service → Ingestions | - |

| ✅ Métadonnées Dremio importées | UI → Explore | - |2. Si Dremio est dans Docker, utiliser `host.docker.internal` au lieu de `localhost`



---### Les agents ne sont pas visibles



## 🆘 Support3. Vérifier les credentials Dremio



En cas de problème :---



1. ✅ Vérifier les [Issues GitHub](https://github.com/Monsau/dremio_connector/issues)## 🔧 Configuration avancée

2. ✅ Consulter la [documentation OpenMetadata](https://docs.open-metadata.org/)

3. ✅ Ouvrir une nouvelle issue avec :Les agents apparaissent automatiquement dans l'UI lors de la création d'une ingestion.

   - Version d'OpenMetadata (1.9.7)

   - Logs complets (`docker logs <container>`)### Changer les ports

   - Configuration du service Dremio (sans les passwords)

**🚀 Stack moderne, performante et 100% open source pour la gestion des données !**

---

Éditer `docker-compose.yml` :### Redémarrage complet

**🚀 Bon déploiement !**



```yaml```bash

services:docker compose down -v

  openmetadata-server:docker compose up -d

    ports:```

      - "8585:8585"  # Changer 8585 → votre port

  ## 📖 Documentation

  ingestion:

    ports:- [START_HERE.md](START_HERE.md) : Guide de démarrage complet

      - "8080:8080"  # Changer 8080 → votre port- [AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md) : Architecture des agents

```

## 🧪 Tests

### Persister les données

```bash

Les volumes Docker sont automatiquement créés. Pour voir l'espace utilisé :# Dans le container

docker exec openmetadata_ingestion python /opt/airflow/activate_agents.py --help

```bash```

docker volume ls

docker system df -v## 🛠️ Développement

```

### Rebuild de l'image custom

### Nettoyer complètement

```bash

```bashdocker compose down

# Arrêter et supprimer tout (ATTENTION : perte de données)docker build -t openmetadata/ingestion:custom-dremio .

docker compose down -vdocker compose up -d

```

# Supprimer les images

docker rmi openmetadata/ingestion:custom-dremio### Modifier le connecteur

```

1. Éditer les fichiers dans `dremio_connector/`

## 📖 Documentation supplémentaire2. Rebuild l'image

3. Relancer les containers

- [START_HERE.md](START_HERE.md) : Guide de démarrage détaillé

- [AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md) : Architecture technique des agents## 📊 Ports utilisés



## 🆘 Support| Service | Port | Description |

|---------|------|-------------|

En cas de problème :| MySQL | 3306 | Base de données |

| Elasticsearch | 9201 | Moteur de recherche |

1. Vérifier les [Issues GitHub](https://github.com/Monsau/dremio_connector/issues)| OpenMetadata | 8585 | Interface web |

2. Consulter la [documentation OpenMetadata](https://docs.open-metadata.org/)| Airflow | 8080 | Orchestrateur |

3. Ouvrir une nouvelle issue avec :

   - Version d'OpenMetadata (1.9.7)## 📝 Licence

   - Logs complets (`docker logs`)

   - Configuration du service DremioMIT


## 📝 Ports utilisés

| Service | Port | Description |
|---------|------|-------------|
| MySQL | 3306 | Base de données OpenMetadata |
| Elasticsearch | 9201 | Moteur de recherche |
| OpenMetadata | 8585 | Interface web principale |
| Airflow | 8080 | Orchestrateur d'ingestion |

## 🎉 Résultat attendu

Après une installation réussie :

✅ **OpenMetadata** accessible sur http://localhost:8585  
✅ **Airflow** accessible sur http://localhost:8080  
✅ **Connecteur Dremio** visible dans la liste des connecteurs  
✅ **4 agents** disponibles pour l'ingestion  
✅ **Métadonnées Dremio** importées et explorables  

---

**🚀 Profitez de votre connecteur Dremio avec agents intégrés !**
