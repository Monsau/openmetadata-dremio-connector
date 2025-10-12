#!/usr/bin/env python3
"""
Exemple pratique : Intégration complète Dremio + dbt avec OpenMetadata

Ce script démontre l'utilisation coordonnée des agents avec le projet dremiodbt.
"""

import sys
import json
import time
from pathlib import Path

# Ajout du chemin src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dremio_connector.agents.agent_manager import agent_executor
from dremio_connector.agents import DbtAgent, MetadataAgent


def workflow_complete_sync():
    """
    Workflow de synchronisation complète : Dremio → dbt → OpenMetadata
    """
    print("🔄 Workflow Synchronisation Complète")
    print("=" * 50)
    
    # Configuration de base OpenMetadata
    om_config = {
        'api_url': 'http://localhost:8585/api',
        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImFkbWluIiwiZW1haWwiOiJhZG1pbkBvcGVubWV0YWRhdGEub3JnIiwiaXNCb3QiOmZhbHNlLCJ0b2tlblR5cGUiOiJKV1QiLCJpYXQiOjE3Mjg4MzI2NjEsImV4cCI6MTc2MDM2ODY2MX0.example', # À remplacer par vrai token
        'service_name': 'dremio_service'
    }
    
    # Étape 1: Sync métadonnées Dremio
    print("\n📊 Étape 1: Synchronisation Métadonnées Dremio")
    print("-" * 40)
    
    metadata_config = {
        'dremio': {
            'url': 'http://localhost:9047',
            'username': 'admin', 
            'password': 'admin123'
        },
        'openmetadata': om_config,
        'sync_mode': 'full'
    }
    
    print("🚀 Exécution MetadataAgent...")
    metadata_result = agent_executor.execute_agent('metadata', metadata_config, 'metadata_sync_001')
    print(f"✅ Résultat: {metadata_result['status']}")
    
    if metadata_result['status'] == 'success':
        stats = metadata_result.get('sync_statistics', {})
        print(f"  📈 Databases: {stats.get('databases', 0)}")
        print(f"  📈 Schemas: {stats.get('schemas', 0)}")  
        print(f"  📈 Tables: {stats.get('tables', 0)}")
        print(f"  ⚠️ Erreurs: {len(stats.get('errors', []))}")
    
    # Étape 2: Ingestion dbt (utilise projet dremiodbt)
    print("\n🔧 Étape 2: Ingestion Modèles dbt")
    print("-" * 40)
    
    # Chemin vers le manifest.json du projet dremiodbt  
    manifest_path = str(Path(__file__).parent.parent.parent / 'dremiodbt' / 'dbt' / 'target' / 'manifest.json')
    
    dbt_config = {
        'manifest_path': manifest_path,
        'openmetadata': {
            **om_config,
            'service_name': 'dremio_dbt_service'  # Service séparé pour dbt
        }
    }
    
    # Vérifier si le manifest existe
    if Path(manifest_path).exists():
        print(f"📋 Manifest trouvé: {manifest_path}")
        print("🚀 Exécution DbtAgent...")
        
        dbt_result = agent_executor.execute_agent('dbt', dbt_config, 'dbt_ingestion_001')
        print(f"✅ Résultat: {dbt_result['status']}")
        
        if dbt_result['status'] == 'success':
            stats = dbt_result.get('statistics', {})
            print(f"  📈 Modèles traités: {stats.get('models_processed', 0)}")
            print(f"  📈 Tables créées: {stats.get('tables_created', 0)}")
            print(f"  📈 Lineage créé: {stats.get('lineage_created', 0)}")
            print(f"  ⚠️ Erreurs: {len(stats.get('errors', []))}")
    else:
        print(f"⚠️ Manifest non trouvé: {manifest_path}")
        print("💡 Exécuter d'abord: cd ../dremiodbt/dbt && dbt compile")
        
        # Simulation pour démo
        print("🎭 Simulation ingestion dbt...")
        dbt_result = {'status': 'simulated', 'message': 'Manifest non disponible'}
    
    # Étape 3: Résumé et recommandations
    print("\n📋 Étape 3: Résumé et Prochaines Étapes")
    print("-" * 40)
    
    total_success = sum(1 for result in [metadata_result, dbt_result] if result.get('status') == 'success')
    
    print(f"🎯 Score workflow: {total_success}/2 étapes réussies")
    
    if total_success == 2:
        print("\n🎉 Workflow complet réussi !")
        print("\n🔄 Prochaines étapes recommandées:")
        print("  1. LineageAgent → Vérification cohérence lineage")
        print("  2. ProfilerAgent → Analyse qualité données")  
        print("  3. Planification agents en mode automatique")
        print("  4. Configuration alertes sur anomalies")
    else:
        print("\n⚠️ Workflow partiellement réussi")
        print("\n🔧 Actions correctives:")
        if metadata_result['status'] != 'success':
            print("  - Vérifier connexion Dremio (http://localhost:9047)")
            print("  - Contrôler credentials admin/admin123") 
        if dbt_result.get('status') != 'success':
            print("  - Compiler dbt project: cd ../dremiodbt/dbt && dbt compile")
            print("  - Vérifier chemin manifest.json")
        print("  - Valider JWT token OpenMetadata")
    
    return {
        'metadata_result': metadata_result,
        'dbt_result': dbt_result,
        'success_rate': total_success / 2
    }


