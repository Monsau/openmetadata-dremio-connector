"""
Agent Lineage pour OpenMetadata.

Cet agent gère la vérification et visualisation du lineage des données.
"""

import logging
from typing import Dict, List, Optional, Any

from ..dbt.lineage_checker import LineageChecker
from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class LineageAgent(BaseAgent):
    """
    Agent spécialisé pour la gestion du lineage.
    
    Fonctionnalités:
    - Vérification lineage existant
    - Validation cohérence
    - Génération rapports
    - Visualisation graphique
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise l'agent lineage.
        
        Args:
            config: Configuration agent
                - openmetadata: Config OpenMetadata
                - service_name: Service à analyser
                - output_dir: Dossier rapports (optionnel)
        """
        super().__init__(config)
        self.agent_type = "lineage"
        self.service_name = config.get('service_name')
        self.output_dir = config.get('output_dir', 'reports')
        
        # Validation config
        if not self.service_name:
            raise ValueError("service_name requis pour LineageAgent")
            
        # Initialise checker lineage
        self.lineage_checker = LineageChecker(
            openmetadata_config=self.openmetadata_config
        )
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Valide la configuration de l'agent lineage.
        
        Returns:
            Résultat validation
        """
        errors = []
        
        # Vérifier config OpenMetadata
        om_errors = self._validate_openmetadata_config()
        errors.extend(om_errors)
        
        # Vérifier service existe
        try:
            # TODO: Vérifier que le service existe via API
            pass
        except Exception as e:
            errors.append(f"Service non accessible: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'config': self.config
        }
    
    def run(self) -> Dict[str, Any]:
        """
        Exécute l'analyse lineage.
        
        Returns:
            Statistiques et rapport
        """
        try:
            self.logger.info("🔍 Démarrage LineageAgent")
            
            # 1. Validation
            validation = self.validate_config()
            if not validation['valid']:
                raise ValueError(f"Config invalide: {validation['errors']}")
            
            # 2. Vérification lineage
            self.logger.info(f"📊 Analyse lineage service: {self.service_name}")
            lineage_report = self.lineage_checker.verify_lineage(self.service_name)
            
            # 3. Génération rapport
            self.logger.info("📋 Génération rapport...")
            report_path = self.lineage_checker.generate_report(
                lineage_report, 
                output_dir=self.output_dir
            )
            
            # 4. Visualisation (optionnel)
            viz_path = None
            try:
                self.logger.info("🎨 Génération visualisation...")
                viz_path = self.lineage_checker.visualize_lineage(
                    lineage_report,
                    output_dir=self.output_dir
                )
            except Exception as e:
                self.logger.warning(f"Visualisation échouée: {str(e)}")
            
            # 5. Résultats
            result = {
                'status': 'success',
                'agent_type': self.agent_type,
                'service_name': self.service_name,
                'lineage_stats': {
                    'total_tables': len(lineage_report.get('tables', [])),
                    'with_lineage': len([t for t in lineage_report.get('tables', []) 
                                       if t.get('upstream') or t.get('downstream')]),
                    'issues': len(lineage_report.get('issues', []))
                },
                'report_path': report_path,
                'visualization_path': viz_path,
                'timestamp': self._get_timestamp()
            }
            
            self.logger.info("✅ LineageAgent terminé avec succès")
            return result
            
        except Exception as e:
            error_result = {
                'status': 'failed',
                'agent_type': self.agent_type,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }
            self.logger.error(f"❌ Erreur LineageAgent: {str(e)}")
            return error_result
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Retourne le schéma de configuration pour l'UI OpenMetadata.
        """
        return {
            "title": "Lineage Agent Configuration", 
            "type": "object",
            "properties": {
                "service_name": {
                    "title": "Service Name",
                    "description": "Nom du service à analyser",
                    "type": "string",
                    "default": "dremio_service"
                },
                "output_dir": {
                    "title": "Output Directory",
                    "description": "Dossier pour les rapports",
                    "type": "string",
                    "default": "reports"
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
                        }
                    },
                    "required": ["api_url", "token"]
                },
                "schedule": {
                    "title": "Schedule",
                    "description": "Planification cron",
                    "type": "string",
                    "default": "0 4 * * *"
                }
            },
            "required": ["service_name", "openmetadata"]
        }