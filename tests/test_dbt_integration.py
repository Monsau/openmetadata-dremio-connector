"""
Tests unitaires pour DbtIntegration

Tests pour le module dbt_integration.py de la Phase 2
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.dremio_connector.dbt.dbt_integration import DbtIntegration


class TestDbtIntegration:
    """Tests pour la classe DbtIntegration"""
    
    @pytest.fixture
    def mock_manifest(self):
        """Manifest dbt simplifié pour tests"""
        return {
            "metadata": {
                "dbt_version": "1.10.8",
                "project_name": "test_project"
            },
            "nodes": {
                "model.test_project.stg_customers": {
                    "name": "stg_customers",
                    "resource_type": "model",
                    "database": "TEST_DB",
                    "schema": "staging", 
                    "config": {
                        "database": "TEST_DB",
                        "schema": "staging",
                        "materialized": "view"
                    },
                    "columns": {
                        "customer_id": {
                            "name": "customer_id",
                            "data_type": "INTEGER",
                            "description": "Customer unique ID"
                        },
                        "first_name": {
                            "name": "first_name", 
                            "data_type": "VARCHAR",
                            "description": "Customer first name"
                        }
                    },
                    "depends_on": {
                        "nodes": ["source.test_project.customers"]
                    },
                    "description": "Staging customer data"
                },
                "model.test_project.dim_customers": {
                    "name": "dim_customers",
                    "resource_type": "model", 
                    "database": "TEST_DB",
                    "schema": "marts",
                    "config": {
                        "database": "TEST_DB",
                        "schema": "marts",
                        "materialized": "table"
                    },
                    "columns": {
                        "customer_id": {
                            "name": "customer_id",
                            "data_type": "INTEGER", 
                            "description": "Customer ID"
                        },
                        "full_name": {
                            "name": "full_name",
                            "data_type": "VARCHAR",
                            "description": "Customer full name"
                        }
                    },
                    "depends_on": {
                        "nodes": ["model.test_project.stg_customers"]
                    },
                    "description": "Customer dimension table"
                }
            },
            "sources": {
                "source.test_project.customers": {
                    "name": "customers",
                    "database": "RAW_DB",
                    "schema": "raw_data",
                    "identifier": "customers"
                }
            },
            "tests": {
                "test.test_project.unique_stg_customers_customer_id": {
                    "name": "unique_stg_customers_customer_id",
                    "test_metadata": {
                        "name": "unique"
                    },
                    "attached_node": "model.test_project.stg_customers"
                },
                "test.test_project.not_null_dim_customers_customer_id": {
                    "name": "not_null_dim_customers_customer_id", 
                    "test_metadata": {
                        "name": "not_null"
                    },
                    "attached_node": "model.test_project.dim_customers"
                }
            }
        }

    @pytest.fixture
    def temp_manifest_file(self, mock_manifest):
        """Crée un fichier manifest temporaire"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mock_manifest, f)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        os.unlink(temp_path)

    @pytest.fixture
    def mock_openmetadata_config(self):
        """Configuration OpenMetadata mock"""
        return {
            'api_url': 'http://localhost:8585/api',
            'token': 'test_token',
            'service_name': 'test_service'
        }

    @pytest.fixture
    def dbt_integration(self, temp_manifest_file, mock_openmetadata_config):
        """Instance DbtIntegration pour tests"""
        with patch('src.dremio_connector.dbt.dbt_integration.requests'):
            return DbtIntegration(
                manifest_path=temp_manifest_file,
                openmetadata_config=mock_openmetadata_config
            )

    def test_init_valid_manifest(self, temp_manifest_file, mock_openmetadata_config):
        """Test initialisation avec manifest valide"""
        with patch('src.dremio_connector.dbt.dbt_integration.requests'):
            dbt = DbtIntegration(
                manifest_path=temp_manifest_file,
                openmetadata_config=mock_openmetadata_config
            )
            
            assert dbt.manifest is not None
            assert str(dbt.manifest_path) == temp_manifest_file
            assert 'nodes' in dbt.manifest
            assert 'sources' in dbt.manifest

    def test_init_invalid_manifest_path(self, mock_openmetadata_config):
        """Test initialisation avec chemin manifest invalide"""
        with pytest.raises(FileNotFoundError):
            DbtIntegration(
                manifest_path='/path/does/not/exist.json',
                openmetadata_config=mock_openmetadata_config
            )

    def test_init_invalid_json(self, mock_openmetadata_config):
        """Test initialisation avec JSON invalide"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('invalid json content')
            invalid_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                DbtIntegration(
                    manifest_path=invalid_path,
                    openmetadata_config=mock_openmetadata_config
                )
        finally:
            os.unlink(invalid_path)

    def test_load_manifest_success(self, dbt_integration):
        """Test chargement manifest avec succès"""
        manifest = dbt_integration._load_manifest()
        
        assert manifest is not None
        assert 'nodes' in manifest
        assert 'metadata' in manifest
        assert manifest['metadata']['project_name'] == 'test_project'

    def test_extract_models_count(self, dbt_integration):
        """Test extraction nombre correct de modèles"""
        models = dbt_integration.extract_models()
        
        assert len(models) == 2
        model_names = [m['name'] for m in models]
        assert 'stg_customers' in model_names
        assert 'dim_customers' in model_names

    def test_extract_models_structure(self, dbt_integration):
        """Test structure des modèles extraits"""
        models = dbt_integration.extract_models()
        
        for model in models:
            # Champs obligatoires
            assert 'name' in model
            assert 'database' in model
            assert 'schema' in model
            assert 'columns' in model
            assert 'depends_on' in model
            assert 'description' in model
            assert 'tests' in model
            assert 'materialization' in model
            
            # Types corrects
            assert isinstance(model['columns'], list)
            assert isinstance(model['depends_on'], list)
            assert isinstance(model['tests'], list)

    def test_extract_models_stg_customers(self, dbt_integration):
        """Test extraction modèle stg_customers spécifique"""
        models = dbt_integration.extract_models()
        stg_customers = next(m for m in models if m['name'] == 'stg_customers')
        
        assert stg_customers['database'] == 'TEST_DB'
        assert stg_customers['schema'] == 'staging'
        assert stg_customers['materialization'] == 'view'
        assert len(stg_customers['columns']) == 2
        assert len(stg_customers['depends_on']) == 1
        assert stg_customers['depends_on'][0] == 'source.test_project.customers'
        assert len(stg_customers['tests']) == 1
        assert stg_customers['tests'][0] == 'unique'

    def test_extract_models_dim_customers(self, dbt_integration):
        """Test extraction modèle dim_customers spécifique"""
        models = dbt_integration.extract_models()
        dim_customers = next(m for m in models if m['name'] == 'dim_customers')
        
        assert dim_customers['database'] == 'TEST_DB'
        assert dim_customers['schema'] == 'marts'
        assert dim_customers['materialization'] == 'table'
        assert len(dim_customers['columns']) == 2
        assert len(dim_customers['depends_on']) == 1
        assert dim_customers['depends_on'][0] == 'model.test_project.stg_customers'
        assert len(dim_customers['tests']) == 1
        assert dim_customers['tests'][0] == 'not_null'

    def test_extract_columns_complete(self, dbt_integration):
        """Test extraction colonnes avec métadonnées complètes"""
        models = dbt_integration.extract_models()
        stg_customers = next(m for m in models if m['name'] == 'stg_customers')
        
        columns = stg_customers['columns']
        customer_id_col = next(c for c in columns if c['name'] == 'customer_id')
        
        assert customer_id_col['name'] == 'customer_id'
        assert customer_id_col['data_type'] == 'INTEGER'
        assert customer_id_col['description'] == 'Customer unique ID'

    def test_extract_columns_none_handling(self, dbt_integration):
        """Test gestion None dans extraction colonnes"""
        # Modifier manifest pour tester None
        dbt_integration.manifest['nodes']['model.test_project.stg_customers']['columns']['test_col'] = {
            'name': 'test_col',
            'data_type': None,
            'description': None
        }
        
        models = dbt_integration.extract_models()
        stg_customers = next(m for m in models if m['name'] == 'stg_customers')
        
        test_col = next((c for c in stg_customers['columns'] if c['name'] == 'test_col'), None)
        assert test_col is not None
        assert test_col['data_type'] == 'VARCHAR'  # Fallback
        assert test_col['description'] == ''  # Fallback

    def test_extract_tests_attached(self, dbt_integration):
        """Test extraction tests attachés aux modèles"""
        node_id = 'model.test_project.stg_customers'
        tests = dbt_integration._extract_tests(node_id)
        
        assert len(tests) == 1
        assert 'unique' in tests

    def test_extract_tests_no_tests(self, dbt_integration):
        """Test extraction tests quand aucun test attaché"""
        node_id = 'model.nonexistent.model'
        tests = dbt_integration._extract_tests(node_id)
        
        assert len(tests) == 0
        assert tests == []

    def test_create_lineage_upstream(self, dbt_integration):
        """Test création lineage upstream"""
        models = dbt_integration.extract_models()
        dim_customers = next(m for m in models if m['name'] == 'dim_customers')
        
        lineage = dbt_integration.create_lineage(dim_customers)
        
        assert 'upstream' in lineage
        assert 'downstream' in lineage
        assert len(lineage['upstream']) == 1
        assert 'model.test_project.stg_customers' in lineage['upstream']

    def test_create_lineage_downstream(self, dbt_integration):
        """Test création lineage downstream"""
        models = dbt_integration.extract_models()
        stg_customers = next(m for m in models if m['name'] == 'stg_customers')
        
        lineage = dbt_integration.create_lineage(stg_customers)
        
        assert 'downstream' in lineage
        assert len(lineage['downstream']) == 1
        assert 'model.test_project.dim_customers' in lineage['downstream']

    def test_node_to_fqn_model(self, dbt_integration):
        """Test conversion node vers FQN pour modèle"""
        node = {
            'name': 'test_model',
            'database': 'TEST_DB', 
            'schema': 'test_schema'
        }
        
        fqn = dbt_integration._node_to_fqn(node)
        expected = 'test_service.TEST_DB.test_schema.test_model'
        
        assert fqn == expected

    def test_source_to_fqn(self, dbt_integration):
        """Test conversion source vers FQN"""
        source = {
            'name': 'test_source',
            'database': 'RAW_DB',
            'schema': 'raw_data'
        }
        
        fqn = dbt_integration._source_to_fqn(source)
        expected = 'test_service.RAW_DB.raw_data.test_source'
        
        assert fqn == expected

    def test_node_to_fqn_none_handling(self, dbt_integration):
        """Test conversion FQN avec gestion None"""
        node = {
            'name': 'test_model',
            'database': None,
            'schema': None
        }
        
        fqn = dbt_integration._node_to_fqn(node)
        expected = 'test_service.DEFAULT.default.test_model'
        
        assert fqn == expected

    @patch('src.dremio_connector.dbt.dbt_integration.requests.post')
    @patch('src.dremio_connector.dbt.dbt_integration.requests.put')
    def test_ingest_to_openmetadata_success(self, mock_put, mock_post, dbt_integration):
        """Test ingestion OpenMetadata avec succès"""
        # Mock réponses API
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {'id': 'table-id'}
        mock_put.return_value.status_code = 200
        
        models = dbt_integration.extract_models()
        stats = dbt_integration.ingest_to_openmetadata(models)
        
        assert 'tables_created' in stats
        assert 'lineage_created' in stats
        assert stats['tables_created'] == 2
        assert stats['lineage_created'] >= 0

    @patch('src.dremio_connector.dbt.dbt_integration.requests.post')
    def test_ingest_to_openmetadata_api_error(self, mock_post, dbt_integration):
        """Test ingestion avec erreur API"""
        # Mock erreur API
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = 'Internal Server Error'
        
        models = dbt_integration.extract_models()
        
        with pytest.raises(Exception):
            dbt_integration.ingest_to_openmetadata(models)

    def test_database_priority_config_over_node(self, temp_manifest_file, mock_openmetadata_config):
        """Test priorité config.database > node.database"""
        # Modifier manifest pour tester priorité
        with open(temp_manifest_file, 'r') as f:
            manifest = json.load(f)
        
        # node.database différent de config.database
        manifest['nodes']['model.test_project.stg_customers']['database'] = '$scratch'
        manifest['nodes']['model.test_project.stg_customers']['config']['database'] = 'REAL_DB'
        
        with open(temp_manifest_file, 'w') as f:
            json.dump(manifest, f)
        
        with patch('src.dremio_connector.dbt.dbt_integration.requests'):
            dbt = DbtIntegration(temp_manifest_file, mock_openmetadata_config)
            models = dbt.extract_models()
            
            stg_customers = next(m for m in models if m['name'] == 'stg_customers')
            assert stg_customers['database'] == 'REAL_DB'  # config prioritaire

    def test_schema_priority_config_over_node(self, temp_manifest_file, mock_openmetadata_config):
        """Test priorité config.schema > node.schema"""
        with open(temp_manifest_file, 'r') as f:
            manifest = json.load(f)
        
        manifest['nodes']['model.test_project.stg_customers']['schema'] = 'old_schema'
        manifest['nodes']['model.test_project.stg_customers']['config']['schema'] = 'new_schema'
        
        with open(temp_manifest_file, 'w') as f:
            json.dump(manifest, f)
        
        with patch('src.dremio_connector.dbt.dbt_integration.requests'):
            dbt = DbtIntegration(temp_manifest_file, mock_openmetadata_config)
            models = dbt.extract_models()
            
            stg_customers = next(m for m in models if m['name'] == 'stg_customers')
            assert stg_customers['schema'] == 'new_schema'


class TestDbtIntegrationEdgeCases:
    """Tests pour cas limites et erreurs"""
    
    @pytest.fixture
    def empty_manifest(self):
        """Manifest vide pour tests edge cases"""
        return {
            "metadata": {"dbt_version": "1.10.8"},
            "nodes": {},
            "sources": {},
            "tests": {}
        }

    @pytest.fixture  
    def empty_manifest_file(self, empty_manifest):
        """Fichier manifest vide"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(empty_manifest, f)
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)

    def test_extract_models_empty_manifest(self, empty_manifest_file, mock_openmetadata_config):
        """Test extraction avec manifest vide"""
        with patch('src.dremio_connector.dbt.dbt_integration.requests'):
            dbt = DbtIntegration(empty_manifest_file, mock_openmetadata_config)
            models = dbt.extract_models()
            
            assert len(models) == 0
            assert models == []

    def test_manifest_missing_metadata(self, mock_openmetadata_config):
        """Test manifest sans métadonnées"""
        manifest = {"nodes": {}, "sources": {}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest, f)
            temp_path = f.name
        
        try:
            with patch('src.dremio_connector.dbt.dbt_integration.requests'):
                dbt = DbtIntegration(temp_path, mock_openmetadata_config)
                # Doit fonctionner même sans metadata
                assert dbt.manifest is not None
        finally:
            os.unlink(temp_path)

    def test_model_without_columns(self, mock_openmetadata_config):
        """Test modèle sans colonnes définies"""
        manifest = {
            "metadata": {"dbt_version": "1.10.8"},
            "nodes": {
                "model.test.no_columns": {
                    "name": "no_columns",
                    "resource_type": "model",
                    "database": "TEST",
                    "schema": "test",
                    "columns": {},  # Pas de colonnes
                    "depends_on": {"nodes": []},
                    "description": ""
                }
            },
            "sources": {},
            "tests": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest, f)
            temp_path = f.name
        
        try:
            with patch('src.dremio_connector.dbt.dbt_integration.requests'):
                dbt = DbtIntegration(temp_path, mock_openmetadata_config)
                models = dbt.extract_models()
                
                assert len(models) == 1
                assert len(models[0]['columns']) == 0
        finally:
            os.unlink(temp_path)

    @pytest.fixture
    def mock_openmetadata_config(self):
        """Configuration OpenMetadata mock"""
        return {
            'api_url': 'http://localhost:8585/api',
            'token': 'test_token',
            'service_name': 'test_service'
        }


if __name__ == '__main__':
    pytest.main([__file__, '-v'])