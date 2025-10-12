# Installation Dremio Connector dans OpenMetadata

## Vue d'ensemble

Le connecteur Dremio fournit 4 agents spécialisés :

- **dbt Agent** : Ingestion modèles dbt avec lineage automatique
- **Metadata Agent** : Synchronisation métadonnées Dremio 
- **Lineage Agent** : Vérification et visualisation lineage
- **Profiler Agent** : Profilage et qualité des données

## Installation

### 1. Installation du package

```bash
# Cloner le repository
git clone https://github.com/Monsau/dremio_connector.git
cd dremio_connector

# Installer les dépendances
pip install -r requirements.txt

# Installer le connecteur
pip install -e .
```

### 2. Configuration dans OpenMetadata

1. Aller dans **Settings > Agents**
2. Cliquer **Add Custom Connector**
3. Uploader le fichier `config/openmetadata_manifest.json`
4. Configurer les credentials

### 3. Création des agents

#### dbt Agent
- **Manifest Path** : `path/to/dbt/target/manifest.json`
- **Service Name** : Nom du service Dremio dans OpenMetadata
- **Schedule** : `0 2 * * *` (tous les jours à 2h)

#### Metadata Agent  
- **Dremio URL** : `http://localhost:9047`
- **Username/Password** : Credentials Dremio
- **Sync Mode** : `incremental` ou `full`

#### Lineage Agent
- **Service Name** : Service à analyser
- **Output Directory** : Dossier pour les rapports

#### Profiler Agent
- **Tables** : Liste FQN ou vide pour toutes
- **Sample Size** : Taille échantillon (10000)

## Utilisation

### Depuis l'UI OpenMetadata
1. Aller dans **Agents**
2. Sélectionner l'agent désiré  
3. Configurer et planifier
4. Surveiller l'exécution

### Depuis Python
```python
from dremio_connector.agents import DbtAgent

config = {
    'manifest_path': 'dbt/target/manifest.json',
    'openmetadata': {
        'api_url': 'http://localhost:8585/api',
        'token': 'YOUR_JWT_TOKEN',
        'service_name': 'dremio_service'
    }
}

agent = DbtAgent(config)
result = agent.run()
```

## Workflows recommandés

### Synchronisation complète
1. **Metadata Agent** (sync métadonnées Dremio)
2. **dbt Agent** (ingestion modèles dbt)  
3. **Lineage Agent** (vérification lineage)
4. **Profiler Agent** (qualité données)

### Synchronisation incrémentale
- **Metadata Agent** quotidien (mode incremental)
- **dbt Agent** après chaque run dbt
- **Lineage Agent** hebdomadaire
- **Profiler Agent** hebdomadaire

## Troubleshooting

### Erreurs communes

**JWT Token expiré**
- Régénérer le token dans OpenMetadata
- Mettre à jour la configuration

**Dremio inaccessible**
- Vérifier URL et credentials
- Contrôler connectivité réseau

**Manifest dbt non trouvé**
- Vérifier chemin manifest.json
- S'assurer que `dbt compile` a été exécuté

**Permissions insuffisantes**
- Vérifier droits utilisateur Dremio
- Contrôler permissions OpenMetadata

## Support

- **Documentation** : README.md du projet
- **Issues** : GitHub Issues
- **Logs** : Vérifier logs agents dans OpenMetadata
