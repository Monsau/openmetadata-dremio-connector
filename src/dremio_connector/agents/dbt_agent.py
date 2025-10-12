"""
Agent dbt pour OpenMetadata.

Cet agent gère l'ingestion des modèles dbt et la création du lineage automatique.
Compatible avec l'architecture des agents OpenMetadata.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..dbt.dbt_integration import DbtIntegration
from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DbtAgent(BaseAgent):
    """
    Agent spécialisé pour l'ingestion dbt.
    
    Fonctionnalités:
    - Parse manifest.json dbt
    - Extrait modèles avec métadonnées
    - Crée lineage automatique
    - Ingère dans OpenMetadata
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise l'agent dbt.
        
        Args:
            config: Configuration agent
                - manifest_path: Chemin manifest.json
                - openmetadata: Config OpenMetadata
                - schedule: Planification (optionnel)
        """
        super().__init__(config)
        self.agent_type = "dbt"
        self.manifest_path = config.get('manifest_path')
        
        # Validation config
        if not self.manifest_path:
            raise ValueError("manifest_path requis pour DbtAgent")
            
        # Initialise intégration dbt
        self.dbt_integration = DbtIntegration(
            manifest_path=self.manifest_path,
            openmetadata_config=self.openmetadata_config
        )
        
    def validate_config(self) -> Dict[str, Any]:
        """
        Valide la configuration de l'agent dbt.
        
        Returns:
            Résultat validation avec erreurs éventuelles
        """
        errors = []
        
        # Vérifier manifest.json
        if not Path(self.manifest_path).exists():
            errors.append(f"manifest.json non trouvé: {self.manifest_path}")
            
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
        Exécute l'ingestion dbt.
        
        Returns:
            Statistiques d'exécution
        """
        try:
            self.logger.info("🚀 Démarrage DbtAgent")
            
            # 1. Validation
            validation = self.validate_config()
            if not validation['valid']:
                raise ValueError(f"Config invalide: {validation['errors']}")
            
            # 2. Extraction modèles
            self.logger.info("📊 Extraction modèles dbt...")
            models = self.dbt_integration.extract_models()
            self.logger.info(f"  ✓ {len(models)} modèles trouvés")
            
            # 3. Ingestion OpenMetadata
            self.logger.info("⬆️ Ingestion OpenMetadata...")
            stats = self.dbt_integration.ingest_to_openmetadata(models)
            
            # 4. Résultats
            result = {
                'status': 'success',
                'agent_type': self.agent_type,
                'models_found': len(models),
                'statistics': stats,
                'timestamp': self._get_timestamp()
            }
            
            self.logger.info("✅ DbtAgent terminé avec succès")
            return result
            
        except Exception as e:
            error_result = {
                'status': 'failed',
                'agent_type': self.agent_type,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }
            self.logger.error(f"❌ Erreur DbtAgent: {str(e)}")
            return error_result
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Retourne le schéma de configuration pour l'UI OpenMetadata.
        
        Returns:
            Schéma JSON pour formulaire de configuration
        """
        return {
            "title": "dbt Agent Configuration",
            "type": "object",
            "properties": {
                "manifest_path": {
                    "title": "dbt Manifest Path",
                    "description": "Chemin vers le fichier manifest.json dbt",
                    "type": "string",
                    "default": "dbt/target/manifest.json"
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
                            "default": "dremio_dbt_service"
                        }
                    },
                    "required": ["api_url", "token", "service_name"]
                },
                "schedule": {
                    "title": "Schedule",
                    "description": "Planification cron (optionnel)",
                    "type": "string",
                    "default": "0 2 * * *"
                }
            },
            "required": ["manifest_path", "openmetadata"]
        }