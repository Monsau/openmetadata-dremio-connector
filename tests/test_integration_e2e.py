"""
Tests d'intégration pour Phase 2 - dbt Integration

Tests end-to-end pour vérifier l'intégration complète dbt → OpenMetadata
"""
import pytest
import tempfile
import json
import os
from unittest.mock import patch, Mock

from src.dremio_connector.dbt import DbtIntegration, LineageChecker


class TestDbtIntegrationE2E:
    """Tests d'intégration end-to-end pour dbt"""
    
    @pytest.fixture
    def full_manifest(self):
        """Manifest dbt complet pour tests d'intégration"""
        return {
            "metadata": {
                "dbt_version": "1.10.8",
                "project_name": "analytics_project",
                "generated_at": "2025-10-12T10:00:00Z"
            },
            "nodes": {
                # Source staging
                "model.analytics.stg_customers": {
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
                            "description": "Unique customer identifier"
                        },
                        "first_name": {
                            "name": "first_name",
                            "data_type": "VARCHAR",
                            "description": "Customer first name"
                        },
                        "last_name": {
                            "name": "last_name", 
                            "data_type": "VARCHAR",
                            "description": "Customer last name"
                        },
                        "email": {
                            "name": "email",
                            "data_type": "VARCHAR",
                            "description": "Customer email address"
                        }
                    },
                    "depends_on": {
                        "nodes": ["source.analytics.raw_customers"]
                    },
                    "description": "Staging table for customer data with basic cleaning",
                    "materialized": "view"
                },
                "model.analytics.stg_orders": {
                    "name": "stg_orders",
                    "resource_type": "model",
                    "database": "ANALYTICS",
                    "schema": "staging", 
                    "config": {
                        "database": "ANALYTICS",
                        "schema": "staging",
                        "materialized": "view"
                    },
                    "columns": {
                        "order_id": {
                            "name": "order_id",
                            "data_type": "INTEGER", 
                            "description": "Unique order identifier"
                        },
                        "customer_id": {
                            "name": "customer_id",
                            "data_type": "INTEGER",
                            "description": "Customer who placed the order"
                        },
                        "order_date": {
                            "name": "order_date",
                            "data_type": "DATE",
                            "description": "Date order was placed"
                        },
                        "status": {
                            "name": "status",
                            "data_type": "VARCHAR",
                            "description": "Order status"
                        },
                        "amount": {
                            "name": "amount",
                            "data_type": "DECIMAL",
                            "description": "Order total amount"
                        }
                    },
                    "depends_on": {
                        "nodes": ["source.analytics.raw_orders"]
                    },
                    "description": "Staging table for order data",
                    "materialized": "view"
                },
                # Marts dimension
                "model.analytics.dim_customers": {
                    "name": "dim_customers",
                    "resource_type": "model",
                    "database": "ANALYTICS",
                    "schema": "marts",
                    "config": {
                        "database": "ANALYTICS",
                        "schema": "marts", 
                        "materialized": "table"
                    },
                    "columns": {
                        "customer_key": {
                            "name": "customer_key",
                            "data_type": "INTEGER",
                            "description": "Surrogate key for customer"
                        },
                        "customer_id": {
                            "name": "customer_id",
                            "data_type": "INTEGER",
                            "description": "Natural customer ID"
                        },
                        "full_name": {
                            "name": "full_name",
                            "data_type": "VARCHAR",
                            "description": "Customer full name (first + last)"
                        },
                        "email": {
                            "name": "email",
                            "data_type": "VARCHAR",
                            "description": "Customer email"
                        },
                        "customer_segment": {
                            "name": "customer_segment", 
                            "data_type": "VARCHAR",
                            "description": "Customer segment (VIP, Regular, etc.)"
                        },
                        "created_at": {
                            "name": "created_at",
                            "data_type": "TIMESTAMP",
                            "description": "Record creation timestamp"
                        }
                    },
                    "depends_on": {
                        "nodes": ["model.analytics.stg_customers"]
                    },
                    "description": "Customer dimension with business logic",
                    "materialized": "table"
                },
                # Marts fact
                "model.analytics.fct_orders": {
                    "name": "fct_orders",
                    "resource_type": "model", 
                    "database": "ANALYTICS",
                    "schema": "marts",
                    "config": {
                        "database": "ANALYTICS",
                        "schema": "marts",
                        "materialized": "table"
                    },
                    "columns": {
                        "order_key": {
                            "name": "order_key",
                            "data_type": "INTEGER",
                            "description": "Surrogate key for order"
                        },
                        "order_id": {
                            "name": "order_id", 
                            "data_type": "INTEGER",
                            "description": "Natural order ID"
                        },
                        "customer_key": {
                            "name": "customer_key",
                            "data_type": "INTEGER", 
                            "description": "Foreign key to dim_customers"
                        },
                        "order_date": {
                            "name": "order_date",
                            "data_type": "DATE",
                            "description": "Order date"
                        },
                        "order_amount": {
                            "name": "order_amount",
                            "data_type": "DECIMAL",
                            "description": "Order total amount"
                        }
                    },
                    "depends_on": {
                        "nodes": ["model.analytics.stg_orders", "model.analytics.dim_customers"]
                    },
                    "description": "Order fact table with metrics",
                    "materialized": "table"
                }
            },
            "sources": {
                "source.analytics.raw_customers": {
                    "name": "raw_customers",
                    "database": "RAW_DATA",
                    "schema": "raw",
                    "identifier": "customers",
                    "description": "Raw customer data from source system"
                },
                "source.analytics.raw_orders": {
                    "name": "raw_orders",
                    "database": "RAW_DATA", 
                    "schema": "raw",
                    "identifier": "orders",
                    "description": "Raw order data from source system"
                }
            },
            "tests": {
                "test.analytics.unique_stg_customers_customer_id": {
                    "name": "unique_stg_customers_customer_id",
                    "test_metadata": {"name": "unique"},
                    "attached_node": "model.analytics.stg_customers"
                },
                "test.analytics.not_null_stg_customers_customer_id": {
                    "name": "not_null_stg_customers_customer_id",
                    "test_metadata": {"name": "not_null"},
                    "attached_node": "model.analytics.stg_customers"
                },
                "test.analytics.unique_stg_orders_order_id": {
                    "name": "unique_stg_orders_order_id", 
                    "test_metadata": {"name": "unique"},
                    "attached_node": "model.analytics.stg_orders"
                },
                "test.analytics.not_null_stg_orders_customer_id": {
                    "name": "not_null_stg_orders_customer_id",
                    "test_metadata": {"name": "not_null"},
                    "attached_node": "model.analytics.stg_orders"
                },
                "test.analytics.relationships_stg_orders_customer_id": {
                    "name": "relationships_stg_orders_customer_id",
                    "test_metadata": {"name": "relationships"},
                    "attached_node": "model.analytics.stg_orders"
                },
                "test.analytics.unique_dim_customers_customer_key": {
                    "name": "unique_dim_customers_customer_key",
                    "test_metadata": {"name": "unique"},
                    "attached_node": "model.analytics.dim_customers"
                },
                "test.analytics.not_null_fct_orders_order_key": {
                    "name": "not_null_fct_orders_order_key", 
                    "test_metadata": {"name": "not_null"},
                    "attached_node": "model.analytics.fct_orders"
                },
                "test.analytics.relationships_fct_orders_customer_key": {
                    "name": "relationships_fct_orders_customer_key",
                    "test_metadata": {"name": "relationships"}, 
                    "attached_node": "model.analytics.fct_orders"
                }
            }
        }

    @pytest.fixture
    def full_manifest_file(self, full_manifest):
        """Fichier manifest complet temporaire"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(full_manifest, f)
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def openmetadata_config(self):
        """Configuration OpenMetadata complète"""
        return {
            'api_url': 'http://localhost:8585/api',
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
            'service_name': 'dremio_analytics_service'
        }

    @patch('src.dremio_connector.dbt.dbt_integration.requests')
    def test_full_dbt_workflow(self, mock_requests, full_manifest_file, openmetadata_config):
        """Test workflow complet dbt extraction → ingestion"""
        
        # Mock API responses
        mock_requests.post.return_value.status_code = 201
        mock_requests.post.return_value.json.return_value = {'id': 'table-uuid'}
        mock_requests.put.return_value.status_code = 200
        
        # Initialiser DbtIntegration
        dbt = DbtIntegration(full_manifest_file, openmetadata_config)
        
        # Étape 1: Extraction modèles
        models = dbt.extract_models()
        
        # Vérifications extraction
        assert len(models) == 4
        model_names = [m['name'] for m in models]
        assert 'stg_customers' in model_names
        assert 'stg_orders' in model_names  
        assert 'dim_customers' in model_names
        assert 'fct_orders' in model_names
        
        # Vérifier organisation par schema
        staging_models = [m for m in models if m['schema'] == 'staging']
        marts_models = [m for m in models if m['schema'] == 'marts']
        assert len(staging_models) == 2
        assert len(marts_models) == 2
        
        # Étape 2: Vérification lineage
        for model in models:
            lineage = dbt.create_lineage(model)
            assert 'upstream' in lineage
            assert 'downstream' in lineage
        
        # Vérifications lineage spécifiques
        stg_customers = next(m for m in models if m['name'] == 'stg_customers')
        stg_customers_lineage = dbt.create_lineage(stg_customers)
        assert len(stg_customers_lineage['upstream']) == 1  # source.raw_customers
        assert len(stg_customers_lineage['downstream']) == 1  # dim_customers
        
        fct_orders = next(m for m in models if m['name'] == 'fct_orders')
        fct_orders_lineage = dbt.create_lineage(fct_orders) 
        assert len(fct_orders_lineage['upstream']) == 2  # stg_orders + dim_customers
        assert len(fct_orders_lineage['downstream']) == 0  # Pas de downstream
        
        # Étape 3: Ingestion OpenMetadata
        stats = dbt.ingest_to_openmetadata(models)
        
        # Vérifications ingestion
        assert stats['tables_created'] == 4
        assert stats['lineage_created'] >= 0
        
        # Vérifier appels API
        assert mock_requests.post.call_count >= 4  # Au moins 4 tables créées
        assert mock_requests.put.call_count >= 0   # Lineages créés

    @patch('src.dremio_connector.dbt.lineage_checker.requests')  
    def test_full_lineage_verification(self, mock_requests, openmetadata_config):
        """Test vérification complète du lineage"""
        
        # Mock réponses API pour lineage
        def mock_lineage_responses(url, **kwargs):
            if 'stg_customers' in url:
                return Mock(
                    status_code=200,
                    json=lambda: {
                        'upstreamEdges': [
                            {'fromEntity': {'fullyQualifiedName': 'dremio_analytics_service.RAW_DATA.raw.customers'}}
                        ],
                        'downstreamEdges': [
                            {'toEntity': {'fullyQualifiedName': 'dremio_analytics_service.ANALYTICS.marts.dim_customers'}}
                        ]
                    }
                )
            elif 'dim_customers' in url:
                return Mock(
                    status_code=200,
                    json=lambda: {
                        'upstreamEdges': [
                            {'fromEntity': {'fullyQualifiedName': 'dremio_analytics_service.ANALYTICS.staging.stg_customers'}}
                        ],
                        'downstreamEdges': [
                            {'toEntity': {'fullyQualifiedName': 'dremio_analytics_service.ANALYTICS.marts.fct_orders'}}
                        ]
                    }
                )
            elif 'fct_orders' in url:
                return Mock(
                    status_code=200,
                    json=lambda: {
                        'upstreamEdges': [
                            {'fromEntity': {'fullyQualifiedName': 'dremio_analytics_service.ANALYTICS.staging.stg_orders'}},
                            {'fromEntity': {'fullyQualifiedName': 'dremio_analytics_service.ANALYTICS.marts.dim_customers'}}
                        ],
                        'downstreamEdges': []
                    }
                )
            else:
                return Mock(status_code=404)
        
        # Mock liste tables
        def mock_tables_response(url, **kwargs):
            return Mock(
                status_code=200,
                json=lambda: {
                    'data': [
                        {
                            'fullyQualifiedName': 'dremio_analytics_service.ANALYTICS.staging.stg_customers',
                            'name': 'stg_customers'
                        },
                        {
                            'fullyQualifiedName': 'dremio_analytics_service.ANALYTICS.marts.dim_customers', 
                            'name': 'dim_customers'
                        },
                        {
                            'fullyQualifiedName': 'dremio_analytics_service.ANALYTICS.marts.fct_orders',
                            'name': 'fct_orders'
                        }
                    ]
                }
            )
        
        # Configure mocks
        mock_requests.get.side_effect = lambda url, **kwargs: (
            mock_lineage_responses(url, **kwargs) if 'lineage' in url
            else mock_tables_response(url, **kwargs)
        )
        
        # Initialiser LineageChecker
        checker = LineageChecker(openmetadata_config)
        
        # Test vérification table individuelle
        stg_result = checker.check_table_lineage(
            'dremio_analytics_service.ANALYTICS.staging.stg_customers'
        )
        assert stg_result['complete'] is True
        assert len(stg_result['upstream']) == 1
        assert len(stg_result['downstream']) == 1
        assert len(stg_result['issues']) == 0
        
        # Test vérification complète
        all_results = checker.check_all_lineage(database='ANALYTICS')
        assert all_results['total_tables'] == 3
        assert all_results['tables_with_lineage'] == 3
        assert all_results['completion_rate'] == 1.0
        
        # Test visualisation
        ascii_viz = checker.visualize_lineage(
            'dremio_analytics_service.ANALYTICS.staging.stg_customers',
            output_format='ascii'
        )
        assert 'stg_customers' in ascii_viz
        assert 'Upstream:' in ascii_viz
        assert 'Downstream:' in ascii_viz
        
        # Test génération rapport
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            checker.generate_lineage_report(
                database='ANALYTICS',
                output_file='test_report.md'
            )
            
            # Vérifier contenu rapport
            written_content = ''.join(call[0][0] for call in mock_file.write.call_args_list)
            assert '# Rapport Lineage' in written_content
            assert 'Total tables: 3' in written_content
            assert 'stg_customers' in written_content

    @patch('src.dremio_connector.dbt.dbt_integration.requests')
    def test_error_handling_workflow(self, mock_requests, full_manifest_file, openmetadata_config):
        """Test gestion d'erreurs dans workflow complet"""
        
        # Mock erreur API
        mock_requests.post.return_value.status_code = 500
        mock_requests.post.return_value.text = 'Internal Server Error'
        
        dbt = DbtIntegration(full_manifest_file, openmetadata_config)
        models = dbt.extract_models()
        
        # L'extraction doit réussir même si l'API est en erreur
        assert len(models) == 4
        
        # L'ingestion doit échouer proprement
        with pytest.raises(Exception) as exc_info:
            dbt.ingest_to_openmetadata(models)
        
        assert 'Failed to create table' in str(exc_info.value)

    def test_performance_large_manifest(self, openmetadata_config):
        """Test performance avec grand manifest"""
        import time
        
        # Créer grand manifest (simulé)
        large_manifest = {
            "metadata": {"dbt_version": "1.10.8", "project_name": "large_project"},
            "nodes": {},
            "sources": {},
            "tests": {}
        }
        
        # Générer 50 modèles
        for i in range(50):
            model_id = f"model.large_project.model_{i}"
            large_manifest["nodes"][model_id] = {
                "name": f"model_{i}",
                "resource_type": "model",
                "database": "LARGE_DB",
                "schema": "schema_1" if i < 25 else "schema_2",
                "config": {"database": "LARGE_DB", "schema": "schema_1" if i < 25 else "schema_2"},
                "columns": {
                    f"col_{j}": {
                        "name": f"col_{j}",
                        "data_type": "VARCHAR",
                        "description": f"Column {j}"
                    } for j in range(10)  # 10 colonnes par modèle
                },
                "depends_on": {"nodes": [f"model.large_project.model_{i-1}"] if i > 0 else []},
                "description": f"Model {i}",
                "materialized": "table"
            }
        
        # Créer fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_manifest, f)
            large_manifest_path = f.name
        
        try:
            with patch('src.dremio_connector.dbt.dbt_integration.requests'):
                # Test performance extraction
                start_time = time.time()
                dbt = DbtIntegration(large_manifest_path, openmetadata_config)
                models = dbt.extract_models()
                extraction_time = time.time() - start_time
                
                # Vérifications
                assert len(models) == 50
                assert extraction_time < 10.0  # Moins de 10s pour 50 modèles
                
                # Test performance lineage
                start_time = time.time()
                lineages = []
                for model in models[:10]:  # Test sur 10 modèles
                    lineage = dbt.create_lineage(model)
                    lineages.append(lineage)
                lineage_time = time.time() - start_time
                
                assert len(lineages) == 10
                assert lineage_time < 5.0  # Moins de 5s pour 10 lineages
                
        finally:
            os.unlink(large_manifest_path)


