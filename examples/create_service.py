"""
Utilitaire : Créer le service Dremio dans OpenMetadata

Ce script crée le service CustomDatabase dans OpenMetadata
avant de lancer la synchronisation.

Usage:
    python examples/create_service.py
"""

import logging
import sys
import os
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_dremio_service(
    openmetadata_url: str,
    jwt_token: str,
    service_name: str
) -> bool:
    """Crée le service Dremio dans OpenMetadata"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    service_definition = {
        "name": service_name,
        "displayName": "Dremio Data Lake Platform",
        "description": "Dremio auto-sync connector with advanced discovery",
        "serviceType": "CustomDatabase",
        "connection": {
            "config": {
                "type": "CustomDatabase",
                "sourcePythonClass": "dremio_connector.core.sync_engine",
                "connectionOptions": {
                    "dremioHost": "localhost",
                    "dremioPort": "9047"
                }
            }
        }
    }
    
    try:
        # Vérifier si le service existe
        logger.info(f"Vérification service {service_name}...")
        response = requests.get(
            f"{openmetadata_url}/v1/services/databaseServices/name/{service_name}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Service {service_name} existe déjà")
            return True
        
        # Créer le service
        logger.info(f"Création service {service_name}...")
        response = requests.post(
            f"{openmetadata_url}/v1/services/databaseServices",
            json=service_definition,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Service {service_name} créé avec succès")
            return True
        else:
            logger.error(f"❌ Échec création service: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False


def main():
    config = {
        "openmetadata_url": "http://localhost:8585/api",
        "jwt_token": "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImdlbmVyaWMtaW5nZXN0aW9uLWJvdCIsInJvbGVzIjpbXSwiZW1haWwiOiJnZW5lcmljLWluZ2VzdGlvbi1ib3RAdGFsZW50eXMuZXUiLCJpc0JvdCI6dHJ1ZSwidG9rZW5UeXBlIjoiQk9UIiwiaWF0IjoxNzU4MTM2NTI4LCJleHAiOm51bGx9.Hy4ed-YPdwKeZ71viL1G2JmQzo-gSdfa7MiKGj8ujgx4znEjuzFqRl15mhqsKjhSjnU-f6v_IV1Qe5kcxxaKScxq3HPPGF6snl2CgZBPXCu9QhSDQBLZO5FIY-vy8h9iLQXOYNoYj79-y7Xqu82O15vLpzHjh4_fOXJ59X0_oiq3NpIrv8eUv93K-nFqDwNPF00SwykEuoRcYNnhWueOy8e_MVkWv66kT74YKqS-iS-c6w18i0YXNnkUwt_RvzMf7-ZI6xuSV7A6xrWdFpC_2rIUJluBR2BWooLwDaA578KkjX8Rqe8VLA2vIBJlKw97Q1JY0a34lRGCiIk2HJBVHQ",
        "service_name": "dremio_service"
    }
    
    print("\n" + "="*80)
    print("🔧 CRÉATION DU SERVICE DREMIO DANS OPENMETADATA")
    print("="*80 + "\n")
    
    success = create_dremio_service(
        openmetadata_url=config["openmetadata_url"],
        jwt_token=config["jwt_token"],
        service_name=config["service_name"]
    )
    
    if success:
        print("\n✅ Service créé ! Vous pouvez maintenant lancer la synchronisation:")
        print("   python examples/full_sync_example.py\n")
        return 0
    else:
        print("\n❌ Échec de la création du service\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
