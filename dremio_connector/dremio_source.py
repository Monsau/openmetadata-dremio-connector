"""
Custom Dremio Connector for OpenMetadata

Enhanced connector that uses DremioAutoDiscovery to find all sources, 
databases, schemas, and tables from Dremio.
"""

from typing import Iterable, Optional, List, Tuple
import logging

from metadata.ingestion.api.common import Entity
from metadata.ingestion.api.steps import Source
from metadata.ingestion.source.database.database_service import DatabaseServiceSource
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.ingestion.api.models import Either
from metadata.generated.schema.api.data.createDatabase import CreateDatabaseRequest
from metadata.generated.schema.api.data.createDatabaseSchema import CreateDatabaseSchemaRequest
from metadata.generated.schema.api.data.createTable import CreateTableRequest
from metadata.generated.schema.entity.data.table import Column, DataType, TableType
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseService,
)
from metadata.generated.schema.metadataIngestion.workflow import (
    Source as WorkflowSource,
)
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.utils.logger import ingestion_logger
from metadata.utils import fqn

# Import votre logique de découverte Dremio
from dremio_connector.core.sync_engine import DremioAutoDiscovery

logger = ingestion_logger()


class DremioConnector(DatabaseServiceSource):
    """
    Custom connector to ingest Dremio metadata using DremioAutoDiscovery
    """

    def __init__(self, config: WorkflowSource, metadata: OpenMetadata):
        self.config = config
        self.metadata = metadata
        self.source_config = config.sourceConfig.config
        self.service_connection = config.serviceConnection.root.config
        self.dremio_client = None
        self.database_source_state = set()
        super().__init__()

    @classmethod
    def create(
        cls, config_dict: dict, metadata: OpenMetadata, pipeline_name: Optional[str] = None
    ) -> "DremioConnector":
        config: WorkflowSource = WorkflowSource.parse_obj(config_dict)
        return cls(config, metadata)

    def prepare(self):
        """Initialize Dremio client and fail if not valid"""
        dremio_url = 'http://host.docker.internal:9047'
        username = 'admin'
        password = 'admin123'
        try:
            # Try to get connectionOptions from OpenMetadata config
            if hasattr(self.config, 'serviceConnection'):
                service_conn = self.config.serviceConnection
                if hasattr(service_conn, '__root__'):
                    root = service_conn.__root__
                    if hasattr(root, 'connectionOptions'):
                        conn_options = root.connectionOptions
                        if isinstance(conn_options, dict) and conn_options:
                            dremio_url = conn_options.get('url', dremio_url)
                            username = conn_options.get('username', username)
                            password = conn_options.get('password', password)
                            logger.info(f"📋 Found connectionOptions (Pattern 1): {list(conn_options.keys())}")
                    elif hasattr(root, 'config') and hasattr(root.config, 'connectionOptions'):
                        conn_options = root.config.connectionOptions
                        if isinstance(conn_options, dict) and conn_options:
                            dremio_url = conn_options.get('url', dremio_url)
                            username = conn_options.get('username', username)
                            password = conn_options.get('password', password)
                            logger.info(f"📋 Found connectionOptions (Pattern 1b): {list(conn_options.keys())}")
                elif hasattr(service_conn, 'connectionOptions'):
                    conn_options = service_conn.connectionOptions
                    if isinstance(conn_options, dict) and conn_options:
                        dremio_url = conn_options.get('url', dremio_url)
                        username = conn_options.get('username', username)
                        password = conn_options.get('password', password)
                        logger.info(f"📋 Found connectionOptions (Pattern 2): {list(conn_options.keys())}")
                elif hasattr(service_conn, '__dict__'):
                    if 'connectionOptions' in service_conn.__dict__:
                        conn_options = service_conn.__dict__['connectionOptions']
                        if isinstance(conn_options, dict) and conn_options:
                            dremio_url = conn_options.get('url', dremio_url)
                            username = conn_options.get('username', username)
                            password = conn_options.get('password', password)
                            logger.info(f"📋 Found connectionOptions (Pattern 3): {list(conn_options.keys())}")
        except Exception as config_error:
            logger.warning(f"⚠️  Could not read connectionOptions, using defaults: {config_error}")
            import traceback
            traceback.print_exc()

        logger.info(f"🔌 Connecting to Dremio at {dremio_url} as {username}")
        self.dremio_client = DremioAutoDiscovery(
            url=dremio_url,
            username=username,
            password=password
        )
        if not self.dremio_client or not self.dremio_client.authenticate():
            logger.error("❌ Dremio authentication failed, raising exception")
            raise Exception("Dremio authentication failed in prepare()")

    def yield_create_request_database_service(self, config: WorkflowSource):
        yield Either(
            right=self.metadata.get_create_service_from_source(
                entity=DatabaseService, config=config
            )
        )

    # ============================================================================
    # TOPOLOGY METHODS - Called automatically by OpenMetadata framework
    # ============================================================================
    
    def get_database_names(self) -> Iterable[str]:
        """Return list of database names (one per Dremio source)"""
        if not self.dremio_client:
            logger.error("❌ Dremio client not initialized")
            return
        
        try:
            catalog = self.dremio_client.get_catalog_item()
            if not catalog or 'data' not in catalog:
                logger.warning("⚠️  No catalog data found")
                return
            
            sources = catalog.get('data', [])
            logger.info(f"📦 Found {len(sources)} Dremio sources")
            
            for source in sources:
                source_name = source.get('path', ['unknown'])[0]
                logger.info(f"📂 Database name: {source_name}")
                yield source_name
                
        except Exception as e:
            logger.error(f"❌ Error getting database names: {e}")
            import traceback
            traceback.print_exc()

    def yield_database(self, database_name: str) -> Iterable[Either[CreateDatabaseRequest]]:
        """Create a database for one Dremio source"""
        try:
            logger.info(f"📂 Creating database: {database_name}")
            
            database_request = CreateDatabaseRequest(
                name=database_name,
                displayName=database_name,
                description=f"Dremio source: {database_name}",
                service=self.context.get().database_service,
            )
            
            yield Either(right=database_request)
            self.register_record_database_request(database_request=database_request)
            
        except Exception as e:
            logger.error(f"❌ Error yielding database {database_name}: {e}")
            import traceback
            traceback.print_exc()

    def get_database_schema_names(self) -> Iterable[str]:
        """Return list of schema names (one 'default' schema per database)"""
        logger.info(f"🗂️  Yielding default schema")
        yield "default"

    def yield_database_schema(self, schema_name: str) -> Iterable[Either[CreateDatabaseSchemaRequest]]:
        """Create a schema for the current database"""
        try:
            database_fqn = fqn.build(
                self.metadata,
                entity_type=Database,
                service_name=self.context.get().database_service,
                database_name=self.context.get().database,
            )
            
            logger.info(f"🗂️  Creating schema: {schema_name} for database {self.context.get().database}")
            
            schema_request = CreateDatabaseSchemaRequest(
                name=schema_name,
                displayName=schema_name,
                description=f"Default schema for {self.context.get().database}",
                database=database_fqn,
            )
            
            yield Either(right=schema_request)
            self.register_record_schema_request(schema_request=schema_request)
            
        except Exception as e:
            logger.error(f"❌ Error yielding schema {schema_name}: {e}")
            import traceback
            traceback.print_exc()

    def get_tables_name_and_type(self) -> Optional[Iterable[Tuple[str, TableType]]]:
        """Return list of tables (one metadata table per database)"""
        try:
            current_db = self.context.get().database
            table_name = f"{current_db}_metadata"
            logger.info(f"📋 Yielding table: {table_name}")
            yield (table_name, TableType.Regular)
            
        except Exception as e:
            logger.error(f"❌ Error getting table names: {e}")
            import traceback
            traceback.print_exc()

    def yield_table(self, table_name_and_type: Tuple[str, TableType]) -> Iterable[Either[CreateTableRequest]]:
        """Create a metadata table"""
        table_name, table_type = table_name_and_type
        
        try:
            schema_fqn = fqn.build(
                self.metadata,
                entity_type=DatabaseSchema,
                service_name=self.context.get().database_service,
                database_name=self.context.get().database,
                schema_name=self.context.get().database_schema,
            )
            
            logger.info(f"📋 Creating table: {table_name} in schema {self.context.get().database_schema}")
            
            columns = [
                Column(
                    name="source_id",
                    displayName="Source ID",
                    dataType=DataType.VARCHAR,
                    dataLength=100,
                    description="Dremio source identifier"
                ),
                Column(
                    name="source_name",
                    displayName="Source Name",
                    dataType=DataType.VARCHAR,
                    dataLength=255,
                    description="Name of the Dremio source"
                ),
                Column(
                    name="source_type",
                    displayName="Source Type",
                    dataType=DataType.VARCHAR,
                    dataLength=50,
                    description="Type of the source (SOURCE, SPACE, etc.)"
                ),
                Column(
                    name="created_at",
                    displayName="Created At",
                    dataType=DataType.TIMESTAMP,
                    description="Creation timestamp"
                ),
            ]
            
            table_request = CreateTableRequest(
                name=table_name,
                displayName=table_name,
                description=f"Metadata table for Dremio source {self.context.get().database}",
                tableType=table_type,
                columns=columns,
                databaseSchema=schema_fqn,
            )
            
            yield Either(right=table_request)
            self.register_record(table_request=table_request)
            
        except Exception as e:
            logger.error(f"❌ Error yielding table {table_name}: {e}")
            import traceback
            traceback.print_exc()

    # ============================================================================
    # REQUIRED ABSTRACT METHODS (stubs for optional functionality)
    # ============================================================================

    def get_stored_procedures(self) -> Iterable:
        """No stored procedures to process"""
        return []

    def yield_stored_procedure(self, stored_procedure) -> Iterable[Either]:
        """Not implemented"""
        yield from []

    def yield_view_lineage(self) -> Iterable[Either]:
        """Not implemented"""
        yield from []

    def yield_tag(self, schema_name: str) -> Iterable[Either]:
        """Not implemented"""
        yield from []

    def test_connection(self) -> None:
        """Test connection to Dremio"""
        try:
            if self.dremio_client and self.dremio_client.authenticate():
                logger.info("✅ Dremio connection test successful")
            else:
                logger.error("❌ Dremio connection test failed")
        except Exception as e:
            logger.error(f"❌ Error testing connection: {e}")

    @classmethod
    def get_available_agents(cls) -> List[dict]:
        """
        Expose all agent types to OpenMetadata for UI discovery.
        """
        from dremio_connector.agents.agent_manager import AgentRegistry
        agents = AgentRegistry.get_available_agents()
        logger.info(f"📋 Agents exposés à OpenMetadata: {[a['type'] for a in agents]}")
        return agents

    def close(self):
        """Cleanup"""
        logger.info("👋 Closing Dremio connector")
        self.dremio_client = None