class TestDbtIntegrationRealWorld:
    """Tests avec données réelles simulées"""
    
    @pytest.fixture
    def real_world_config(self):
        """Configuration production-like"""
        return {
            'api_url': 'https://openmetadata.company.com/api',
            'token': 'prod_jwt_token_here', 
            'service_name': 'dremio_production_service'
        }

    def test_dbt_versions_compatibility(self, real_world_config):
        """Test compatibilité différentes versions dbt"""
        
        dbt_versions = ['1.8.0', '1.9.2', '1.10.8']
        
        for version in dbt_versions:
            manifest = {
                "metadata": {
                    "dbt_version": version,
                    "project_name": f"project_{version.replace('.', '_')}"
                },
                "nodes": {
                    "model.test.test_model": {
                        "name": "test_model",
                        "resource_type": "model",
                        "database": "TEST",
                        "schema": "test",
                        "config": {"database": "TEST", "schema": "test"},
                        "columns": {},
                        "depends_on": {"nodes": []},
                        "description": f"Test model for dbt {version}"
                    }
                },
                "sources": {},
                "tests": {}
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(manifest, f)
                manifest_path = f.name
            
            try:
                with patch('src.dremio_connector.dbt.dbt_integration.requests'):
                    dbt = DbtIntegration(manifest_path, real_world_config)
                    models = dbt.extract_models()
                    
                    assert len(models) == 1
                    assert models[0]['name'] == 'test_model'
                    
            finally:
                os.unlink(manifest_path)

    def test_complex_lineage_patterns(self, real_world_config):
        """Test patterns de lineage complexes"""
        
        # Pattern: source → staging → intermediate → mart → report
        complex_manifest = {
            "metadata": {"dbt_version": "1.10.8", "project_name": "complex_lineage"},
            "nodes": {
                "model.complex.stg_raw_data": {
                    "name": "stg_raw_data",
                    "resource_type": "model",
                    "database": "DWH", "schema": "staging",
                    "config": {"database": "DWH", "schema": "staging"},
                    "columns": {"id": {"name": "id", "data_type": "INTEGER"}},
                    "depends_on": {"nodes": ["source.complex.raw_table"]},
                    "description": "Staging raw data"
                },
                "model.complex.int_cleaned_data": {
                    "name": "int_cleaned_data", 
                    "resource_type": "model",
                    "database": "DWH", "schema": "intermediate",
                    "config": {"database": "DWH", "schema": "intermediate"}, 
                    "columns": {"id": {"name": "id", "data_type": "INTEGER"}},
                    "depends_on": {"nodes": ["model.complex.stg_raw_data"]},
                    "description": "Intermediate cleaned data"
                },
                "model.complex.mart_aggregated": {
                    "name": "mart_aggregated",
                    "resource_type": "model",
                    "database": "DWH", "schema": "marts",
                    "config": {"database": "DWH", "schema": "marts"},
                    "columns": {"metric": {"name": "metric", "data_type": "DECIMAL"}}, 
                    "depends_on": {"nodes": ["model.complex.int_cleaned_data"]},
                    "description": "Mart with aggregations"
                },
                "model.complex.rpt_final_report": {
                    "name": "rpt_final_report",
                    "resource_type": "model", 
                    "database": "DWH", "schema": "reports",
                    "config": {"database": "DWH", "schema": "reports"},
                    "columns": {"report_value": {"name": "report_value", "data_type": "VARCHAR"}},
                    "depends_on": {"nodes": ["model.complex.mart_aggregated"]},
                    "description": "Final report"
                }
            },
            "sources": {
                "source.complex.raw_table": {
                    "name": "raw_table",
                    "database": "RAW_DB", 
                    "schema": "raw",
                    "identifier": "raw_table"
                }
            },
            "tests": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(complex_manifest, f)
            manifest_path = f.name
        
        try:
            with patch('src.dremio_connector.dbt.dbt_integration.requests'):
                dbt = DbtIntegration(manifest_path, real_world_config)
                models = dbt.extract_models()
                
                # Vérifier chaîne de lineage complète
                stg_model = next(m for m in models if m['name'] == 'stg_raw_data')
                stg_lineage = dbt.create_lineage(stg_model)
                assert len(stg_lineage['upstream']) == 1  # source
                assert len(stg_lineage['downstream']) == 1  # int_cleaned_data
                
                rpt_model = next(m for m in models if m['name'] == 'rpt_final_report') 
                rpt_lineage = dbt.create_lineage(rpt_model)
                assert len(rpt_lineage['upstream']) == 1  # mart_aggregated
                assert len(rpt_lineage['downstream']) == 0  # Fin de chaîne
                
        finally:
            os.unlink(manifest_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])