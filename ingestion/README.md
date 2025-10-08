# Dremio to OpenMetadata Ingestion

Ce projet permet d'ingérer automatiquement les sources Dremio et les VDS (Virtual Data Sets) vers OpenMetadata en tant que service de base de données personnalisé (CustomDB).

## 🎯 Fonctionnalités

- **Ingestion des sources Dremio** : MinIO, PostgreSQL, et autres sources configurées
- **Ingestion des VDS** : Virtual Data Sets créés dans Dremio
- **Service CustomDB** : Exposition dans OpenMetadata comme base de données personnalisée
- **Métadonnées complètes** : Schémas, tables, colonnes, types de données
- **Pipeline automatique** : Configuration de pipelines d'ingestion dans OpenMetadata
- **Support des vues** : Les VDS sont ingérés comme des vues SQL

## 🏗️ Architecture

```
Dremio                    OpenMetadata
├── Sources              ├── CustomDB Service
│   ├── MinIO       →    │   ├── Schema: MinIO
│   ├── PostgreSQL  →    │   ├── Schema: PostgreSQL
│   └── ...              │   └── Schema: ...
└── VDS             →    └── Schema: VDS_Analytics
    ├── View1            ├── View: View1
    ├── View2            ├── View: View2
    └── ...              └── View: ...
```

## 📋 Prérequis

1. **Dremio** en fonctionnement (localhost:9047 par défaut)
2. **OpenMetadata** en fonctionnement (localhost:8585 par défaut)
3. **Python 3.8+** avec pip
4. **Token JWT OpenMetadata** (voir section Configuration)

## 🚀 Installation

1. **Cloner/copier le projet** dans votre répertoire Dremio
2. **Installer les dépendances** :
   ```bash
   cd ingestion
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement** :
   ```bash
   cp .env.example .env
   # Éditer .env avec vos paramètres
   ```

## ⚙️ Configuration

### 1. Récupérer le Token JWT OpenMetadata

1. Ouvrir OpenMetadata dans le navigateur : `http://localhost:8585`
2. Aller dans **Settings** → **Bots** → **ingestion-bot**
3. Cliquer sur **"Generate New Token"**
4. Copier le token et l'ajouter dans votre fichier `.env`

### 2. Fichier .env

Créer un fichier `.env` basé sur `.env.example` :

```bash
# Dremio
DREMIO_HOST=localhost
DREMIO_PORT=9047
DREMIO_USERNAME=admin
DREMIO_PASSWORD=admin123

# OpenMetadata
OPENMETADATA_HOST=localhost
OPENMETADATA_PORT=8585
OPENMETADATA_JWT_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIs...
```

### 3. Configuration avancée

Le fichier `config/dremio_ingestion.yaml` permet de personnaliser :
- Filtres d'inclusion/exclusion
- Configuration des pipelines
- Mapping des types de données
- Options de performance

## 📖 Utilisation

### Mode interactif (recommandé pour débuter)

```bash
python example_usage.py
```

Ce mode :
1. Teste les connexions
2. Demande confirmation pour l'ingestion
3. Affiche les résultats

### Test des connexions uniquement

```bash
python example_usage.py --test-connections
```

### Analyse sans ingestion (dry-run)

```bash
python example_usage.py --dry-run
```

### Ingestion complète directe

```bash
python dremio_to_openmetadata_ingestion.py --mode ingestion
```

### Modes disponibles

- `--mode test` : Test des connexions et affichage des métadonnées
- `--mode dry-run` : Analyse sans modification
- `--mode ingestion` : Ingestion complète

## 📊 Résultat dans OpenMetadata

Après ingestion réussie, vous trouverez dans OpenMetadata :

### Service "Dremio Data Lake Platform"
- Type : CustomDatabase
- Contient tous les schémas correspondants aux sources Dremio

### Schémas créés
- Un schéma par source Dremio (ex: "MinIO", "PostgreSQL")
- Un schéma "VDS_Analytics" pour tous les VDS

### Tables et Vues
- Tables physiques des sources
- Vues SQL pour les VDS avec leur définition SQL

### Pipeline d'ingestion
- Pipeline automatique configuré
- Planification quotidienne par défaut
- Peut être modifié dans OpenMetadata UI

## 🔧 Dépannage

### Erreur de connexion Dremio
```bash
# Vérifier que Dremio est démarré
curl http://localhost:9047/apiv2/info

# Vérifier les identifiants dans .env
```

### Erreur de token OpenMetadata
```bash
# Régénérer un nouveau token dans OpenMetadata UI
# Vérifier que le token n'a pas expiré
```

### Problèmes de dépendances
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --upgrade
```

### Debug détaillé
Modifier le niveau de log dans `config/dremio_ingestion.yaml` :
```yaml
logging:
  level: "DEBUG"
```

## 📝 Logs

Les logs sont sauvegardés dans :
- `dremio_ingestion.log` : Log principal
- `ingestion_metrics.json` : Métriques de performance (si activé)
- `ingestion_progress.json` : Sauvegarde d'état (si activé)

## 🔄 Pipeline automatique

Une fois l'ingestion initiale terminée, OpenMetadata :
1. Crée automatiquement un pipeline d'ingestion
2. Le planifie pour s'exécuter quotidiennement
3. Maintient les métadonnées à jour

Pour modifier la planification :
1. Aller dans OpenMetadata UI
2. Services → Dremio Data Lake Platform → Ingestion
3. Éditer le pipeline

## 📚 Structure du projet

```
ingestion/
├── dremio_to_openmetadata_ingestion.py  # Script principal
├── example_usage.py                     # Exemples d'utilisation
├── requirements.txt                     # Dépendances
├── .env.example                         # Variables d'environnement
├── config/
│   └── dremio_ingestion.yaml           # Configuration principale
└── src/
    ├── client/
    │   ├── dremio_client.py             # Client API Dremio
    │   └── openmetadata_client.py       # Client API OpenMetadata
    └── utils/
        └── config_manager.py            # Gestionnaire configuration
```

## 🤝 Contribution

Pour contribuer au projet :
1. Fork le repository
2. Créer une branche feature
3. Faire vos modifications
4. Tester avec `python example_usage.py --test-connections`
5. Soumettre une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.