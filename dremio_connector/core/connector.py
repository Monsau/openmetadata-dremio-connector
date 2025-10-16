"""
DremioConnector : Classe principale du connecteur Dremio pour OpenMetadata

⚠️ DEPRECATED: Ce module est obsolète. Utilisez plutôt :
    from dremio_connector.core.sync_engine import DremioOpenMetadataSync
    
Pour la compatibilité ascendante, cette classe reste disponible mais 
pointera vers le nouveau moteur dans une version future.

Migration recommandée :
    # Ancien code
    connector = DremioConnector(dremio_config, om_config)
    connector.ingest()
    
    # Nouveau code
    from dremio_connector import DremioOpenMetadataSync
    sync = DremioOpenMetadataSync(...)
    stats = sync.sync()
"""

import warnings
from dremio_connector.clients.dremio_client import DremioClient
from dremio_connector.clients.openmetadata_client import OpenMetadataClient

warnings.warn(
    "DremioConnector is deprecated. Use DremioOpenMetadataSync instead.",
    DeprecationWarning,
    stacklevel=2
)

class DremioConnector:
    """
    ⚠️ DEPRECATED: Utilisez DremioOpenMetadataSync à la place
    
    Classe wrapper pour compatibilité ascendante uniquement.
    """
    
    def __init__(self, dremio_config, om_config):
        self.dremio = DremioClient(**dremio_config)
        self.om = OpenMetadataClient(**om_config)

    def test_connections(self):
        """Test les connexions Dremio et OpenMetadata"""
        return self.dremio.test_connection() and self.om.test_connection()

    def ingest(self):
        """
        ⚠️ DEPRECATED: Utilisez DremioOpenMetadataSync.sync() à la place
        
        Cette méthode est conservée pour compatibilité mais n'est plus maintenue.
        """
        warnings.warn(
            "DremioConnector.ingest() is deprecated. Use DremioOpenMetadataSync.sync() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Placeholder - ne fait rien
        pass
