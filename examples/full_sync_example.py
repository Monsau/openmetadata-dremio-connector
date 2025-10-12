"""
Exemple: Synchronisation automatique complète Dremio → OpenMetadata

Ce script démontre l'utilisation du moteur de synchronisation avancé
qui découvre automatiquement TOUTES les ressources Dremio et les
synchronise dans OpenMetadata avec métadonnées complètes.

Features:
- Auto-discovery de 100% des ressources Dremio
- Synchronisation idempotente (peut être ré-exécuté sans danger)
- Métadonnées complètes (colonnes, types, descriptions)
- Statistiques détaillées
- Gestion d'erreurs robuste

Usage:
    python examples/full_sync_example.py
"""

import logging
import sys
import os

# Ajouter src au path pour imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from dremio_connector.core.sync_engine import DremioOpenMetadataSync

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """
    Synchronisation complète Dremio → OpenMetadata
    """
    print("\n" + "="*80)
    print("🚀 SYNCHRONISATION AUTOMATIQUE DREMIO → OPENMETADATA")
    print("="*80 + "\n")
    
    # Configuration
    config = {
        "dremio_url": "http://localhost:9047",
        "dremio_user": "admin",
        "dremio_password": "admin123",
        "openmetadata_url": "http://localhost:8585/api",
        "jwt_token": "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ",
        "service_name": "dremio_dbt_service"  # Service existant dans OpenMetadata
    }
    
    print("Configuration:")
    print(f"  • Dremio:        {config['dremio_url']}")
    print(f"  • OpenMetadata:  {config['openmetadata_url']}")
    print(f"  • Service:       {config['service_name']}")
    print(f"  • User:          {config['dremio_user']}")
    print("\n")
    
    # Créer le moteur de synchronisation
    sync = DremioOpenMetadataSync(
        dremio_url=config["dremio_url"],
        dremio_user=config["dremio_user"],
        dremio_password=config["dremio_password"],
        openmetadata_url=config["openmetadata_url"],
        jwt_token=config["jwt_token"],
        service_name=config["service_name"]
    )
    
    # Lancer la synchronisation
    try:
        stats = sync.sync()
        
        print("\n" + "="*80)
        print("✅ SYNCHRONISATION TERMINÉE")
        print("="*80)
        
        if "error" in stats:
            print(f"\n❌ Erreur: {stats['error']}")
            return 1
        
        print(f"""
📊 Résultats:
   • Ressources découvertes:  {stats['resources_discovered']}
   • Databases créées/màj:    {stats['databases_created']}
   • Schemas créés/màj:       {stats['schemas_created']}
   • Tables créées/màj:       {stats['tables_created']}
   • Erreurs:                 {stats['errors']}
   • Durée:                   {stats['duration_seconds']:.2f}s
        """)
        
        print("\n🎉 Vos ressources Dremio sont maintenant disponibles dans OpenMetadata!")
        print(f"   Visitez: http://localhost:8585 → Services → {config['service_name']}\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Synchronisation interrompue par l'utilisateur\n")
        return 130
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}\n")
        logging.exception("Erreur durant la synchronisation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
