"""
Dremio Connector for OpenMetadata
==================================

A connector to ingest metadata from Dremio Data Lake Platform into OpenMetadata.

Modules:
    - core: Core connector logic and source classes
    - clients: Client implementations for Dremio and OpenMetadata APIs
    - utils: Utility functions for logging, configuration, and data processing
"""

__version__ = "1.0.0"
__author__ = "Dremio OpenMetadataTeam"

from dremio_connector.core.sync_engine import DremioOpenMetadataSync, sync_dremio_to_openmetadata
from dremio_connector.clients.dremio_client import DremioClient
from dremio_connector.clients.openmetadata_client import OpenMetadataClient

__all__ = [
    "DremioOpenMetadataSync",
    "sync_dremio_to_openmetadata",
    "DremioClient", 
    "OpenMetadataClient",
]
