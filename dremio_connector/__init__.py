"""
Dremio Connector for OpenMetadata
==================================

A unified 4-in-1 connector to ingest metadata from Dremio Data Lake Platform into OpenMetadata.

Features:
    - Metadata: Full topology discovery (Databases → Schemas → Tables → Columns)
    - Profiling: Statistical analysis with configurable sampling
    - Auto-Classification: Automatic PII/Sensitive/Financial tags
    - DBT Integration: Enrichment with DBT descriptions and tags

Modules:
    - dremio_source: Main unified connector (4-in-1 agent)
    - core.sync_engine: Dremio API client and discovery engine
"""

__version__ = "2.0.0"
__author__ = "Dremio OpenMetadata Team"

from dremio_connector.dremio_source import DremioConnector
from dremio_connector.core.sync_engine import DremioAutoDiscovery, DremioOpenMetadataSync, sync_dremio_to_openmetadata

__all__ = [
    "DremioConnector",
    "DremioAutoDiscovery",
    "DremioOpenMetadataSync",
    "sync_dremio_to_openmetadata",
]