def demo_agent_configurations():
    """
    Démo des configurations possibles pour chaque agent.
    """
    print("\n📝 Configurations Agents - Exemples Pratiques")
    print("=" * 50)
    
    configs = {
        'production': {
            'description': 'Configuration Production',
            'dbt_schedule': '0 2 * * *',  # 2h du matin quotidien
            'metadata_schedule': '0 1 * * *',  # 1h du matin quotidien  
            'lineage_schedule': '0 4 * * 1',  # 4h lundi (hebdo)
            'profiler_schedule': '0 3 * * 0',  # 3h dimanche (hebdo)
        },
        
        'development': {
            'description': 'Configuration Développement', 
            'dbt_schedule': '*/30 * * * *',  # Toutes les 30min
            'metadata_schedule': '0 */2 * * *',  # Toutes les 2h
            'lineage_schedule': '0 9 * * *',  # 9h quotidien
            'profiler_schedule': '0 18 * * *',  # 18h quotidien
        },
        
        'minimal': {
            'description': 'Configuration Minimale',
            'dbt_schedule': 'manual',  # Manuel seulement
            'metadata_schedule': '0 6 * * *',  # 6h quotidien
            'lineage_schedule': 'manual',  # Manuel
            'profiler_schedule': '0 2 * * 0',  # 2h dimanche
        }
    }
    
    for env_name, config in configs.items():
        print(f"\n🏷️ **{env_name.upper()}** - {config['description']}")
        print(f"  🔧 dbt Agent: {config['dbt_schedule']}")
        print(f"  📊 Metadata Agent: {config['metadata_schedule']}")
        print(f"  🔍 Lineage Agent: {config['lineage_schedule']}")
        print(f"  📈 Profiler Agent: {config['profiler_schedule']}")
    
    print("\n💡 **Cron Expressions Utiles**:")
    print("  - '0 2 * * *'     → Quotidien 2h")
    print("  - '0 */6 * * *'   → Toutes les 6h")
    print("  - '0 9-17 * * 1-5' → Heures ouvrables (9h-17h, lun-ven)")
    print("  - '0 3 * * 0'     → Hebdo dimanche 3h")
    print("  - 'manual'        → Exécution manuelle uniquement")


def check_dremiodbt_integration():
    """
    Vérifie l'intégration avec le projet dremiodbt.
    """
    print("\n🔗 Vérification Intégration dremiodbt")
    print("=" * 40)
    
    dremiodbt_path = Path(__file__).parent.parent.parent / 'dremiodbt'
    
    # Vérifications
    checks = [
        ('Projet dremiodbt', dremiodbt_path.exists()),
        ('dbt_project.yml', (dremiodbt_path / 'dbt' / 'dbt_project.yml').exists()),
        ('profiles.yml', (dremiodbt_path / 'dbt' / 'profiles.yml').exists()),
        ('Modèles staging', (dremiodbt_path / 'dbt' / 'models' / 'staging').exists()),
        ('Modèles marts', (dremiodbt_path / 'dbt' / 'models' / 'marts').exists()),
        ('target/manifest.json', (dremiodbt_path / 'dbt' / 'target' / 'manifest.json').exists())
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    success_rate = sum(1 for _, result in checks if result) / len(checks)
    
    if success_rate == 1.0:
        print("\n🎉 Intégration dremiodbt complète !")
    elif success_rate >= 0.8:
        print(f"\n✅ Intégration dremiodbt OK ({success_rate*100:.0f}%)")
        print("💡 Manque seulement manifest.json → exécuter: dbt compile")
    else:
        print(f"\n⚠️ Intégration partielle ({success_rate*100:.0f}%)")
        print("🔧 Vérifier projet dremiodbt disponible")
    
    return success_rate


def main():
    """
    Script principal de démonstration.
    """
    print("🌟 Démonstration Agents Dremio + OpenMetadata")
    print("Intégration avec projet dremiodbt")
    print("=" * 60)
    
    # 1. Vérification environnement
    integration_score = check_dremiodbt_integration()
    
    # 2. Démonstration configurations  
    demo_agent_configurations()
    
    # 3. Workflow complet (si environnement OK)
    if integration_score >= 0.8:
        print("\n" + "=" * 60)
        workflow_result = workflow_complete_sync()
        
        # Résumé final
        print("\n" + "=" * 60)
        print("🏁 RÉSUMÉ DÉMONSTRATION")
        print(f"  📊 Intégration dremiodbt: {integration_score*100:.0f}%")
        print(f"  🚀 Workflow réussi: {workflow_result['success_rate']*100:.0f}%")
        
        if workflow_result['success_rate'] == 1.0:
            print("\n🎉 **SUCCÈS COMPLET** - Système prêt pour production !")
        else:
            print(f"\n⚠️ **SUCCÈS PARTIEL** - Voir instructions ci-dessus")
            
    else:
        print("\n⚠️ Environnement incomplet - Workflow démo sauté")
        print("🔧 Compléter setup dremiodbt pour workflow complet")
    
    print("\n📚 Documentation:")
    print("  - AGENTS_ARCHITECTURE.md → Architecture détaillée")
    print("  - INSTALLATION_OPENMETADATA.md → Guide installation")
    print("  - examples/configs/ → Configurations d'exemple")


if __name__ == "__main__":
    main()