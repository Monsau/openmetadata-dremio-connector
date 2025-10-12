"""
Agent Profiler pour OpenMetadata.

Cet agent gère le profilage des données et génération de statistiques.
"""

import logging
from typing import Dict, List, Optional, Any

from ..clients.dremio_client import DremioClient
from ..clients.openmetadata_client import OpenMetadataClient
from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ProfilerAgent(BaseAgent):
    """
    Agent spécialisé pour le profilage des données.
    
    Fonctionnalités:
    - Analyse qualité données
    - Statistiques colonnes
    - Détection anomalies
    - Métriques de complétude
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise l'agent profiler.
        
        Args:
            config: Configuration agent
                - dremio: Config Dremio
                - openmetadata: Config OpenMetadata
                - tables: Tables à profiler (optionnel)
                - sample_size: Taille échantillon
        """
        super().__init__(config)
        self.agent_type = "profiler"
        
        # Config spécifique
        dremio_config = config.get('dremio', {})
        if not dremio_config:
            raise ValueError("Configuration dremio requise")
            
        self.tables_to_profile = config.get('tables', [])  # Si vide, toutes les tables
        self.sample_size = config.get('sample_size', 10000)
        
        # Initialise clients
        self.dremio_client = DremioClient(dremio_config)
        self.openmetadata_client = OpenMetadataClient(self.openmetadata_config)
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Valide la configuration de l'agent profiler.
        """
        errors = []
        
        # Vérifier connexions
        try:
            if not self.dremio_client.test_connection():
                errors.append("Connexion Dremio échouée")
        except Exception as e:
            errors.append(f"Erreur Dremio: {str(e)}")
        
        om_errors = self._validate_openmetadata_config()
        errors.extend(om_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'config': self.config
        }
    
    def run(self) -> Dict[str, Any]:
        """
        Exécute le profilage des données.
        
        Returns:
            Statistiques et métriques de profilage
        """
        try:
            self.logger.info("📊 Démarrage ProfilerAgent")
            
            # 1. Validation
            validation = self.validate_config()
            if not validation['valid']:
                raise ValueError(f"Config invalide: {validation['errors']}")
            
            # 2. Découverte tables à profiler
            if not self.tables_to_profile:
                self.logger.info("🔍 Découverte tables automatique...")
                self.tables_to_profile = self._discover_tables()
            
            self.logger.info(f"📋 {len(self.tables_to_profile)} tables à profiler")
            
            # 3. Profilage
            profiling_stats = {
                'tables_profiled': 0,
                'columns_analyzed': 0,
                'quality_issues': 0,
                'errors': []
            }
            
            for table_fqn in self.tables_to_profile:
                try:
                    self.logger.info(f"📊 Profilage: {table_fqn}")
                    
                    # Analyse table
                    profile = self._profile_table(table_fqn)
                    
                    # Envoi vers OpenMetadata
                    self._upload_profile(table_fqn, profile)
                    
                    profiling_stats['tables_profiled'] += 1
                    profiling_stats['columns_analyzed'] += len(profile['columns'])
                    profiling_stats['quality_issues'] += len(profile.get('issues', []))
                    
                except Exception as e:
                    error_msg = f"Erreur profilage {table_fqn}: {str(e)}"
                    self.logger.error(error_msg)
                    profiling_stats['errors'].append(error_msg)
            
            # 4. Résultats
            result = {
                'status': 'success',
                'agent_type': self.agent_type,
                'profiling_statistics': profiling_stats,
                'sample_size': self.sample_size,
                'timestamp': self._get_timestamp()
            }
            
            self.logger.info("✅ ProfilerAgent terminé avec succès")
            return result
            
        except Exception as e:
            error_result = {
                'status': 'failed',
                'agent_type': self.agent_type,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }
            self.logger.error(f"❌ Erreur ProfilerAgent: {str(e)}")
            return error_result
    
    def _discover_tables(self) -> List[str]:
        """Découvre automatiquement les tables à profiler."""
        tables = []
        try:
            # Récupère toutes les tables du service
            service_tables = self.openmetadata_client.get_tables_by_service(
                self.openmetadata_config['service_name']
            )
            tables = [table['fullyQualifiedName'] for table in service_tables]
        except Exception as e:
            self.logger.warning(f"Découverte auto échouée: {str(e)}")
            # Fallback: utiliser API Dremio directement
            spaces = self.dremio_client.get_spaces()
            for space in spaces:
                space_tables = self.dremio_client.get_tables_in_space(space['name'])
                tables.extend([f"{space['name']}.{table['name']}" for table in space_tables])
        
        return tables
    
    def _profile_table(self, table_fqn: str) -> Dict[str, Any]:
        """
        Profile une table spécifique.
        
        Args:
            table_fqn: Nom complet table (database.schema.table)
            
        Returns:
            Profil avec statistiques colonnes
        """
        # Parse FQN
        parts = table_fqn.split('.')
        if len(parts) < 2:
            raise ValueError(f"FQN invalide: {table_fqn}")
        
        space = parts[0]
        table_name = '.'.join(parts[1:])
        
        # Récupère schéma table
        table_info = self.dremio_client.get_table_info(space, table_name)
        
        # Génère statistiques par colonne
        column_profiles = []
        for column in table_info.get('columns', []):
            col_profile = self._profile_column(space, table_name, column)
            column_profiles.append(col_profile)
        
        # Statistiques globales table
        table_stats = self._get_table_statistics(space, table_name)
        
        return {
            'table_fqn': table_fqn,
            'row_count': table_stats.get('row_count', 0),
            'columns': column_profiles,
            'issues': self._detect_quality_issues(column_profiles),
            'sample_size': self.sample_size,
            'profiled_at': self._get_timestamp()
        }
    
    def _profile_column(self, space: str, table: str, column: Dict[str, Any]) -> Dict[str, Any]:
        """Profile une colonne spécifique."""
        col_name = column['name']
        col_type = column.get('type', 'UNKNOWN')
        
        # Requête statistiques selon type
        stats = {}
        
        try:
            if col_type in ['VARCHAR', 'TEXT', 'STRING']:
                stats = self._profile_string_column(space, table, col_name)
            elif col_type in ['INTEGER', 'BIGINT', 'FLOAT', 'DOUBLE', 'DECIMAL']:
                stats = self._profile_numeric_column(space, table, col_name)
            elif col_type in ['DATE', 'TIMESTAMP']:
                stats = self._profile_date_column(space, table, col_name)
            else:
                stats = self._profile_generic_column(space, table, col_name)
                
        except Exception as e:
            self.logger.warning(f"Erreur profilage colonne {col_name}: {str(e)}")
            stats = {'error': str(e)}
        
        return {
            'name': col_name,
            'type': col_type,
            'statistics': stats
        }
    
    def _profile_string_column(self, space: str, table: str, column: str) -> Dict[str, Any]:
        """Profile colonne texte."""
        query = f"""
        SELECT 
            COUNT(*) as total_count,
            COUNT({column}) as non_null_count,
            COUNT(DISTINCT {column}) as distinct_count,
            MIN(LENGTH({column})) as min_length,
            MAX(LENGTH({column})) as max_length,
            AVG(LENGTH({column})) as avg_length
        FROM {space}."{table}"
        LIMIT {self.sample_size}
        """
        
        result = self.dremio_client.execute_query(query)
        return result[0] if result else {}
    
    def _profile_numeric_column(self, space: str, table: str, column: str) -> Dict[str, Any]:
        """Profile colonne numérique."""
        query = f"""
        SELECT 
            COUNT(*) as total_count,
            COUNT({column}) as non_null_count,
            COUNT(DISTINCT {column}) as distinct_count,
            MIN({column}) as min_value,
            MAX({column}) as max_value,
            AVG({column}) as avg_value,
            STDDEV({column}) as stddev_value
        FROM {space}."{table}"
        LIMIT {self.sample_size}
        """
        
        result = self.dremio_client.execute_query(query)
        return result[0] if result else {}
    
    def _profile_date_column(self, space: str, table: str, column: str) -> Dict[str, Any]:
        """Profile colonne date."""
        query = f"""
        SELECT 
            COUNT(*) as total_count,
            COUNT({column}) as non_null_count,
            COUNT(DISTINCT {column}) as distinct_count,
            MIN({column}) as min_date,
            MAX({column}) as max_date
        FROM {space}."{table}"
        LIMIT {self.sample_size}
        """
        
        result = self.dremio_client.execute_query(query)
        return result[0] if result else {}
    
    def _profile_generic_column(self, space: str, table: str, column: str) -> Dict[str, Any]:
        """Profile colonne générique."""
        query = f"""
        SELECT 
            COUNT(*) as total_count,
            COUNT({column}) as non_null_count,
            COUNT(DISTINCT {column}) as distinct_count
        FROM {space}."{table}"
        LIMIT {self.sample_size}
        """
        
        result = self.dremio_client.execute_query(query)
        return result[0] if result else {}
    
    def _get_table_statistics(self, space: str, table: str) -> Dict[str, Any]:
        """Récupère statistiques globales table."""
        query = f'SELECT COUNT(*) as row_count FROM {space}."{table}"'
        result = self.dremio_client.execute_query(query)
        return result[0] if result else {'row_count': 0}
    
    def _detect_quality_issues(self, column_profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Détecte problèmes qualité données."""
        issues = []
        
        for col_profile in column_profiles:
            stats = col_profile.get('statistics', {})
            col_name = col_profile['name']
            
            # Vérifier complétude
            total = stats.get('total_count', 0)
            non_null = stats.get('non_null_count', 0)
            
            if total > 0:
                completeness = (non_null / total) * 100
                if completeness < 95:  # Seuil configurable
                    issues.append({
                        'type': 'completeness',
                        'column': col_name,
                        'severity': 'warning' if completeness >= 80 else 'error',
                        'message': f'Complétude faible: {completeness:.1f}%'
                    })
            
            # Vérifier unicité pour colonnes suspectes d'être des clés
            distinct = stats.get('distinct_count', 0)
            if col_name.lower() in ['id', 'key', 'code'] and distinct < non_null:
                issues.append({
                    'type': 'uniqueness',
                    'column': col_name,
                    'severity': 'warning',
                    'message': f'Doublons détectés dans colonne clé potentielle'
                })
        
        return issues
    
    def _upload_profile(self, table_fqn: str, profile: Dict[str, Any]) -> None:
        """Upload profil vers OpenMetadata."""
        try:
            self.openmetadata_client.upload_table_profile(table_fqn, profile)
        except Exception as e:
            self.logger.warning(f"Upload profil échoué pour {table_fqn}: {str(e)}")
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Retourne le schéma de configuration pour l'UI OpenMetadata.
        """
        return {
            "title": "Profiler Agent Configuration",
            "type": "object",
            "properties": {
                "dremio": {
                    "title": "Dremio Configuration",
                    "type": "object",
                    "properties": {
                        "url": {
                            "title": "Dremio URL",
                            "type": "string",
                            "default": "http://localhost:9047"
                        },
                        "username": {
                            "title": "Username",
                            "type": "string",
                            "default": "admin"
                        },
                        "password": {
                            "title": "Password",
                            "type": "string",
                            "format": "password"
                        }
                    },
                    "required": ["url", "username", "password"]
                },
                "tables": {
                    "title": "Tables to Profile",
                    "description": "Liste des tables (FQN). Si vide, toutes les tables",
                    "type": "array",
                    "items": {"type": "string"},
                    "default": []
                },
                "sample_size": {
                    "title": "Sample Size",
                    "description": "Taille échantillon pour profilage",
                    "type": "integer",
                    "default": 10000,
                    "minimum": 1000,
                    "maximum": 100000
                },
                "openmetadata": {
                    "title": "OpenMetadata Configuration",
                    "type": "object",
                    "properties": {
                        "api_url": {
                            "title": "API URL",
                            "type": "string",
                            "default": "http://localhost:8585/api"
                        },
                        "token": {
                            "title": "JWT Token",
                            "type": "string",
                            "format": "password"
                        },
                        "service_name": {
                            "title": "Service Name",
                            "type": "string",
                            "default": "dremio_service"
                        }
                    },
                    "required": ["api_url", "token", "service_name"]
                },
                "schedule": {
                    "title": "Schedule", 
                    "description": "Planification cron",
                    "type": "string",
                    "default": "0 3 * * 0"
                }
            },
            "required": ["dremio", "openmetadata"]
        }