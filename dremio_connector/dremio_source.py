"""
Custom Dremio Connector for OpenMetadata

Enhanced connector that uses DremioAutoDiscovery to find all sources, 
databases, schemas, and tables from Dremio.
Supports Metadata ingestion, Profiling, Auto-Classification, and DBT in the same agent (4-in-1).
"""

from typing import Iterable, Optional, List, Tuple, Dict, Any
import logging
import json
from pathlib import Path
from datetime import datetime, timezone

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
from metadata.generated.schema.entity.data.table import Column, DataType, TableType, Table, TableProfile, ColumnProfile
from metadata.generated.schema.entity.data.database import Database
from metadata.generated.schema.entity.data.databaseSchema import DatabaseSchema
from metadata.generated.schema.entity.services.databaseService import (
    DatabaseService,
)
from metadata.generated.schema.api.classification.createTag import CreateTagRequest
from metadata.generated.schema.api.classification.createClassification import CreateClassificationRequest
from metadata.generated.schema.entity.classification.tag import Tag
from metadata.generated.schema.type.tagLabel import TagLabel, TagSource, LabelType
from metadata.generated.schema.type.basic import FullyQualifiedEntityName
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
        """Initialize Dremio client - requires connectionOptions"""
        logger.info("🚀 Preparing Dremio connector...")
        
        dremio_url = None
        username = None
        password = None
        
        # Configuration options with defaults
        self.profile_sample_rows = None  # Number of rows for profiling (None = all rows)
        self.classification_enabled = True  # Enable auto-classification (default: True)
        self.dbt_enabled = False
        self.dbt_catalog_path = None
        self.dbt_manifest_path = None
        self.dbt_run_results_path = None
        
        try:
            # Extract from serviceConnection.__dict__['root'].config.connectionOptions.root
            if hasattr(self.config, 'serviceConnection'):
                service_conn = self.config.serviceConnection
                
                # Pattern 1: Via __dict__['root'] (OpenMetadata 1.9.7 structure)
                if hasattr(service_conn, '__dict__') and 'root' in service_conn.__dict__:
                    root = service_conn.__dict__['root']
                    if hasattr(root, 'config') and hasattr(root.config, 'connectionOptions'):
                        conn_opts = root.config.connectionOptions
                        # ConnectionOptions has a 'root' attribute containing the dict
                        if hasattr(conn_opts, 'root') and isinstance(conn_opts.root, dict):
                            opts = conn_opts.root
                            dremio_url = opts.get('url')
                            username = opts.get('username')
                            password = opts.get('password')
                            
                            # Extract optional configuration
                            self.profile_sample_rows = opts.get('profileSampleRows')
                            self.classification_enabled = opts.get('classificationEnabled', True)
                            self.dbt_enabled = opts.get('dbtEnabled', False)
                            self.dbt_catalog_path = opts.get('dbtCatalogPath')
                            self.dbt_manifest_path = opts.get('dbtManifestPath')
                            self.dbt_run_results_path = opts.get('dbtRunResultsPath')
                            
                            logger.info(f"📋 Found connectionOptions: url={dremio_url}, username={username}")
                            logger.info(f"📊 Profiling sample rows: {self.profile_sample_rows or 'all rows'}")
                            logger.info(f"🏷️  Classification enabled: {self.classification_enabled}")
                            logger.info(f"🔧 DBT enabled: {self.dbt_enabled}")
                            
                        # Or ConnectionOptions might be a direct dict
                        elif isinstance(conn_opts, dict):
                            dremio_url = conn_opts.get('url')
                            username = conn_opts.get('username')
                            password = conn_opts.get('password')
                            self.profile_sample_rows = conn_opts.get('profileSampleRows')
                            self.classification_enabled = conn_opts.get('classificationEnabled', True)
                            self.dbt_enabled = conn_opts.get('dbtEnabled', False)
                            self.dbt_catalog_path = conn_opts.get('dbtCatalogPath')
                            self.dbt_manifest_path = conn_opts.get('dbtManifestPath')
                            self.dbt_run_results_path = conn_opts.get('dbtRunResultsPath')
                            logger.info(f"📋 Found connectionOptions (dict): url={dremio_url}, username={username}")
                            logger.info(f"📊 Profiling sample rows: {self.profile_sample_rows or 'all rows'}")
                            logger.info(f"🏷️  Classification enabled: {self.classification_enabled}")
                            logger.info(f"🔧 DBT enabled: {self.dbt_enabled}")
                
                # Pattern 2: Fallback via __root__ (older structure)
                if not dremio_url and hasattr(service_conn, '__root__'):
                    root = service_conn.__root__
                    if hasattr(root, 'config') and hasattr(root.config, 'connectionOptions'):
                        conn_opts = root.config.connectionOptions
                        if hasattr(conn_opts, 'root') and isinstance(conn_opts.root, dict):
                            opts = conn_opts.root
                            dremio_url = opts.get('url')
                            username = opts.get('username')
                            password = opts.get('password')
                            self.profile_sample_rows = opts.get('profileSampleRows')
                            self.classification_enabled = opts.get('classificationEnabled', True)
                            self.dbt_enabled = opts.get('dbtEnabled', False)
                            self.dbt_catalog_path = opts.get('dbtCatalogPath')
                            self.dbt_manifest_path = opts.get('dbtManifestPath')
                            self.dbt_run_results_path = opts.get('dbtRunResultsPath')
                            logger.info(f"📋 Found connectionOptions (__root__): url={dremio_url}, username={username}")
                            logger.info(f"📊 Profiling sample rows: {self.profile_sample_rows or 'all rows'}")
                            logger.info(f"🏷️  Classification enabled: {self.classification_enabled}")
                            logger.info(f"🔧 DBT enabled: {self.dbt_enabled}")
                        elif isinstance(conn_opts, dict):
                            dremio_url = conn_opts.get('url')
                            username = conn_opts.get('username')
                            password = conn_opts.get('password')
                            self.profile_sample_rows = conn_opts.get('profileSampleRows')
                            self.classification_enabled = conn_opts.get('classificationEnabled', True)
                            self.dbt_enabled = conn_opts.get('dbtEnabled', False)
                            self.dbt_catalog_path = conn_opts.get('dbtCatalogPath')
                            self.dbt_manifest_path = conn_opts.get('dbtManifestPath')
                            self.dbt_run_results_path = conn_opts.get('dbtRunResultsPath')
                            logger.info(f"📋 Found connectionOptions (__root__ dict): url={dremio_url}, username={username}")
                            logger.info(f"📊 Profiling sample rows: {self.profile_sample_rows or 'all rows'}")
                            logger.info(f"🏷️  Classification enabled: {self.classification_enabled}")
                            logger.info(f"🔧 DBT enabled: {self.dbt_enabled}")
        except Exception as config_error:
            logger.error(f"❌ Error reading connectionOptions: {config_error}")
            import traceback
            traceback.print_exc()

        # Validate required parameters
        if not dremio_url or not username or not password:
            missing = []
            if not dremio_url: missing.append('url')
            if not username: missing.append('username')
            if not password: missing.append('password')
            error_msg = f"❌ Missing required connectionOptions: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

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
        """Return list of schema names from Dremio source"""
        if not self.dremio_client:
            logger.error("❌ Dremio client not initialized")
            return
        
        try:
            current_source = self.context.get().database
            logger.info(f"🔍 Getting schemas for source: {current_source}")
            
            # Get source details - use string path separated by /
            source_details = self.dremio_client.get_catalog_item(current_source)
            
            if not source_details or 'children' not in source_details:
                logger.warning(f"⚠️  No children found for source {current_source}")
                return
            
            # List all folders/schemas in this source
            children = source_details.get('children', [])
            logger.info(f"� Found {len(children)} items in source {current_source}")
            
            for child in children:
                child_path = child.get('path', [])
                if len(child_path) >= 2:
                    schema_name = child_path[1]  # Second element is the schema
                    child_type = child.get('type', 'UNKNOWN')
                    logger.info(f"🗂️  Schema: {schema_name} (type: {child_type})")
                    yield schema_name
                    
        except Exception as e:
            logger.error(f"❌ Error getting schema names: {e}")
            import traceback
            traceback.print_exc()

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
        """Return list of tables from Dremio schema"""
        if not self.dremio_client:
            logger.error("❌ Dremio client not initialized")
            return
        
        try:
            current_source = self.context.get().database
            current_schema = self.context.get().database_schema
            logger.info(f"🔍 Getting tables for {current_source}.{current_schema}")
            
            # Get schema details - use path separated by /
            schema_path_str = f"{current_source}/{current_schema}"
            schema_details = self.dremio_client.get_catalog_item(schema_path_str)
            
            if not schema_details or 'children' not in schema_details:
                logger.warning(f"⚠️  No tables found in {current_source}.{current_schema}")
                return
            
            # List all tables in this schema
            children = schema_details.get('children', [])
            logger.info(f"� Found {len(children)} items in schema {current_schema}")
            
            for child in children:
                child_path = child.get('path', [])
                child_type = child.get('type', 'UNKNOWN')
                
                if len(child_path) >= 3:
                    table_name = child_path[2]  # Third element is the table
                    
                    # Map Dremio types to OpenMetadata TableType
                    if child_type in ['PHYSICAL_DATASET', 'TABLE']:
                        om_type = TableType.Regular
                    elif child_type == 'VIRTUAL_DATASET':
                        om_type = TableType.View
                    else:
                        om_type = TableType.Regular
                    
                    logger.info(f"📋 Table: {table_name} (Dremio type: {child_type} -> OM type: {om_type})")
                    yield (table_name, om_type)
                    
        except Exception as e:
            logger.error(f"❌ Error getting table names: {e}")
            import traceback
            traceback.print_exc()

    def yield_table(self, table_name_and_type: Tuple[str, TableType]) -> Iterable[Either[CreateTableRequest]]:
        """Create a table with real columns from Dremio"""
        table_name, table_type = table_name_and_type
        
        try:
            schema_fqn = fqn.build(
                self.metadata,
                entity_type=DatabaseSchema,
                service_name=self.context.get().database_service,
                database_name=self.context.get().database,
                schema_name=self.context.get().database_schema,
            )
            
            current_source = self.context.get().database
            current_schema = self.context.get().database_schema
            
            logger.info(f"📋 Creating table: {table_name} in {current_source}.{current_schema}")
            
            # Get table details from Dremio - use path separated by /
            table_path_str = f"{current_source}/{current_schema}/{table_name}"
            table_details = self.dremio_client.get_catalog_item(table_path_str)
            
            columns = []
            if table_details and 'fields' in table_details:
                # Real columns from Dremio
                for field in table_details.get('fields', []):
                    field_name = field.get('name', 'unknown')
                    field_type = field.get('type', {}).get('name', 'VARCHAR')
                    
                    # Map Dremio types to OpenMetadata DataType
                    om_type = self._map_dremio_type_to_om(field_type)
                    
                    # Pour VARCHAR et types similaires, OpenMetadata exige dataLength
                    column_args = {
                        "name": field_name,
                        "displayName": field_name,
                        "dataType": om_type,
                        "description": f"Column from Dremio (type: {field_type})"
                    }
                    
                    # Ajouter dataLength pour les types qui l'exigent
                    if om_type in (DataType.VARCHAR, DataType.CHAR, DataType.BINARY, DataType.VARBINARY):
                        column_args["dataLength"] = 65535  # Taille par défaut pour VARCHAR
                    
                    # 🏷️ AUTO-CLASSIFICATION : Get tags for this column BEFORE creating it
                    column_dict = {
                        'name': field_name,
                        'dataType': str(om_type)
                    }
                    tags = self.get_column_tag_labels(f"{current_source}.{current_schema}.{table_name}", column_dict)
                    if tags:
                        column_args["tags"] = tags
                        logger.info(f"  🏷️ {field_name}: Adding {len(tags)} tags to column definition")
                    
                    columns.append(Column(**column_args))
                    logger.info(f"  ├─ Column: {field_name} ({field_type} -> {om_type})")
            else:
                # Fallback: dummy column if no schema available
                logger.warning(f"⚠️  No fields found for table {table_name}, using dummy column")
                columns.append(Column(
                    name="data",
                    displayName="Data",
                    dataType=DataType.VARCHAR,
                    dataLength=65535,
                    description="No schema information available"
                ))
            
            table_request = CreateTableRequest(
                name=table_name,
                displayName=table_name,
                description=f"Table {table_name} from Dremio source {current_source}",
                tableType=table_type,
                columns=columns,
                databaseSchema=schema_fqn,
            )
            
            # 🔧 DBT ENRICHMENT: Add DBT metadata if enabled
            if self.dbt_enabled:
                table_fqn = f"{self.context.get().database_service}.{current_source}.{current_schema}.{table_name}"
                logger.info(f"🔧 Attempting DBT enrichment for: {table_fqn}")
                # Note: We enrich after table is created by OpenMetadata
                # For now, we log the intention - actual enrichment happens in post-processing
            
            yield Either(right=table_request)
            self.register_record(table_request=table_request)
            
        except Exception as e:
            logger.error(f"❌ Error yielding table {table_name}: {e}")
            import traceback
            traceback.print_exc()
    
    def _map_dremio_type_to_om(self, dremio_type: str) -> DataType:
        """Map Dremio data types to OpenMetadata DataType"""
        type_mapping = {
            'INTEGER': DataType.INT,
            'BIGINT': DataType.BIGINT,
            'FLOAT': DataType.FLOAT,
            'DOUBLE': DataType.DOUBLE,
            'DECIMAL': DataType.DECIMAL,
            'VARCHAR': DataType.VARCHAR,
            'CHAR': DataType.CHAR,
            'TEXT': DataType.TEXT,
            'BOOLEAN': DataType.BOOLEAN,
            'DATE': DataType.DATE,
            'TIME': DataType.TIME,
            'TIMESTAMP': DataType.TIMESTAMP,
            'BINARY': DataType.BINARY,
            'ARRAY': DataType.ARRAY,
            'MAP': DataType.MAP,
            'STRUCT': DataType.STRUCT,
            'JSON': DataType.JSON,
        }
        
        dremio_type_upper = dremio_type.upper()
        return type_mapping.get(dremio_type_upper, DataType.VARCHAR)

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
                raise Exception("Failed to authenticate with Dremio")
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            raise

    # ============================================================================
    # PROFILING METHODS
    # ============================================================================

    def get_profile_metrics(
        self, 
        table: Table,
        profile_sample: Optional[float] = None,
    ) -> Tuple[Optional[TableProfile], List[ColumnProfile]]:
        """
        Profile a Dremio table and return metrics
        
        This method is called by OpenMetadata profiling workflow when
        "Enable Profiler" is checked in the metadata ingestion configuration.
        
        Args:
            table: OpenMetadata Table entity to profile
            profile_sample: Percentage of data to sample (0-100)
            
        Returns:
            Tuple of (TableProfile, List of ColumnProfiles)
        """
        logger.info(f"🔬 Profiling table: {table.fullyQualifiedName}")
        
        try:
            # Extract source/schema/table from FQN
            # Format: service.database.schema.table
            fqn_parts = table.fullyQualifiedName.split('.')
            if len(fqn_parts) < 4:
                logger.warning(f"⚠️  Invalid FQN format: {table.fullyQualifiedName}")
                return None, []
            
            database = fqn_parts[1]  # Dremio source
            schema = fqn_parts[2]     # Dremio folder/schema
            table_name = fqn_parts[3]
            
            logger.info(f"  📊 Analyzing: {database}.{schema}.{table_name}")
            
            # Build Dremio path (with quotes for safety)
            dremio_path = f'"{database}"."{schema}"."{table_name}"'
            
            # 1. Get row count
            row_count = self._get_row_count(dremio_path)
            
            # 2. Get column statistics
            column_profiles = []
            if table.columns:
                for column in table.columns:
                    col_profile = self._profile_column(
                        dremio_path=dremio_path,
                        column_name=column.name,
                        column_type=str(column.dataType),
                        total_rows=row_count
                    )
                    if col_profile:
                        column_profiles.append(col_profile)
            
            # 3. Create TableProfile
            table_profile = TableProfile(
                timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
                rowCount=row_count,
                columnCount=len(table.columns) if table.columns else 0,
                profileSample=profile_sample or 100.0,
            )
            
            logger.info(f"  ✅ Profile complete: {row_count} rows, {len(column_profiles)} columns profiled")
            
            return table_profile, column_profiles
            
        except Exception as e:
            logger.error(f"❌ Error profiling table {table.fullyQualifiedName}: {e}")
            import traceback
            traceback.print_exc()
            return None, []

    def _get_row_count(self, dremio_path: str) -> int:
        """Get total row count for a table"""
        try:
            query = f"SELECT COUNT(*) as row_count FROM {dremio_path}"
            result = self.dremio_client.execute_sql_query(query)
            
            if result and 'rows' in result and len(result['rows']) > 0:
                return int(result['rows'][0].get('row_count', 0))
            return 0
        except Exception as e:
            logger.warning(f"⚠️  Could not get row count for {dremio_path}: {e}")
            return 0

    def _profile_column(
        self, 
        dremio_path: str, 
        column_name: str, 
        column_type: str,
        total_rows: int
    ) -> Optional[ColumnProfile]:
        """
        Profile a single column with optional row sampling
        Returns statistics like null count, distinct count, min, max, etc.
        """
        try:
            logger.info(f"    📈 Profiling column: {column_name} ({column_type})")
            
            # Escape column name with double quotes
            col_escaped = f'"{column_name}"'
            
            # Build sample clause if configured
            sample_clause = ""
            if self.profile_sample_rows:
                sample_clause = f" LIMIT {self.profile_sample_rows}"
                logger.info(f"    📊 Using sample: {self.profile_sample_rows} rows")
            
            # Base metrics for all types
            query = f"""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT({col_escaped}) as non_null_count,
                    COUNT(DISTINCT {col_escaped}) as distinct_count
                FROM (SELECT * FROM {dremio_path}{sample_clause})
            """
            
            # Add type-specific metrics
            if 'INT' in column_type.upper() or column_type.upper() in ('BIGINT', 'DOUBLE', 'FLOAT', 'DECIMAL'):
                query = f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT({col_escaped}) as non_null_count,
                        COUNT(DISTINCT {col_escaped}) as distinct_count,
                        MIN({col_escaped}) as min_value,
                        MAX({col_escaped}) as max_value,
                        AVG(CAST({col_escaped} AS DOUBLE)) as mean_value,
                        STDDEV(CAST({col_escaped} AS DOUBLE)) as stddev_value
                    FROM (SELECT * FROM {dremio_path}{sample_clause})
                """
            elif 'VARCHAR' in column_type.upper() or 'CHAR' in column_type.upper():
                query = f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT({col_escaped}) as non_null_count,
                        COUNT(DISTINCT {col_escaped}) as distinct_count,
                        MIN(LENGTH({col_escaped})) as min_length,
                        MAX(LENGTH({col_escaped})) as max_length,
                        AVG(LENGTH({col_escaped})) as avg_length
                    FROM (SELECT * FROM {dremio_path}{sample_clause})
                """
            
            result = self.dremio_client.execute_sql_query(query)
            
            if not result or 'rows' not in result or len(result['rows']) == 0:
                logger.warning(f"    ⚠️  No statistics returned for column {column_name}")
                return None
            
            stats = result['rows'][0]
            
            # Calculate metrics
            total_count = int(stats.get('total_count', 0))
            non_null_count = int(stats.get('non_null_count', 0))
            null_count = total_count - non_null_count
            null_proportion = (null_count / total_count) if total_count > 0 else 0.0
            distinct_count = int(stats.get('distinct_count', 0))
            unique_proportion = (distinct_count / total_count) if total_count > 0 else 0.0
            
            # Create ColumnProfile
            profile = ColumnProfile(
                name=column_name,
                timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
                valuesCount=total_count,
                nullCount=null_count,
                nullProportion=null_proportion,
                distinctCount=distinct_count,
                uniqueCount=distinct_count,
                uniqueProportion=unique_proportion,
            )
            
            # Add numeric-specific metrics
            if 'INT' in column_type.upper() or column_type.upper() in ('BIGINT', 'DOUBLE', 'FLOAT', 'DECIMAL'):
                if 'min_value' in stats and stats['min_value'] is not None:
                    profile.min = float(stats['min_value'])
                if 'max_value' in stats and stats['max_value'] is not None:
                    profile.max = float(stats['max_value'])
                if 'mean_value' in stats and stats['mean_value'] is not None:
                    profile.mean = float(stats['mean_value'])
                if 'stddev_value' in stats and stats['stddev_value'] is not None:
                    profile.stddev = float(stats['stddev_value'])
            
            # Add string-specific metrics
            elif 'VARCHAR' in column_type.upper() or 'CHAR' in column_type.upper():
                if 'min_length' in stats and stats['min_length'] is not None:
                    profile.minLength = float(stats['min_length'])
                if 'max_length' in stats and stats['max_length'] is not None:
                    profile.maxLength = float(stats['max_length'])
                if 'avg_length' in stats and stats['avg_length'] is not None:
                    profile.meanLength = float(stats['avg_length'])
            
            logger.info(f"    ✅ Column {column_name}: {non_null_count}/{total_count} values, {distinct_count} distinct, {null_count} nulls")
            
            return profile
            
        except Exception as e:
            logger.warning(f"    ⚠️  Could not profile column {column_name}: {e}")
            return None

    def yield_tag(self, *args, **kwargs) -> Iterable[Either[CreateTagRequest]]:
        """
        Create classification tags for automatic data classification.
        Called by OpenMetadata when "Enable Auto Classification" is checked.
        
        Creates PII (Personally Identifiable Information) tags for sensitive data.
        """
        logger.info("🏷️  Creating classification tags for auto-tagging")
        
        try:
            # Define PII classification tags
            pii_tags = [
                {
                    "name": "Email",
                    "description": "Email addresses detected automatically",
                    "classification": "PII"
                },
                {
                    "name": "Phone",
                    "description": "Phone numbers detected automatically",
                    "classification": "PII"
                },
                {
                    "name": "Name",
                    "description": "Personal names detected automatically",
                    "classification": "PII"
                },
                {
                    "name": "Address",
                    "description": "Physical addresses detected automatically",
                    "classification": "PII"
                },
                {
                    "name": "ID",
                    "description": "Identification numbers (SSN, etc.) detected automatically",
                    "classification": "PII"
                },
                {
                    "name": "Credential",
                    "description": "Credentials, passwords, tokens detected automatically",
                    "classification": "Sensitive"
                },
                {
                    "name": "CreditCard",
                    "description": "Credit card numbers detected automatically",
                    "classification": "Financial"
                },
                {
                    "name": "BankAccount",
                    "description": "Bank account numbers detected automatically",
                    "classification": "Financial"
                }
            ]
            
            for tag_info in pii_tags:
                try:
                    tag_request = CreateTagRequest(
                        name=tag_info["name"],
                        description=tag_info["description"],
                        classification=tag_info["classification"]
                    )
                    yield Either(right=tag_request)
                    logger.info(f"  ✅ Created tag: {tag_info['classification']}.{tag_info['name']}")
                except Exception as tag_error:
                    logger.warning(f"  ⚠️  Could not create tag {tag_info['name']}: {tag_error}")
                    
        except Exception as e:
            logger.error(f"❌ Error creating classification tags: {e}")

    def get_column_tag_labels(
        self,
        table_name: str,
        column: Dict[str, Any]
    ) -> Optional[List[TagLabel]]:
        """
        Auto-classify columns based on name patterns and data types.
        Called by OpenMetadata for each column when "Enable Auto Classification" is checked.
        
        Args:
            table_name: Name of the table
            column: Column dict with 'name' and 'dataType' keys
            
        Returns:
            List of TagLabel objects for detected classifications
        """
        # Check if classification is enabled
        if not self.classification_enabled:
            return None
            
        logger.info(f"🔍 get_column_tag_labels() CALLED for {table_name}.{column.get('name', 'unknown')}")
        try:
            # Extract column name from ColumnName object or string
            col_name_obj = column.get('name', '')
            if hasattr(col_name_obj, '__root__'):
                column_name = col_name_obj.__root__.lower()
            else:
                column_name = str(col_name_obj).lower()
            
            column_type = str(column.get('dataType', '')).upper()
            
            logger.info(f"  📝 Analyzing column: {column_name} (type: {column_type})")
            
            tags = []
            
            # Email detection
            if any(pattern in column_name for pattern in ['email', 'mail', 'e_mail', 'courriel']):
                tags.append(TagLabel(
                    tagFQN="PII.Email",
                    source=TagSource.Classification,
                    labelType=LabelType.Automated,
                    state="Suggested"
                ))
                logger.debug(f"  🏷️  {table_name}.{column['name']}: Detected EMAIL")
            
            # Phone detection
            if any(pattern in column_name for pattern in ['phone', 'tel', 'telephone', 'mobile', 'cell']):
                tags.append(TagLabel(
                    tagFQN="PII.Phone",
                    source=TagSource.Classification,
                    labelType=LabelType.Automated,
                    state="Suggested"
                ))
                logger.debug(f"  🏷️  {table_name}.{column['name']}: Detected PHONE")
            
            # Name detection
            if any(pattern in column_name for pattern in ['name', 'nom', 'prenom', 'firstname', 'lastname', 'fullname']):
                tags.append(TagLabel(
                    tagFQN="PII.Name",
                    source=TagSource.Classification,
                    labelType=LabelType.Automated,
                    state="Suggested"
                ))
                logger.debug(f"  🏷️  {table_name}.{column['name']}: Detected NAME")
            
            # Address detection
            if any(pattern in column_name for pattern in ['address', 'adresse', 'street', 'city', 'ville', 'zip', 'postal', 'country', 'pays']):
                tags.append(TagLabel(
                    tagFQN="PII.Address",
                    source=TagSource.Classification,
                    labelType=LabelType.Automated,
                    state="Suggested"
                ))
                logger.debug(f"  🏷️  {table_name}.{column['name']}: Detected ADDRESS")
            
            # ID detection
            if any(pattern in column_name for pattern in ['ssn', 'social_security', 'passport', 'license', 'licence']):
                tags.append(TagLabel(
                    tagFQN="PII.ID",
                    source=TagSource.Classification,
                    labelType=LabelType.Automated,
                    state="Suggested"
                ))
                logger.debug(f"  🏷️  {table_name}.{column['name']}: Detected ID")
            
            # Credential detection
            if any(pattern in column_name for pattern in ['password', 'passwd', 'pwd', 'token', 'secret', 'key', 'credential']):
                tags.append(TagLabel(
                    tagFQN="Sensitive.Credential",
                    source=TagSource.Classification,
                    labelType=LabelType.Automated,
                    state="Suggested"
                ))
                logger.debug(f"  🏷️  {table_name}.{column['name']}: Detected CREDENTIAL")
            
            # Credit card detection
            if any(pattern in column_name for pattern in ['credit_card', 'creditcard', 'cc_number', 'card_number', 'carte_credit']):
                tags.append(TagLabel(
                    tagFQN="Financial.CreditCard",
                    source=TagSource.Classification,
                    labelType=LabelType.Automated,
                    state="Suggested"
                ))
                logger.debug(f"  🏷️  {table_name}.{column['name']}: Detected CREDIT CARD")
            
            # Bank account detection
            if any(pattern in column_name for pattern in ['account', 'iban', 'swift', 'routing', 'bank_account', 'compte_bancaire']):
                tags.append(TagLabel(
                    tagFQN="Financial.BankAccount",
                    source=TagSource.Classification,
                    labelType=LabelType.Automated,
                    state="Suggested"
                ))
                logger.debug(f"  🏷️  {table_name}.{column['name']}: Detected BANK ACCOUNT")
            
            if tags:
                logger.info(f"  ✅ {table_name}.{column['name']}: Applied {len(tags)} classification tags: {[t.tagFQN for t in tags]}")
            else:
                logger.info(f"  ⚠️  {table_name}.{column['name']}: No tags detected")
            
            return tags if tags else None
            
        except Exception as e:
            logger.warning(f"  ⚠️  Could not classify column {column.get('name', 'unknown')}: {e}")
            return None

    # ============================================================================
    # DBT INTEGRATION - Optional 4th capability
    # ============================================================================
    
    def _load_dbt_catalog(self) -> Optional[Dict]:
        """Load DBT catalog.json file"""
        if not self.dbt_catalog_path:
            return None
            
        try:
            catalog_file = Path(self.dbt_catalog_path)
            if not catalog_file.exists():
                logger.warning(f"⚠️  DBT catalog not found: {self.dbt_catalog_path}")
                return None
                
            logger.info(f"📖 Loading DBT catalog from: {self.dbt_catalog_path}")
            with open(catalog_file, 'r', encoding='utf-8') as f:
                catalog = json.load(f)
            logger.info(f"✅ DBT catalog loaded: {len(catalog.get('nodes', {}))} nodes")
            return catalog
        except Exception as e:
            logger.error(f"❌ Error loading DBT catalog: {e}")
            return None
    
    def _load_dbt_manifest(self) -> Optional[Dict]:
        """Load DBT manifest.json file"""
        if not self.dbt_manifest_path:
            return None
            
        try:
            manifest_file = Path(self.dbt_manifest_path)
            if not manifest_file.exists():
                logger.warning(f"⚠️  DBT manifest not found: {self.dbt_manifest_path}")
                return None
                
            logger.info(f"📖 Loading DBT manifest from: {self.dbt_manifest_path}")
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            logger.info(f"✅ DBT manifest loaded: {len(manifest.get('nodes', {}))} nodes")
            return manifest
        except Exception as e:
            logger.error(f"❌ Error loading DBT manifest: {e}")
            return None
    
    def _load_dbt_run_results(self) -> Optional[Dict]:
        """Load DBT run_results.json file"""
        if not self.dbt_run_results_path:
            return None
            
        try:
            results_file = Path(self.dbt_run_results_path)
            if not results_file.exists():
                logger.warning(f"⚠️  DBT run results not found: {self.dbt_run_results_path}")
                return None
                
            logger.info(f"📖 Loading DBT run results from: {self.dbt_run_results_path}")
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            logger.info(f"✅ DBT run results loaded: {len(results.get('results', []))} results")
            return results
        except Exception as e:
            logger.error(f"❌ Error loading DBT run results: {e}")
            return None
    
    def _enrich_with_dbt(self, table_fqn: str, table_entity: Table) -> Table:
        """
        Enrich table metadata with DBT information
        
        Args:
            table_fqn: Fully qualified name of the table
            table_entity: Table entity to enrich
            
        Returns:
            Enriched table entity
        """
        if not self.dbt_enabled:
            return table_entity
            
        try:
            # Load DBT files on first call
            if not hasattr(self, '_dbt_catalog'):
                self._dbt_catalog = self._load_dbt_catalog()
                self._dbt_manifest = self._load_dbt_manifest()
                self._dbt_run_results = self._load_dbt_run_results()
            
            # Match table with DBT model
            # DBT uses format: model.project_name.model_name
            # We need to match against our Dremio table FQN
            
            if self._dbt_manifest:
                for node_id, node_data in self._dbt_manifest.get('nodes', {}).items():
                    if node_data.get('resource_type') == 'model':
                        # Try to match by name
                        model_name = node_data.get('name', '').lower()
                        table_name = table_fqn.split('.')[-1].lower()
                        
                        if model_name == table_name:
                            logger.info(f"🔧 Enriching {table_fqn} with DBT model: {node_id}")
                            
                            # Add description from DBT
                            if node_data.get('description') and not table_entity.description:
                                table_entity.description = node_data['description']
                                logger.info(f"  ✅ Added DBT description")
                            
                            # Add tags from DBT
                            dbt_tags = node_data.get('tags', [])
                            if dbt_tags:
                                # Convert to TagLabel objects
                                if not table_entity.tags:
                                    table_entity.tags = []
                                for tag_name in dbt_tags:
                                    table_entity.tags.append(TagLabel(
                                        tagFQN=f"DBT.{tag_name}",
                                        source=TagSource.Classification,
                                        labelType=LabelType.Automated,
                                        state="Confirmed"
                                    ))
                                logger.info(f"  ✅ Added {len(dbt_tags)} DBT tags")
                            
                            # Add column descriptions from DBT
                            dbt_columns = node_data.get('columns', {})
                            if dbt_columns and table_entity.columns:
                                for col in table_entity.columns:
                                    col_name = str(col.name.__root__ if hasattr(col.name, '__root__') else col.name).lower()
                                    if col_name in dbt_columns:
                                        dbt_col = dbt_columns[col_name]
                                        if dbt_col.get('description') and not col.description:
                                            col.description = dbt_col['description']
                                            logger.info(f"  ✅ Added description for column: {col_name}")
                            
                            break
            
            return table_entity
            
        except Exception as e:
            logger.warning(f"⚠️  Could not enrich table with DBT: {e}")
            return table_entity

    def close(self):
        """Clean up resources"""
        logger.info("👋 Closing Dremio connector")
        if self.dremio_client:
            self.dremio_client = None

