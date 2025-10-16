"""Core module for Dremio connector functionality."""

from dremio_connector.core.sync_engine import (
    DremioOpenMetadataSync,
    DremioAutoDiscovery,
    OpenMetadataSyncEngine,
    sync_dremio_to_openmetadata
)

__all__ = [
    "DremioOpenMetadataSync",
    "DremioAutoDiscovery",
    "OpenMetadataSyncEngine",
    "sync_dremio_to_openmetadata"
]
