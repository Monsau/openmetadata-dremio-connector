# Dremio to OpenMetadata Ingestion - Version Nettoyée

## Description

Système d'ingestion optimisé pour transférer automatiquement les métadonnées Dremio vers OpenMetadata. Cette version nettoyée contient uniquement les fonctionnalités essentielles pour l'ingestion, sans les scripts de debug et utilitaires de développement.

## Architecture

```
dremio_ingestion_clean.py          # Script principal d'ingestion
├── DremioIngestion                # Orchestrateur principal
├── DremioClient                   # Client API Dremio
└── OpenMetadataClient            # Client API OpenMetadata
```

## Fonctionnalités

### ✅ Ingestion des Sources Dremio
- Découverte automatique des sources (PostgreSQL, MinIO, etc.)
- Récupération des schémas et tables
- Création des entités correspondantes dans OpenMetadata

### ✅ Ingestion des VDS (Virtual Data Sets)
- Découverte des VDS dans tous les espaces Dremio
- Support des espaces multiples (Analytics, DataLake, CustomDB_Analytics)
- Création des vues dans OpenMetadata avec métadonnées complètes

### ✅ Gestion des Métadonnées
- Mapping automatique des types de données Dremio → OpenMetadata
- Préservation des descriptions et noms d'affichage
- Organisation logique par schémas selon l'origine

## Installation

### 1. Prérequis
- Python 3.8+
- Accès à une instance Dremio
- Accès à une instance OpenMetadata
- Token JWT OpenMetadata valide

### 2. Installation des dépendances
```bash
cd ingestion/
pip install -r requirements.txt
```

### 3. Configuration
Copiez le fichier template et configurez vos paramètres :

```bash
cp .env.template .env
# Éditez le fichier .env avec vos paramètres
```

Configuration requise dans `.env` :
```bash
# Dremio
DREMIO_HOST=localhost
DREMIO_PORT=9047
DREMIO_USERNAME=admin
DREMIO_PASSWORD=admin123

# OpenMetadata  
OPENMETADATA_HOST=localhost
OPENMETADATA_PORT=8585
OPENMETADATA_JWT_TOKEN=your_jwt_token_here
```

## Utilisation

### Mode Test (Recommandé en premier)
Teste les connexions et affiche un aperçu des métadonnées :
```bash
python dremio_ingestion_clean.py --mode test
```

### Mode Ingestion Complète
Lance l'ingestion de toutes les métadonnées :
```bash
python dremio_ingestion_clean.py --mode ingestion
```

### Mode Dry-Run
Teste uniquement les connexions :
```bash
python dremio_ingestion_clean.py --mode dry-run
```

## Processus d'Ingestion

L'ingestion suit ces étapes séquentielles :

1. **Validation des Connexions**
   - Test de connexion Dremio
   - Test de connexion OpenMetadata

2. **Création du Service**
   - Service CustomDatabase `dremio-custom-service`
   - Base de données `dremio-custom-service_database`

3. **Ingestion des Sources**
   - Pour chaque source Dremio (PostgreSQL_Business, minio-storage, etc.)
   - Création du schéma correspondant
   - Ingestion des tables avec colonnes et métadonnées

4. **Ingestion des VDS**
   - Découverte des VDS dans tous les espaces
   - Création des schémas par espace (Analytics, DataLake, CustomDB_Analytics)
   - Création des vues avec définitions complètes

5. **Pipeline de Métadonnées**
   - Création du pipeline d'ingestion automatique
   - Configuration pour refresh quotidien

## Structure des Données dans OpenMetadata

### Service et Base de Données
```
Service: dremio-custom-service (CustomDatabase)
└── Database: dremio-custom-service_database
```

