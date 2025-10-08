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
__author__ = "Dremio OpenMetadata Team"

from src.dremio_connector.core.dremio_source import DremioSource
from src.dremio_connector.clients.dremio_client import DremioClient
from src.dremio_connector.clients.openmetadata_client import OpenMetadataClient

__all__ = [
    "DremioSource",
    "DremioClient", 
    "OpenMetadataClient",
]
