"""
Ce script utilise l'API OpenMetadata pour enregistrer les agents.
"""
from metadata.generated.schema.entity.services.ingestionPipelines.ingestionPipeline import IngestionPipeline
from metadata.generated.schema.entity.services.databaseService import DatabaseService
from metadata.generated.schema.entity.services.serviceType import ServiceType
from metadata.generated.schema.api.services.ingestionPipelines.createIngestionPipeline import CreateIngestionPipelineRequest
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import OpenMetadataJWTClientConfig

# Configuration de connexion à OpenMetadata
server_config = OpenMetadataJWTClientConfig(
    hostPort="http://localhost:8585/api",
    jwtToken="${OPENMETADATA_JWT_TOKEN}"  # À remplacer
)

metadata = OpenMetadata(server_config)

def create_pipeline(name, display_name, service_type, pipeline_type):
    """Crée un pipeline d'ingestion"""
    try:
        # Trouver le service Dremio
        dremio_service = metadata.get_by_name(
            entity=DatabaseService,
            fqn="dremio-prod",
            fields=["id", "name"]
        )
        
        if not dremio_service:
            print(f"❌ Service Dremio non trouvé")
            return None
            
        pipeline = CreateIngestionPipelineRequest(
            name=name,
            displayName=display_name,
            pipelineType=pipeline_type,
            service=dremio_service.fullyQualifiedName,
            sourceConfig={
                "config": {
                    "type": service_type,
                }
            }
        )
        
        res = metadata.create_ingestion_pipeline(pipeline)
        print(f"✅ Pipeline {name} créé avec succès")
        return res
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du pipeline {name}: {e}")
        return None

def register_agents():
    """Enregistre tous les agents dans OpenMetadata"""
    # Agent Metadata
    create_pipeline(
        name="dremio-metadata-pipeline",
        display_name="Dremio Metadata Ingestion",
        service_type="DatabaseMetadata",
        pipeline_type="metadata"
    )
    
    # Agent Profiler
    create_pipeline(
        name="dremio-profiler-pipeline",
        display_name="Dremio Data Profiler",
        service_type="Profiler",
        pipeline_type="profiler"
    )
    
    # Agent Lineage
    create_pipeline(
        name="dremio-lineage-pipeline", 
        display_name="Dremio Data Lineage",
        service_type="DatabaseLineage",
        pipeline_type="lineage"
    )
    
    # Agent DBT 
    create_pipeline(
        name="dremio-dbt-pipeline",
        display_name="Dremio DBT Integration",
        service_type="Dbt",
        pipeline_type="dbt"
    )

if __name__ == "__main__":
    print("\n🚀 Démarrage de l'enregistrement des agents OpenMetadata...")
    register_agents()
    print("\n✅ Enregistrement terminé")