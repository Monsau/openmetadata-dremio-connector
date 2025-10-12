"""
Tests unitaires pour LineageChecker

Tests pour le module lineage_checker.py de la Phase 2
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from src.dremio_connector.dbt.lineage_checker import LineageChecker


class TestLineageChecker:
    """Tests pour la classe LineageChecker"""
    
    @pytest.fixture
    def mock_openmetadata_config(self):
        """Configuration OpenMetadata mock"""
        return {
            'api_url': 'http://localhost:8585/api',
            'token': 'test_token',
            'service_name': 'test_service'
        }

    @pytest.fixture
    def lineage_checker(self, mock_openmetadata_config):
        """Instance LineageChecker pour tests"""
        with patch('src.dremio_connector.dbt.lineage_checker.requests'):
            return LineageChecker(mock_openmetadata_config)

    @pytest.fixture
    def mock_lineage_response(self):
        """Réponse API lineage mock"""
        return {
            'upstreamEdges': [
                {
                    'fromEntity': {
                        'fullyQualifiedName': 'test_service.RAW.raw_data.customers',
                        'type': 'table'
                    }
                }
            ],
            'downstreamEdges': [
                {
                    'toEntity': {
                        'fullyQualifiedName': 'test_service.MARTS.marts.dim_customers', 
                        'type': 'table'
                    }
                },
                {
                    'toEntity': {
                        'fullyQualifiedName': 'test_service.MARTS.marts.fct_orders',
                        'type': 'table'
                    }
                }
            ]
        }

    @pytest.fixture
    def mock_tables_response(self):
        """Réponse API list tables mock"""
        return {
            'data': [
                {
                    'fullyQualifiedName': 'test_service.STAGING.staging.stg_customers',
                    'name': 'stg_customers',
                    'databaseSchema': {
                        'name': 'staging',
                        'database': {
                            'name': 'STAGING'
                        }
                    }
                },
                {
                    'fullyQualifiedName': 'test_service.MARTS.marts.dim_customers',
                    'name': 'dim_customers', 
                    'databaseSchema': {
                        'name': 'marts',
                        'database': {
                            'name': 'MARTS'
                        }
                    }
                }
            ]
        }

    def test_init_success(self, mock_openmetadata_config):
        """Test initialisation LineageChecker"""
        with patch('src.dremio_connector.dbt.lineage_checker.requests'):
            checker = LineageChecker(mock_openmetadata_config)
            
            assert checker.api_url == 'http://localhost:8585/api'
            assert checker.service_name == 'test_service'
            assert 'Authorization' in checker.headers

    @patch('src.dremio_connector.dbt.lineage_checker.requests.get')
    def test_get_lineage_from_api_success(self, mock_get, lineage_checker, mock_lineage_response):
        """Test récupération lineage API avec succès"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_lineage_response
        
        table_fqn = 'test_service.STAGING.staging.stg_customers'
        lineage = lineage_checker._get_lineage_from_api(table_fqn)
        
        assert 'upstreamEdges' in lineage
        assert 'downstreamEdges' in lineage
        assert len(lineage['upstreamEdges']) == 1
        assert len(lineage['downstreamEdges']) == 2

    @patch('src.dremio_connector.dbt.lineage_checker.requests.get')
    def test_get_lineage_from_api_not_found(self, mock_get, lineage_checker):
        """Test récupération lineage table non trouvée"""
        mock_get.return_value.status_code = 404
        
        table_fqn = 'test_service.UNKNOWN.schema.table'
        lineage = lineage_checker._get_lineage_from_api(table_fqn)
        
        assert lineage == {}

    @patch('src.dremio_connector.dbt.lineage_checker.requests.get')
    def test_get_lineage_from_api_server_error(self, mock_get, lineage_checker):
        """Test récupération lineage erreur serveur"""
        mock_get.return_value.status_code = 500
        mock_get.return_value.text = 'Internal Server Error'
        
        table_fqn = 'test_service.DB.schema.table'
        
        with pytest.raises(Exception) as exc_info:
            lineage_checker._get_lineage_from_api(table_fqn)
        
        assert 'Failed to get lineage' in str(exc_info.value)

    @patch.object(LineageChecker, '_get_lineage_from_api')
    def test_check_table_lineage_complete(self, mock_get_lineage, lineage_checker, mock_lineage_response):
        """Test vérification lineage table complète"""
        mock_get_lineage.return_value = mock_lineage_response
        
        table_fqn = 'test_service.STAGING.staging.stg_customers'
        result = lineage_checker.check_table_lineage(table_fqn)
        
        assert result['table'] == 'stg_customers'
        assert len(result['upstream']) == 1
        assert len(result['downstream']) == 2
        assert result['complete'] is True
        assert len(result['issues']) == 0
        assert 'test_service.RAW.raw_data.customers' in result['upstream']
        assert 'test_service.MARTS.marts.dim_customers' in result['downstream']

    @patch.object(LineageChecker, '_get_lineage_from_api')
    def test_check_table_lineage_no_upstream(self, mock_get_lineage, lineage_checker):
        """Test vérification lineage sans upstream"""
        mock_get_lineage.return_value = {
            'upstreamEdges': [],
            'downstreamEdges': []
        }
        
        table_fqn = 'test_service.DB.schema.isolated_table'
        result = lineage_checker.check_table_lineage(table_fqn)
        
        assert result['table'] == 'isolated_table'
        assert len(result['upstream']) == 0
        assert len(result['downstream']) == 0
        assert result['complete'] is False  # Pas d'upstream = problème
        assert len(result['issues']) > 0
        assert any('No upstream lineage' in issue for issue in result['issues'])

    @patch.object(LineageChecker, '_get_lineage_from_api')
    def test_check_table_lineage_api_error(self, mock_get_lineage, lineage_checker):
        """Test vérification lineage erreur API"""
        mock_get_lineage.side_effect = Exception('API Error')
        
        table_fqn = 'test_service.DB.schema.table'
        result = lineage_checker.check_table_lineage(table_fqn)
        
        assert result['table'] == 'table'
        assert len(result['upstream']) == 0
        assert len(result['downstream']) == 0
        assert result['complete'] is False
        assert len(result['issues']) > 0
        assert any('API Error' in issue for issue in result['issues'])

    @patch('src.dremio_connector.dbt.lineage_checker.requests.get')
    def test_list_tables_success(self, mock_get, lineage_checker, mock_tables_response):
        """Test liste tables avec succès"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_tables_response
        
        tables = lineage_checker._list_tables()
        
        assert len(tables) == 2
        assert tables[0]['fullyQualifiedName'] == 'test_service.STAGING.staging.stg_customers'
        assert tables[1]['fullyQualifiedName'] == 'test_service.MARTS.marts.dim_customers'

    @patch('src.dremio_connector.dbt.lineage_checker.requests.get')
    def test_list_tables_filtered_by_database(self, mock_get, lineage_checker, mock_tables_response):
        """Test liste tables filtrée par database"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_tables_response
        
        tables = lineage_checker._list_tables(database='STAGING')
        
        # Doit filtrer par database dans URL
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        assert 'database=STAGING' in call_args

    @patch('src.dremio_connector.dbt.lineage_checker.requests.get')
    def test_list_tables_filtered_by_schema(self, mock_get, lineage_checker, mock_tables_response):
        """Test liste tables filtrée par schema"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_tables_response
        
        tables = lineage_checker._list_tables(schema='staging')
        
        # Doit filtrer par schema dans URL
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        assert 'databaseSchema=staging' in call_args

    @patch.object(LineageChecker, '_list_tables')
    @patch.object(LineageChecker, 'check_table_lineage')
    def test_check_all_lineage_success(self, mock_check_table, mock_list_tables, lineage_checker):
        """Test vérification lineage complet"""
        # Mock liste tables
        mock_list_tables.return_value = [
            {'fullyQualifiedName': 'service.DB.schema.table1'},
            {'fullyQualifiedName': 'service.DB.schema.table2'},
            {'fullyQualifiedName': 'service.DB.schema.table3'}
        ]
        
        # Mock résultats vérification
        mock_check_table.side_effect = [
            {
                'table': 'table1',
                'upstream': ['source1'],
                'downstream': ['table2'], 
                'complete': True,
                'issues': []
            },
            {
                'table': 'table2',
                'upstream': ['table1'],
                'downstream': ['table3'],
                'complete': True, 
                'issues': []
            },
            {
                'table': 'table3',
                'upstream': ['table2'],
                'downstream': [],
                'complete': False,  # Pas de downstream = incomplet pour certains cas
                'issues': ['No downstream lineage']
            }
        ]
        
        result = lineage_checker.check_all_lineage()
        
        assert result['total_tables'] == 3
        assert result['tables_with_lineage'] == 3  # Toutes ont upstream ou downstream
        assert result['tables_without_lineage'] == 0
        assert result['completion_rate'] == 1.0
        assert len(result['details']) == 3

    @patch.object(LineageChecker, '_list_tables')  
    def test_check_all_lineage_no_tables(self, mock_list_tables, lineage_checker):
        """Test vérification lineage sans tables"""
        mock_list_tables.return_value = []
        
        result = lineage_checker.check_all_lineage()
        
        assert result['total_tables'] == 0
        assert result['tables_with_lineage'] == 0
        assert result['tables_without_lineage'] == 0
        assert result['completion_rate'] == 0
        assert len(result['details']) == 0

    @patch.object(LineageChecker, 'check_table_lineage')
    def test_visualize_lineage_ascii_format(self, mock_check_table, lineage_checker):
        """Test visualisation lineage format ASCII"""
        mock_check_table.return_value = {
            'table': 'stg_customers',
            'upstream': ['source.customers'],
            'downstream': ['dim_customers', 'fct_orders'],
            'complete': True,
            'issues': []
        }
        
        table_fqn = 'service.DB.schema.stg_customers'
        result = lineage_checker.visualize_lineage(table_fqn, output_format='ascii')
        
        assert 'stg_customers' in result
        assert '├── Upstream:' in result
        assert 'source.customers' in result
        assert '└── Downstream:' in result
        assert 'dim_customers' in result
        assert 'fct_orders' in result

    @patch.object(LineageChecker, 'check_table_lineage')
    def test_visualize_lineage_json_format(self, mock_check_table, lineage_checker):
        """Test visualisation lineage format JSON"""
        lineage_data = {
            'table': 'stg_customers',
            'upstream': ['source.customers'],
            'downstream': ['dim_customers'],
            'complete': True,
            'issues': []
        }
        mock_check_table.return_value = lineage_data
        
        table_fqn = 'service.DB.schema.stg_customers'
        result = lineage_checker.visualize_lineage(table_fqn, output_format='json')
        
        # Résultat doit être JSON valide
        parsed = json.loads(result)
        assert parsed == lineage_data

    @patch.object(LineageChecker, 'check_all_lineage')
    @patch('builtins.open', create=True)
    def test_generate_lineage_report_success(self, mock_open, mock_check_all, lineage_checker):
        """Test génération rapport lineage"""
        # Mock résultats
        mock_check_all.return_value = {
            'total_tables': 5,
            'tables_with_lineage': 4,
            'tables_without_lineage': 1,
            'completion_rate': 0.8,
            'details': [
                {
                    'table': 'table1',
                    'upstream': ['source1'], 
                    'downstream': ['table2'],
                    'complete': True,
                    'issues': []
                },
                {
                    'table': 'table2',
                    'upstream': [],
                    'downstream': [],
                    'complete': False,
                    'issues': ['No lineage found']
                }
            ]
        }
        
        # Mock file write
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        lineage_checker.generate_lineage_report(
            database='TEST_DB',
            output_file='report.md'
        )
        
        # Vérifier ouverture fichier
        mock_open.assert_called_once_with('report.md', 'w', encoding='utf-8')
        
        # Vérifier contenu écrit
        written_content = ''.join(call[0][0] for call in mock_file.write.call_args_list)
        assert '# Rapport Lineage' in written_content
        assert 'Total tables: 5' in written_content
        assert 'Taux de completion: 80.0%' in written_content
        assert 'table1' in written_content
        assert 'table2' in written_content

    def test_visualize_lineage_invalid_format(self, lineage_checker):
        """Test visualisation avec format invalide"""
        with patch.object(lineage_checker, 'check_table_lineage'):
            with pytest.raises(ValueError) as exc_info:
                lineage_checker.visualize_lineage(
                    'service.DB.schema.table',
                    output_format='invalid'
                )
            
            assert 'Unsupported format' in str(exc_info.value)


class TestLineageCheckerEdgeCases:
    """Tests pour cas limites LineageChecker"""
    
    @pytest.fixture
    def mock_openmetadata_config(self):
        return {
            'api_url': 'http://localhost:8585/api',
            'token': 'test_token',
            'service_name': 'test_service'
        }

    @patch('src.dremio_connector.dbt.lineage_checker.requests.get')
    def test_get_lineage_empty_response(self, mock_get, mock_openmetadata_config):
        """Test lineage réponse vide"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}
        
        with patch('src.dremio_connector.dbt.lineage_checker.requests'):
            checker = LineageChecker(mock_openmetadata_config)
            lineage = checker._get_lineage_from_api('service.DB.schema.table')
            
            assert lineage == {}

    @patch('src.dremio_connector.dbt.lineage_checker.requests.get')
    def test_list_tables_empty_response(self, mock_get, mock_openmetadata_config):
        """Test liste tables réponse vide"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': []}
        
        with patch('src.dremio_connector.dbt.lineage_checker.requests'):
            checker = LineageChecker(mock_openmetadata_config)
            tables = checker._list_tables()
            
            assert tables == []

    @patch('src.dremio_connector.dbt.lineage_checker.requests.get') 
    def test_check_all_lineage_api_errors(self, mock_get, mock_openmetadata_config):
        """Test vérification complète avec erreurs API"""
        # Premier appel (list_tables) réussit
        # Deuxième appel (lineage) échoue
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: {'data': [{'fullyQualifiedName': 'service.DB.schema.table'}]}),
            Mock(status_code=500, text='Server Error')
        ]
        
        with patch('src.dremio_connector.dbt.lineage_checker.requests'):
            checker = LineageChecker(mock_openmetadata_config)
            result = checker.check_all_lineage()
            
            assert result['total_tables'] == 1
            assert result['tables_with_lineage'] == 0  # Erreur dans check_table_lineage
            assert result['completion_rate'] == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])