"""
Dremio Source Class - Main connector implementation for OpenMetadata
"""

import logging
from typing import Dict, List, Any, Optional
from src.dremio_connector.clients.dremio_client import DremioClient
from src.dremio_connector.clients.openmetadata_client import OpenMetadataClient

logger = logging.getLogger(__name__)


class DremioSource:
    """
    Main Dremio Source implementation for metadata ingestion.
    
    This class handles the extraction of metadata from Dremio and 
    ingestion into OpenMetadata.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Dremio Source with configuration.
        
        Args:
            config: Configuration dictionary containing:
                - dremioHost: Dremio server host
                - dremioPort: Dremio server port
                - dremioUsername: Authentication username
                - dremioPassword: Authentication password
                - openMetadataServerConfig: OpenMetadata server configuration
        """
        self.config = config
        
        # Initialize Dremio client
        dremio_config = {
            'host': config.get('dremioHost', 'localhost'),
            'port': int(config.get('dremioPort', 9047)),
            'username': config.get('dremioUsername', 'admin'),
            'password': config.get('dremioPassword', 'admin123')
        }
        self.dremio_client = DremioClient(**dremio_config)
        
        # Initialize OpenMetadata client
        om_config = config.get('openMetadataServerConfig', {})
        self.om_client = OpenMetadataClient(
            base_url=om_config.get('hostPort', 'http://localhost:8585/api'),
            jwt_token=om_config.get('securityConfig', {}).get('jwtToken', '')
        )
        
        self.service_name = config.get('serviceName', 'dremio-service')
        
    def test_connection(self) -> bool:
        """Test connections to both Dremio and OpenMetadata."""
        dremio_ok = self.dremio_client.test_connection()
        om_ok = self.om_client.health_check()
        
        if dremio_ok and om_ok:
            logger.info("✅ All connections successful")
            return True
        else:
            logger.error(f"❌ Connection failed - Dremio: {dremio_ok}, OpenMetadata: {om_ok}")
            return False
    
    def ingest_metadata(self) -> Dict[str, Any]:
        """
        Main ingestion workflow.
        
        Returns:
            Dict containing ingestion statistics and results
        """
        results = {
            'sources': 0,
            'datasets': 0,
            'vds': 0,
            'errors': []
        }
        
        try:
            # Create or get service
            logger.info("Creating OpenMetadata service...")
            service_created = self._create_service()
            
            if not service_created:
                logger.error("Failed to create service")
                results['errors'].append("Service creation failed")
                return results
            
            # Ingest sources
            if self.config.get('include_sources', True):
                logger.info("Ingesting Dremio sources...")
                sources_count = self._ingest_sources()
                results['sources'] = sources_count
            
            # Ingest VDS
            if self.config.get('include_vds', True):
                logger.info("Ingesting Dremio VDS...")
                vds_count = self._ingest_vds()
                results['vds'] = vds_count
            
            logger.info(f"✅ Ingestion complete: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")
            results['errors'].append(str(e))
            return results
    
    def _create_service(self) -> bool:
        """Create or update the Dremio service in OpenMetadata."""
        service_definition = {
            'name': self.service_name,
            'displayName': f'Dremio Data Lake Platform',
            'description': 'Dremio metadata ingestion service',
            'serviceType': 'CustomDatabase',
            'connection': {
                'config': {
                    'type': 'CustomDatabase',
                    'sourcePythonClass': 'dremio_connector.core.dremio_source.DremioSource',
                    'connectionOptions': {
                        'dremioHost': self.config.get('dremioHost'),
                        'dremioPort': str(self.config.get('dremioPort')),
                    }
                }
            }
        }
        
        return self.om_client.create_database_service(service_definition)
    
    def _ingest_sources(self) -> int:
        """Ingest Dremio sources as database schemas."""
        sources = self.dremio_client.get_sources()
        count = 0
        
        for source in sources:
            try:
                # Create schema for each source
                schema_definition = {
                    'name': source['name'],
                    'displayName': source.get('displayName', source['name']),
                    'description': source.get('description', f"Dremio source: {source['name']}"),
                    'service': self.service_name
                }
                
                if self.om_client.create_database_schema(schema_definition):
                    count += 1
                    
                    # Ingest datasets from this source
                    datasets = self.dremio_client.get_source_datasets(source['id'])
                    for dataset in datasets:
                        self._create_table(dataset, source['name'])
                        
            except Exception as e:
                logger.error(f"Error ingesting source {source['name']}: {e}")
        
        return count
    
    def _ingest_vds(self) -> int:
        """Ingest Dremio VDS as views."""
        vds_list = self.dremio_client.get_vds()
        count = 0
        
        for vds in vds_list:
            try:
                # Get VDS details including SQL
                vds_details = self.dremio_client.get_vds_details(vds['id'])
                
                # Extract schema name from path
                path_parts = vds.get('path', '').split('.')
                schema_name = path_parts[0] if len(path_parts) > 0 else 'default'
                
                # Create table definition for VDS
                table_definition = {
                    'name': vds['name'],
                    'displayName': vds.get('displayName', vds['name']),
                    'description': vds.get('description', ''),
                    'tableType': 'View',
                    'viewDefinition': vds_details.get('sql', ''),
                    'databaseSchema': schema_name,
                    'service': self.service_name,
                    'columns': self._get_vds_columns(vds['id'])
                }
                
                if self.om_client.create_table(table_definition):
                    count += 1
                    
            except Exception as e:
                logger.error(f"Error ingesting VDS {vds['name']}: {e}")
        
        return count
    
    def _create_table(self, dataset: Dict[str, Any], schema_name: str) -> bool:
        """Create a table entity in OpenMetadata."""
        try:
            # Get table schema/columns
            columns = self._get_table_columns(dataset['id'])
            
            table_definition = {
                'name': dataset['name'],
                'displayName': dataset.get('displayName', dataset['name']),
                'description': dataset.get('description', ''),
                'tableType': 'Regular',
                'databaseSchema': schema_name,
                'service': self.service_name,
                'columns': columns
            }
            
            return self.om_client.create_table(table_definition)
            
        except Exception as e:
            logger.error(f"Error creating table {dataset['name']}: {e}")
            return False
    
    def _get_table_columns(self, table_id: str) -> List[Dict[str, Any]]:
        """Get column definitions for a table."""
        try:
            schema = self.dremio_client.get_table_schema(table_id)
            columns = []
            
            for field in schema:
                columns.append({
                    'name': field['name'],
                    'dataType': self._map_data_type(field['type']),
                    'description': field.get('description', ''),
                    'dataLength': 255
                })
            
            return columns
            
        except Exception as e:
            logger.error(f"Error getting table columns: {e}")
            return []
    
    def _get_vds_columns(self, vds_id: str) -> List[Dict[str, Any]]:
        """Get column definitions for a VDS."""
        return self._get_table_columns(vds_id)
    
    def _map_data_type(self, dremio_type: str) -> str:
        """Map Dremio data types to OpenMetadata data types."""
        type_mapping = {
            'INTEGER': 'INT',
            'BIGINT': 'BIGINT',
            'FLOAT': 'FLOAT',
            'DOUBLE': 'DOUBLE',
            'VARCHAR': 'VARCHAR',
            'BOOLEAN': 'BOOLEAN',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'TIMESTAMP': 'TIMESTAMP',
            'DECIMAL': 'DECIMAL'
        }
        
        return type_mapping.get(dremio_type.upper(), 'VARCHAR')
