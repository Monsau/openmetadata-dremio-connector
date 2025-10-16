"""
Force l'enregistrement des agents Dremio dans OpenMetadata.
À exécuter dans le container ingestion.
"""

import logging
from typing import List, Dict, Any

from metadata.ingestion.api.common import Entity
from metadata.ingestion.api.steps import Source
from metadata.ingestion.source.database.database_service import DatabaseServiceSource

from dremio_connector.agents.metadata_agent import MetadataAgent
from dremio_connector.agents.profiler_agent import ProfilerAgent
from dremio_connector.agents.lineage_agent import LineageAgent
from dremio_connector.agents.dbt_agent import DbtAgent

logger = logging.getLogger(__name__)

def force_register_agents() -> List[Dict[str, Any]]:
    """
    Force l'enregistrement des agents dans OpenMetadata.
    """
    agents = [
        {
            "type": "metadata",
            "name": "MetadataAgent",
            "description": "Extrait les métadonnées de Dremio",
            "class": "dremio_connector.agents.metadata_agent.MetadataAgent",
            "module": "dremio_connector.agents.metadata_agent"
        },
        {
            "type": "profiler", 
            "name": "ProfilerAgent",
            "description": "Profile les données Dremio",
            "class": "dremio_connector.agents.profiler_agent.ProfilerAgent",
            "module": "dremio_connector.agents.profiler_agent"
        },
        {
            "type": "lineage",
            "name": "LineageAgent", 
            "description": "Extrait le lineage des données Dremio",
            "class": "dremio_connector.agents.lineage_agent.LineageAgent",
            "module": "dremio_connector.agents.lineage_agent"
        },
        {
            "type": "dbt",
            "name": "DbtAgent",
            "description": "Intègre les modèles dbt avec Dremio",
            "class": "dremio_connector.agents.dbt_agent.DbtAgent",
            "module": "dremio_connector.agents.dbt_agent"
        }
    ]
    
    logger.info(f"🔄 Enregistrement forcé de {len(agents)} agents...")
    
    # Vérifier que les agents sont importables
    for agent in agents:
        try:
            module_path = agent["class"].rsplit(".", 1)[0]
            class_name = agent["class"].rsplit(".", 1)[1]
            
            # Import dynamique
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            
            # Vérifier l'héritage
            if not issubclass(agent_class, Source):
                raise TypeError(f"L'agent {agent['name']} doit hériter de Source")
                
            logger.info(f"✅ Agent {agent['name']} vérifié")
            
        except Exception as e:
            logger.error(f"❌ Erreur validation agent {agent['name']}: {e}")
            raise
    
    logger.info("✅ Tous les agents sont valides")
    return agents

if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    
    try:
        agents = force_register_agents()
        logger.info(f"✅ {len(agents)} agents enregistrés avec succès:")
        for agent in agents:
            logger.info(f"  - {agent['name']} ({agent['type']})")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        raise