### Schémas par Type de Source
```
├── PostgreSQL_Business/          # Source PostgreSQL
│   ├── campagnes_marketing
│   ├── clients
│   ├── commandes
│   └── ...
├── minio-storage/               # Source MinIO
├── CustomDB_Analytics/          # VDS Espace CustomDB_Analytics
│   ├── vue_clients_count
│   ├── vue_commandes_simple
│   └── ...
├── Analytics/                   # VDS Espace Analytics
│   └── Vue_Clients_Complets
└── DataLake/                    # VDS Espace DataLake
    └── Dashboard_Geographique
```

## Mapping des Types de Données

| Type Dremio | Type OpenMetadata |
|-------------|-------------------|
| VARCHAR     | VARCHAR          |
| INTEGER     | INT              |
| BIGINT      | BIGINT           |
| DOUBLE      | DOUBLE           |
| BOOLEAN     | BOOLEAN          |
| DATE        | DATE             |
| TIMESTAMP   | TIMESTAMP        |
| DECIMAL     | DECIMAL          |
| FLOAT       | FLOAT            |
| TEXT        | TEXT             |

## Logs et Monitoring

Les logs sont écrits dans :
- Console (stdout)
- Fichier `dremio_ingestion.log`

Format des logs :
```
2024-10-04 10:30:15 - DremioIngestion - INFO - [OK] Service CustomDB créé avec succès
```

## Résolution des Problèmes Courants

### Erreur de Connexion Dremio
- Vérifiez DREMIO_HOST, DREMIO_PORT
- Validez les credentials DREMIO_USERNAME/PASSWORD
- Assurez-vous que Dremio est accessible

### Erreur de Connexion OpenMetadata  
- Vérifiez OPENMETADATA_HOST, OPENMETADATA_PORT
- Validez le token OPENMETADATA_JWT_TOKEN
- Vérifiez que OpenMetadata est démarré

### Erreur "Service existe déjà" (409)
- Normal lors des exécutions répétées
- Le système met à jour les ressources existantes

### VDS non trouvés
- Vérifiez que les VDS sont publiés dans Dremio
- Assurez-vous d'avoir les permissions sur les espaces

## Maintenance

### Fichiers Générés
- `dremio_ingestion.log` : Logs d'exécution
- `__pycache__/` : Cache Python (peut être supprimé)

### Nettoyage
```bash
# Suppression des logs
rm dremio_ingestion.log

# Suppression du cache Python
rm -rf __pycache__ src/__pycache__ src/client/__pycache__
```

## Développement

### Structure du Code
```
src/
├── client/
│   ├── dremio_client.py          # Client API Dremio
│   └── openmetadata_client.py    # Client API OpenMetadata
└── utils/                        # (Non utilisé dans la version clean)
```

### Ajout de Fonctionnalités
1. Modifiez `dremio_ingestion_clean.py`
2. Testez avec `--mode test`
3. Validez avec `--mode ingestion`

## Historique des Versions

- **v2.0-clean** : Version nettoyée avec fonctionnalités essentielles uniquement
- **v1.x** : Version de développement avec scripts de debug

## Support

En cas de problème :
1. Exécutez d'abord `--mode test` pour diagnostiquer
2. Vérifiez les logs dans `dremio_ingestion.log`  
3. Validez la configuration dans `.env`
4. Vérifiez la connectivité réseau vers Dremio et OpenMetadata

## Exemple de Session Complète

```bash
# 1. Configuration
cp .env.template .env
# Éditer .env avec vos paramètres

# 2. Test initial
python dremio_ingestion_clean.py --mode test

# 3. Ingestion complète  
python dremio_ingestion_clean.py --mode ingestion

# 4. Vérification dans OpenMetadata UI
# Naviguer vers http://localhost:8585
# Aller dans Databases > dremio-custom-service
```

## Résultat Attendu

Après une ingestion réussie, vous devriez voir dans OpenMetadata :
- ✅ Service `dremio-custom-service` 
- ✅ Schémas correspondant aux sources Dremio
- ✅ Tables avec colonnes et métadonnées
- ✅ VDS organisés par espaces
- ✅ Pipeline de métadonnées configuré