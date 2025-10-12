"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'dremioHost': 'localhost',
        'dremioPort': 9047,
        'dremioUsername': 'admin',
        'dremioPassword': 'admin123',
        'openMetadataServerConfig': {
            'hostPort': 'http://localhost:8585/api',
            'securityConfig': {
                'jwtToken': 'test_token'
            }
        },
        'serviceName': 'test-service',
        'include_sources': True,
        'include_vds': True
    }


@pytest.fixture
def mock_dremio_client():
    """Mock DremioClient for testing"""
    client = Mock()
    client.authenticate.return_value = True
    client.get_spaces.return_value = [
        {'name': 'TestSpace', 'id': 'space-1'},
        {'name': 'Analytics', 'id': 'space-2'}
    ]
    client.get_datasets.return_value = [
        {
            'name': 'customers',
            'path': ['TestSpace', 'customers'],
            'type': 'PHYSICAL_DATASET'
        }
    ]
    return client


@pytest.fixture
def mock_openmetadata_client():
    """Mock OpenMetadataClient for testing"""
    client = Mock()
    client.create_database.return_value = {'id': 'db-1'}
    client.create_schema.return_value = {'id': 'schema-1'}
    client.create_table.return_value = {'id': 'table-1'}
    return client


@pytest.fixture
def mock_openmetadata_config():
    """Configuration OpenMetadata standard pour tests"""
    return {
        'api_url': 'http://localhost:8585/api',
        'token': 'test_jwt_token',
        'service_name': 'test_dremio_service'
    }


@pytest.fixture
def sample_dbt_manifest():
    """Manifest dbt sample pour tests"""
    return {
        "metadata": {
            "dbt_version": "1.10.8",
            "project_name": "test_analytics"
        },
        "nodes": {
            "model.test_analytics.stg_customers": {
                "name": "stg_customers",
                "resource_type": "model",
                "database": "ANALYTICS",
                "schema": "staging",
                "config": {
                    "database": "ANALYTICS",
                    "schema": "staging",
                    "materialized": "view"
                },
                "columns": {
                    "customer_id": {
                        "name": "customer_id",
                        "data_type": "INTEGER",
                        "description": "Customer ID"
                    }
                },
                "depends_on": {"nodes": ["source.test_analytics.raw_customers"]},
                "description": "Staging customer data",
                "materialized": "view"
            }
        },
        "sources": {
            "source.test_analytics.raw_customers": {
                "name": "raw_customers",
                "database": "RAW_DATA",
                "schema": "raw",
                "identifier": "customers"
            }
        },
        "tests": {
            "test.test_analytics.unique_stg_customers_customer_id": {
                "name": "unique_stg_customers_customer_id",
                "test_metadata": {"name": "unique"},
                "attached_node": "model.test_analytics.stg_customers"
            }
        }
    }
