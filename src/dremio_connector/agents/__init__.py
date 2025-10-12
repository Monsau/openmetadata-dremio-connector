"""
Agents OpenMetadata pour le connecteur Dremio.

Ce module contient les agents personnalisés compatibles avec OpenMetadata :
- DbtAgent : Ingestion dbt avec lineage automatique
- MetadataAgent : Synchronisation métadonnées Dremio
- LineageAgent : Vérification et visualisation lineage
- ProfilerAgent : Profilage et qualité des données
"""

from .dbt_agent import DbtAgent
from .metadata_agent import MetadataAgent
from .lineage_agent import LineageAgent
from .profiler_agent import ProfilerAgent

__all__ = [
    'DbtAgent',
    'MetadataAgent', 
    'LineageAgent',
    'ProfilerAgent'
]