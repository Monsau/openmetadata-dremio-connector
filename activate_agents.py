#!/usr/bin/env python3
"""
🚀 Script d'activation des agents Dremio dans OpenMetadata
Ce script exécute directement les agents sans passer par l'UI
"""

import sys
import argparse
from datetime import datetime

def run_metadata_agent(mode='incremental', dremio_user='admin', dremio_pass='admin123', om_token=None):
    """Exécute le MetadataAgent pour synchroniser Dremio"""
    print("\n" + "="*70)
    print("🔄 METADATA AGENT - Synchronisation Dremio")
    print("="*70 + "\n")
    
    try:
        from dremio_connector.agents import MetadataAgent
        
        config = {
            'dremio': {
                'url': 'http://host.docker.internal:9047',
                'username': dremio_user,
                'password': dremio_pass
            },
            'openmetadata': {
                'api_url': 'http://openmetadata_server:8585/api',
                'token': om_token or 'eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJlbWFpbCI6ImluZ2VzdGlvbi1ib3RAb3Blbm1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE3Mjg0ODA3MDIsImV4cCI6bnVsbH0.TAq5Qjjb_2FnWTsJ3KqKO_P8rXrGPj3z9TfqMkT6Z3_PbJ4v4W_DaAmN_iCqR-5mB9PYhN_CuYGJy5VLGcq5bg',
                'service_name': 'dremio-with-official-connector'
            },
            'mode': mode  # 'full' ou 'incremental'
        }
        
        print(f"📋 Configuration:")
        print(f"   Dremio URL: {config['dremio']['url']}")
        print(f"   Service: {config['openmetadata']['service_name']}")
        print(f"   Mode: {mode}\n")
        
        print("🚀 Démarrage de l'agent...")
        agent = MetadataAgent(config=config)
        
        # Test connexion
        print("🔌 Test connexion...")
        if agent.test_connection():
            print("✅ Connexion réussie\n")
        else:
            print("⚠️  Connexion OK mais avec avertissements\n")
        
        # Exécution
        print("⚙️  Exécution de la synchronisation...")
        result = agent.run()
        
        print(f"\n✅ TERMINÉ!")
        print(f"   Résultat: {result}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_lineage_agent():
    """Exécute le LineageAgent pour valider le lineage"""
    print("\n" + "="*70)
    print("🔍 LINEAGE AGENT - Validation Lineage")
    print("="*70 + "\n")
    
    try:
        from dremio_connector.agents import LineageAgent
        
        config = {
            'openmetadata': {
                'api_url': 'http://openmetadata_server:8585/api',
                'token': 'eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJlbWFpbCI6ImluZ2VzdGlvbi1ib3RAb3Blbm1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE3Mjg0ODA3MDIsImV4cCI6bnVsbH0.TAq5Qjjb_2FnWTsJ3KqKO_P8rXrGPj3z9TfqMkT6Z3_PbJ4v4W_DaAmN_iCqR-5mB9PYhN_CuYGJy5VLGcq5bg',
                'service_name': 'dremio-with-official-connector'
            },
            'validation_mode': 'strict',
            'report_path': '/tmp/lineage_reports'
        }
        
        print(f"📋 Configuration:")
        print(f"   Service: {config['openmetadata']['service_name']}")
        print(f"   Mode: {config['validation_mode']}\n")
        
        print("🚀 Démarrage de l'agent...")
        agent = LineageAgent(config=config)
        
        # Exécution
        print("⚙️  Exécution de la validation...")
        result = agent.run()
        
        print(f"\n✅ TERMINÉ!")
        print(f"   Résultat: {result}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_profiler_agent(sampling_rate=0.1):
    """Exécute le ProfilerAgent pour analyser la qualité des données"""
    print("\n" + "="*70)
    print("📊 PROFILER AGENT - Analyse Qualité Données")
    print("="*70 + "\n")
    
    try:
        from dremio_connector.agents import ProfilerAgent
        
        config = {
            'dremio': {
                'url': 'http://host.docker.internal:9047',
                'username': 'admin',
                'password': 'Dremio123!'
            },
            'openmetadata': {
                'api_url': 'http://openmetadata_server:8585/api',
                'token': 'eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJlbWFpbCI6ImluZ2VzdGlvbi1ib3RAb3Blbm1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE3Mjg0ODA3MDIsImV4cCI6bnVsbH0.TAq5Qjjb_2FnWTsJ3KqKO_P8rXrGPj3z9TfqMkT6Z3_PbJ4v4W_DaAmN_iCqR-5mB9PYhN_CuYGJy5VLGcq5bg',
                'service_name': 'dremio-with-official-connector'
            },
            'sampling_rate': sampling_rate,
            'profiling_options': {
                'include_nulls': True,
                'include_duplicates': True,
                'include_distributions': True
            }
        }
        
        print(f"📋 Configuration:")
        print(f"   Dremio URL: {config['dremio']['url']}")
        print(f"   Service: {config['openmetadata']['service_name']}")
        print(f"   Sampling: {sampling_rate * 100}%\n")
        
        print("🚀 Démarrage de l'agent...")
        agent = ProfilerAgent(config=config)
        
        # Exécution
        print("⚙️  Exécution du profilage...")
        result = agent.run()
        
        print(f"\n✅ TERMINÉ!")
        print(f"   Résultat: {result}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_dbt_agent(manifest_path):
    """Exécute le DbtAgent pour ingérer les modèles dbt"""
    print("\n" + "="*70)
    print("🔧 DBT AGENT - Ingestion Modèles dbt")
    print("="*70 + "\n")
    
    try:
        from dremio_connector.agents import DbtAgent
        
        config = {
            'manifest_path': manifest_path,
            'openmetadata': {
                'api_url': 'http://openmetadata_server:8585/api',
                'token': 'eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJlbWFpbCI6ImluZ2VzdGlvbi1ib3RAb3Blbm1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJpYXQiOjE3Mjg0ODA3MDIsImV4cCI6bnVsbH0.TAq5Qjjb_2FnWTsJ3KqKO_P8rXrGPj3z9TfqMkT6Z3_PbJ4v4W_DaAmN_iCqR-5mB9PYhN_CuYGJy5VLGcq5bg',
                'service_name': 'dremio-with-official-connector'
            }
        }
        
        print(f"📋 Configuration:")
        print(f"   Manifest: {manifest_path}")
        print(f"   Service: {config['openmetadata']['service_name']}\n")
        
        print("🚀 Démarrage de l'agent...")
        agent = DbtAgent(config=config)
        
        # Exécution
        print("⚙️  Exécution de l'ingestion dbt...")
        result = agent.run()
        
        print(f"\n✅ TERMINÉ!")
        print(f"   Résultat: {result}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Menu principal"""
    parser = argparse.ArgumentParser(
        description='🚀 Activation des agents Dremio dans OpenMetadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Exécuter tous les agents
  python activate_agents.py --all

  # Exécuter seulement MetadataAgent
  python activate_agents.py --metadata

  # Exécuter MetadataAgent en mode full
  python activate_agents.py --metadata --full

  # Exécuter ProfilerAgent avec sampling 20%
  python activate_agents.py --profiler --sampling 0.2

  # Exécuter DbtAgent
  python activate_agents.py --dbt --manifest /path/to/manifest.json
        """
    )
    
    parser.add_argument('--all', action='store_true', 
                       help='Exécuter tous les agents (metadata + lineage + profiler)')
    parser.add_argument('--metadata', action='store_true',
                       help='Exécuter MetadataAgent (sync Dremio)')
    parser.add_argument('--lineage', action='store_true',
                       help='Exécuter LineageAgent (validation)')
    parser.add_argument('--profiler', action='store_true',
                       help='Exécuter ProfilerAgent (qualité)')
    parser.add_argument('--dbt', action='store_true',
                       help='Exécuter DbtAgent (ingestion dbt)')
    
    parser.add_argument('--full', action='store_true',
                       help='Mode full pour MetadataAgent (au lieu de incremental)')
    parser.add_argument('--sampling', type=float, default=0.1,
                       help='Taux de sampling pour ProfilerAgent (0.0-1.0, défaut: 0.1)')
    parser.add_argument('--manifest', type=str,
                       help='Chemin vers manifest.json pour DbtAgent')
    parser.add_argument('--dremio-user', type=str, default='admin',
                       help='Username Dremio (défaut: admin)')
    parser.add_argument('--dremio-pass', type=str, default='admin123',
                       help='Password Dremio (défaut: admin123)')
    parser.add_argument('--om-token', type=str,
                       help='JWT token OpenMetadata (optionnel, sinon utilise token par défaut)')
    
    args = parser.parse_args()
    
    # Si aucun agent spécifié, afficher aide
    if not any([args.all, args.metadata, args.lineage, args.profiler, args.dbt]):
        parser.print_help()
        print("\n" + "="*70)
        print("💡 CONSEIL: Commence par --metadata pour synchroniser Dremio")
        print("="*70)
        sys.exit(0)
    
    print("\n" + "="*70)
    print("🚀 ACTIVATION DES AGENTS DREMIO")
    print("="*70)
    print(f"⏰ Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    total_count = 0
    
    # Exécuter les agents demandés
    if args.all or args.metadata:
        total_count += 1
        mode = 'full' if args.full else 'incremental'
        if run_metadata_agent(mode=mode, dremio_user=args.dremio_user, dremio_pass=args.dremio_pass, om_token=args.om_token):
            success_count += 1
    
    if args.all or args.lineage:
        total_count += 1
        if run_lineage_agent():
            success_count += 1
    
    if args.all or args.profiler:
        total_count += 1
        if run_profiler_agent(sampling_rate=args.sampling):
            success_count += 1
    
    if args.dbt:
        total_count += 1
        if args.manifest:
            if run_dbt_agent(manifest_path=args.manifest):
                success_count += 1
        else:
            print("\n❌ --manifest requis pour DbtAgent")
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    print(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✅ Succès: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 TOUS LES AGENTS ONT ÉTÉ EXÉCUTÉS AVEC SUCCÈS!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_count - success_count} agent(s) en erreur")
        sys.exit(1)

if __name__ == "__main__":
    main()
