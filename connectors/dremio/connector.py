"""
DremioConnector : Classe principale du connecteur Dremio pour OpenMetadata
"""
from .dremio_client import DremioClient
from .openmetadata_client import OpenMetadataClient

class DremioConnector:
    def __init__(self, dremio_config, om_config):
        self.dremio = DremioClient(**dremio_config)
        self.om = OpenMetadataClient(**om_config)

    def test_connections(self):
        return self.dremio.test_connection() and self.om.test_connection()

    def ingest(self):
        # Découverte des sources, VDS, etc.
        # Mapping et création dans OpenMetadata
        pass

    # Autres méthodes métier à ajouter selon besoins
