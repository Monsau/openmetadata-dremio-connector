"""
Agent Metadata pour OpenMetadata.

Cet agent gère l'ingestion et synchronisation des métadonnées Dremio.
"""

import logging
from typing import Dict, List, Optional, Any

from ..clients.dremio_client import DremioClient
from ..clients.openmetadata_client import OpenMetadataClient
from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MetadataAgent(BaseAgent):
    """
    Agent spécialisé pour l'ingestion des métadonnées Dremio.
    
    Fonctionnalités:
    - Découverte automatique ressources Dremio
    - Synchronisation incrémentale
    - Gestion des espaces/sources/tables
    - Métadonnées colonnes avec types
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise l'agent metadata.
        
        Args:
            config: Configuration agent
                - dremio: Config Dremio (url, user, password)
                - openmetadata: Config OpenMetadata
                - sync_mode: Mode sync (full/incremental)
        """
        super().__init__(config)
        self.agent_type = "metadata"
        
        # Config Dremio
        dremio_config = config.get('dremio', {})
        if not dremio_config:
            raise ValueError("Configuration dremio requise")
            
        self.sync_mode = config.get('sync_mode', 'incremental')
        
        # Initialise clients
        self.dremio_client = DremioClient(dremio_config)
        self.openmetadata_client = OpenMetadataClient(self.openmetadata_config)
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Valide la configuration de l'agent metadata.
        
        Returns:
            Résultat validation
        """
        errors = []
        
        # Vérifier config Dremio
        try:
            if not self.dremio_client.test_connection():
                errors.append("Connexion Dremio échouée")
        except Exception as e:
            errors.append(f"Erreur Dremio: {str(e)}")
        
        # Vérifier config OpenMetadata
        om_errors = self._validate_openmetadata_config()
        errors.extend(om_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'config': self.config
        }
    
    def run(self) -> Dict[str, Any]:
        """
        Exécute la synchronisation des métadonnées.
        
        Returns:
            Statistiques de synchronisation
        """
        try:
            self.logger.info("📡 Démarrage MetadataAgent")
            
            # 1. Validation
            validation = self.validate_config()
            if not validation['valid']:
                raise ValueError(f"Config invalide: {validation['errors']}")
            
            # 2. Découverte Dremio
            self.logger.info("🔍 Découverte ressources Dremio...")
            if self.sync_mode == 'full':
                resources = self.dremio_client.discover_all_resources()
            else:
                resources = self.dremio_client.discover_incremental_resources()
                
            self.logger.info(f"  ✓ {len(resources)} ressources trouvées")
            
            # 3. Synchronisation OpenMetadata
            sync_stats = {
                'databases': 0,
                'schemas': 0, 
                'tables': 0,
                'errors': []
            }
            
            self.logger.info("⬆️ Synchronisation OpenMetadata...")
            
            for resource in resources:
                try:
                    if resource['type'] == 'space':
                        self._sync_database(resource)
                        sync_stats['databases'] += 1
                        
                    elif resource['type'] == 'folder':
                        self._sync_schema(resource)
                        sync_stats['schemas'] += 1
                        
                    elif resource['type'] in ['table', 'view']:
                        self._sync_table(resource)
                        sync_stats['tables'] += 1
                        
                except Exception as e:
                    error_msg = f"Erreur sync {resource['name']}: {str(e)}"
                    self.logger.error(error_msg)
                    sync_stats['errors'].append(error_msg)
            
            # 4. Résultats
            result = {
                'status': 'success',
                'agent_type': self.agent_type,
                'sync_mode': self.sync_mode,
                'resources_discovered': len(resources),
                'sync_statistics': sync_stats,
                'timestamp': self._get_timestamp()
            }
            
            self.logger.info("✅ MetadataAgent terminé avec succès")
            return result
            
        except Exception as e:
            error_result = {
                'status': 'failed',
                'agent_type': self.agent_type,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }
            self.logger.error(f"❌ Erreur MetadataAgent: {str(e)}")
            return error_result
    
    def _sync_database(self, space_resource: Dict[str, Any]) -> str:
        """Synchronise un espace Dremio comme database."""
        return self.openmetadata_client.create_or_update_database(
            name=space_resource['name'],
            description=space_resource.get('description', ''),
            service_name=self.openmetadata_config['service_name']
        )
    
    def _sync_schema(self, folder_resource: Dict[str, Any]) -> str:
        """Synchronise un dossier Dremio comme schema."""
        return self.openmetadata_client.create_or_update_schema(
            name=folder_resource['name'],
            database_name=folder_resource['space'],
            description=folder_resource.get('description', '')
        )
    
    def _sync_table(self, table_resource: Dict[str, Any]) -> str:
        """Synchronise une table/vue Dremio."""
        return self.openmetadata_client.create_or_update_table(
            name=table_resource['name'],
            database_name=table_resource['space'],
            schema_name=table_resource.get('folder', 'default'),
            columns=table_resource.get('columns', []),
            table_type=table_resource['type'],
            description=table_resource.get('description', '')
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Retourne le schéma de configuration pour l'UI OpenMetadata.
        """
        return {
            "title": "Metadata Agent Configuration",
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
                "sync_mode": {
                    "title": "Sync Mode",
                    "description": "Mode de synchronisation",
                    "type": "string",
                    "enum": ["full", "incremental"],
                    "default": "incremental"
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
                    "default": "0 1 * * *"
                }
            },
            "required": ["dremio", "openmetadata"]
        }