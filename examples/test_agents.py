#!/usr/bin/env python3
"""
Exemple d'utilisation des agents Dremio pour OpenMetadata.

Ce script démontre comment utiliser les différents agents du connecteur.
"""

import sys
import json
from pathlib import Path

# Ajout du chemin src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dremio_connector.agents.agent_manager import agent_registry, agent_executor
from dremio_connector.agents import DbtAgent, MetadataAgent, LineageAgent, ProfilerAgent


def example_dbt_agent():
    """
    Exemple d'utilisation du DbtAgent.
    """
    print("🔧 Test DbtAgent")
    print("-" * 30)
    
    # Configuration exemple
    config = {
        'manifest_path': 'c:/projets/dremiodbt/dbt/target/manifest.json',
        'openmetadata': {
            'api_url': 'http://localhost:8585/api',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',  # Token exemple
            'service_name': 'dremio_dbt_service'
        },
        'schedule': '0 2 * * *'
    }
    
    try:
        # Test de création agent
        agent = DbtAgent(config)
        print(f"✓ Agent créé: {agent.agent_type}")
        
        # Test validation config
        validation = agent.validate_config()
        print(f"✓ Validation: {validation['valid']}")
        if not validation['valid']:
            print(f"  Erreurs: {validation['errors']}")
        
        # Test schéma
        schema = agent.get_schema()
        print(f"✓ Schéma récupéré: {len(schema.get('properties', {}))} propriétés")
        
        # Test statut
        status = agent.get_status()
        print(f"✓ Statut: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur DbtAgent: {str(e)}")
        return False


def example_metadata_agent():
    """
    Exemple d'utilisation du MetadataAgent.
    """
    print("\n🔧 Test MetadataAgent")
    print("-" * 30)
    
    # Configuration exemple  
    config = {
        'dremio': {
            'url': 'http://localhost:9047',
            'username': 'admin',
            'password': 'admin123'
        },
        'openmetadata': {
            'api_url': 'http://localhost:8585/api',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
            'service_name': 'dremio_service'
        },
        'sync_mode': 'incremental',
        'schedule': '0 1 * * *'
    }
    
    try:
        # Test de création agent
        agent = MetadataAgent(config)
        print(f"✓ Agent créé: {agent.agent_type}")
        
        # Test schéma
        schema = agent.get_schema()
        print(f"✓ Schéma récupéré: {len(schema.get('properties', {}))} propriétés")
        
        # Test statut
        status = agent.get_status()
        print(f"✓ Statut: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur MetadataAgent: {str(e)}")
        return False


def example_agent_registry():
    """
    Exemple d'utilisation du registre d'agents.
    """
    print("\n🔧 Test AgentRegistry")
    print("-" * 30)
    
    try:
        # Agents disponibles
        available = agent_registry.get_available_agents()
        print(f"✓ {len(available)} agents disponibles:")
        
        for agent_info in available:
            print(f"  - {agent_info['type']}: {agent_info['name']}")
        
        # Test création agent via registre
        config = {
            'openmetadata': {
                'api_url': 'http://localhost:8585/api',
                'token': 'test_token',
                'service_name': 'test_service'
            },
            'service_name': 'test_service'  # Pour LineageAgent
        }
        
        lineage_agent = agent_registry.create_agent('lineage', config)
        print(f"✓ Agent créé via registre: {lineage_agent.agent_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur AgentRegistry: {str(e)}")
        return False


def example_agent_executor():
    """
    Exemple d'utilisation de l'exécuteur d'agents.
    """
    print("\n🔧 Test AgentExecutor") 
    print("-" * 30)
    
    try:
        # Configuration exemple (simulation)
        config = {
            'openmetadata': {
                'api_url': 'http://localhost:8585/api',
                'token': 'test_token',
                'service_name': 'test_service'
            },
            'service_name': 'test_service',
            'output_dir': 'reports'
        }
        
        # Test exécution agent (simulation)
        print("⚡ Simulation exécution LineageAgent...")
        
        # Créer agent pour test
        agent = agent_registry.create_agent('lineage', config)
        
        # Test validation seulement (pas d'exécution complète)
        validation = agent.validate_config()
        print(f"✓ Validation agent: {validation['valid']}")
        
        # Statut exécuteur
        running = agent_executor.get_running_agents()
        history = agent_executor.get_execution_history(5)
        
        print(f"✓ Agents en cours: {len(running)}")
        print(f"✓ Historique: {len(history)} exécutions")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur AgentExecutor: {str(e)}")
        return False


