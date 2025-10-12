#!/usr/bin/env python3
"""
Script de configuration des agents Dremio dans OpenMetadata.

Ce script enregistre automatiquement tous les agents du connecteur
dans OpenMetadata pour qu'ils soient disponibles dans l'UI.
"""

import json
import sys
from pathlib import Path

# Ajout du chemin src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dremio_connector.agents.agent_manager import get_openmetadata_agents, agent_registry


def generate_agent_configs():
    """
    Génère les fichiers de configuration pour chaque agent.
    """
    print("🔧 Génération configurations agents OpenMetadata...")
    
    # Créer dossier config s'il n'existe pas
    config_dir = Path(__file__).parent.parent / 'config' / 'agents'
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuration générale
    general_config = get_openmetadata_agents()
    
    with open(config_dir / 'agents_config.json', 'w', encoding='utf-8') as f:
        json.dump(general_config, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Configuration générale: {config_dir / 'agents_config.json'}")
    
    # Configurations individuelles par agent
    for agent_info in general_config['agents']:
        agent_type = agent_info['type']
        
        # Configuration spécifique agent
        agent_config = {
            'agent_type': agent_type,
            'name': agent_info['name'],
            'description': agent_info['description'],
            'schema': agent_info['schema'],
            'example_config': _generate_example_config(agent_type, agent_info['schema'])
        }
        
        # Sauvegarder
        config_file = config_dir / f'{agent_type}_agent.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(agent_config, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ {agent_type.capitalize()} Agent: {config_file}")


def _generate_example_config(agent_type: str, schema: dict) -> dict:
    """
    Génère une configuration d'exemple basée sur le schéma.
    """
    config = {}
    
    properties = schema.get('properties', {})
    
    for prop_name, prop_info in properties.items():
        if 'default' in prop_info:
            config[prop_name] = prop_info['default']
        elif prop_info.get('type') == 'string':
            config[prop_name] = f"example_{prop_name}"
        elif prop_info.get('type') == 'object':
            # Récursion pour objets imbriqués
            nested = {}
            for nested_prop, nested_info in prop_info.get('properties', {}).items():
                if 'default' in nested_info:
                    nested[nested_prop] = nested_info['default']
                elif nested_info.get('type') == 'string':
                    if nested_info.get('format') == 'password':
                        nested[nested_prop] = "your_password_here"
                    else:
                        nested[nested_prop] = f"example_{nested_prop}"
                elif nested_info.get('type') == 'integer':
                    nested[nested_prop] = 1000
            config[prop_name] = nested
        elif prop_info.get('type') == 'array':
            config[prop_name] = []
        elif prop_info.get('type') == 'integer':
            config[prop_name] = 1000
    
    return config


def generate_openmetadata_manifest():
    """
    Génère le manifest pour OpenMetadata décrivant le connecteur.
    """
    print("\n📋 Génération manifest OpenMetadata...")
    
    config_dir = Path(__file__).parent.parent / 'config'
    
    # Récupérer info agents
    agents_info = get_openmetadata_agents()
    
    # Manifest OpenMetadata
    manifest = {
        "name": "dremio_connector",
        "displayName": "Dremio Connector",
        "description": "Connecteur OpenMetadata pour Dremio avec support dbt intégré",
        "version": "1.0.0",
        "author": "Talentyus EU",
        "license": "MIT",
        "homepage": "https://github.com/Monsau/dremio_connector",
        "repository": "https://github.com/Monsau/dremio_connector",
        "keywords": ["dremio", "openmetadata", "dbt", "lineage", "metadata"],
        "category": "connector",
        "type": "custom",
        "agents": [
            {
                "type": agent['type'],
                "name": agent['name'],
                "description": agent['description'],
                "configSchema": agent['schema']
            }
            for agent in agents_info['agents']
        ],
        "capabilities": agents_info['capabilities'],
        "supportedServices": agents_info['supported_services'],
        "installation": {
            "type": "python",
            "requirements": "requirements.txt",
            "entry_point": "dremio_connector.agents"
        },
        "configuration": {
            "global_config_schema": {
                "type": "object",
                "properties": {
                    "openmetadata": {
                        "type": "object",
                        "properties": {
                            "api_url": {"type": "string"},
                            "token": {"type": "string", "format": "password"},
                            "service_name": {"type": "string"}
                        },
                        "required": ["api_url", "token", "service_name"]
                    }
                },
                "required": ["openmetadata"]
            }
        }
    }
    
    # Sauvegarder
    manifest_file = config_dir / 'openmetadata_manifest.json'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Manifest OpenMetadata: {manifest_file}")


def generate_installation_guide():
    """
    Génère un guide d'installation pour OpenMetadata.
    """
    print("\n📖 Génération guide installation...")
    
    guide = """# Installation Dremio Connector dans OpenMetadata

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
"""

    guide_file = Path(__file__).parent.parent / 'INSTALLATION_OPENMETADATA.md'
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"  ✓ Guide installation: {guide_file}")


def main():
    """
    Script principal de configuration.
    """
    print("🚀 Configuration agents Dremio pour OpenMetadata")
    print("=" * 50)
    
    try:
        # Générer configurations agents
        generate_agent_configs()
        
        # Générer manifest OpenMetadata
        generate_openmetadata_manifest()
        
        # Générer guide installation
        generate_installation_guide()
        
        print("\n✅ Configuration terminée avec succès!")
        print("\n📋 Fichiers générés:")
        print("  - config/agents/agents_config.json")
        print("  - config/agents/*_agent.json") 
        print("  - config/openmetadata_manifest.json")
        print("  - INSTALLATION_OPENMETADATA.md")
        
        print("\n🔄 Prochaines étapes:")
        print("  1. Uploader openmetadata_manifest.json dans OpenMetadata")
        print("  2. Configurer les agents selon vos besoins")
        print("  3. Planifier l'exécution des agents")
        
    except Exception as e:
        print(f"\n❌ Erreur configuration: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()