def generate_test_configs():
    """
    Génère des configurations de test pour chaque agent.
    """
    print("\n📝 Génération configurations de test")
    print("-" * 40)
    
    # Configurations de test
    test_configs = {
        'dbt_agent_config.json': {
            'agent_type': 'dbt',
            'manifest_path': 'c:/projets/dremiodbt/dbt/target/manifest.json',
            'openmetadata': {
                'api_url': 'http://localhost:8585/api',
                'token': 'YOUR_JWT_TOKEN_HERE',
                'service_name': 'dremio_dbt_service'
            },
            'schedule': '0 2 * * *'
        },
        
        'metadata_agent_config.json': {
            'agent_type': 'metadata',
            'dremio': {
                'url': 'http://localhost:9047',
                'username': 'admin',
                'password': 'admin123'
            },
            'openmetadata': {
                'api_url': 'http://localhost:8585/api',
                'token': 'YOUR_JWT_TOKEN_HERE',
                'service_name': 'dremio_service'
            },
            'sync_mode': 'incremental',
            'schedule': '0 1 * * *'
        },
        
        'lineage_agent_config.json': {
            'agent_type': 'lineage',
            'service_name': 'dremio_service',
            'output_dir': 'reports',
            'openmetadata': {
                'api_url': 'http://localhost:8585/api',
                'token': 'YOUR_JWT_TOKEN_HERE'
            },
            'schedule': '0 4 * * *'
        },
        
        'profiler_agent_config.json': {
            'agent_type': 'profiler',
            'dremio': {
                'url': 'http://localhost:9047',
                'username': 'admin',
                'password': 'admin123'
            },
            'tables': [],  # Vide = toutes les tables
            'sample_size': 10000,
            'openmetadata': {
                'api_url': 'http://localhost:8585/api',
                'token': 'YOUR_JWT_TOKEN_HERE',
                'service_name': 'dremio_service'
            },
            'schedule': '0 3 * * 0'
        }
    }
    
    # Créer dossier examples/configs
    config_dir = Path(__file__).parent.parent / 'examples' / 'configs'
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder chaque configuration
    for filename, config in test_configs.items():
        config_file = config_dir / filename
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ {filename}")
    
    print(f"\n📁 Configurations sauvegardées dans: {config_dir}")


def main():
    """
    Script principal de test des agents.
    """
    print("🧪 Test des agents Dremio pour OpenMetadata")
    print("=" * 50)
    
    results = []
    
    # Tests individuels
    results.append(("DbtAgent", example_dbt_agent()))
    results.append(("MetadataAgent", example_metadata_agent()))
    results.append(("AgentRegistry", example_agent_registry()))
    results.append(("AgentExecutor", example_agent_executor()))
    
    # Génération configs
    generate_test_configs()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 Résumé des tests:")
    
    for test_name, success in results:
        status = "✅ OK" if success else "❌ ERREUR"
        print(f"  {status} {test_name}")
    
    total_success = sum(1 for _, success in results if success)
    print(f"\n🎯 Score: {total_success}/{len(results)} tests réussis")
    
    if total_success == len(results):
        print("\n🎉 Tous les tests sont passés ! Système opérationnel.")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifier les configurations.")
    
    print("\n🔄 Prochaines étapes:")
    print("  1. Configurer OpenMetadata (JWT token, services)")
    print("  2. Adapter les configs dans examples/configs/")
    print("  3. Tester avec de vraies données")
    print("  4. Déployer dans OpenMetadata UI")


if __name__ == "__main__":
    main()