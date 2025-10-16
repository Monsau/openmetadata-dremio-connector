"""
Agent dbt pour OpenMetadata.

Cet agent gère l'ingestion des modèles dbt et la création du lineage automatique.
Compatible avec l'architecture des agents OpenMetadata.
"""

import json
import logging
import traceback
from typing import Dict, List, Optional, Any, Iterable
from pathlib import Path

from metadata.ingestion.api.steps import Source
from metadata.generated.schema.type.basic import SourceUrl

logger = logging.getLogger(__name__)


class DbtAgent(Source):
    """
    Agent spécialisé pour l'ingestion dbt.
    
    Fonctionnalités:
    - Parse manifest.json dbt
    - Extrait modèles avec métadonnées
    - Crée lineage automatique
    - Ingère dans OpenMetadata
    """
    
    def __init__(self, config: Dict[str, Any], metadata_config: Dict[str, Any]):
        """
        Initialise l'agent dbt.
        
        Args:
            config: Configuration agent
                - manifest_path: Chemin manifest.json
            metadata_config: Config OpenMetadata standard
        """
        super().__init__(config, metadata_config)
        self.manifest_path = config.get('manifest_path')
        
        # Validation config
        if not self.manifest_path:
            raise ValueError("manifest_path requis pour DbtAgent")
            
    @classmethod
    def create(cls, config_dict: dict, metadata_config: dict):
        """Création d'une nouvelle instance."""
        return cls(config_dict, metadata_config)

    def next_record(self) -> Iterable[Dict[str, Any]]:
        """
        Méthode requise par Source.
        Génère les modèles dbt à ingérer.
        """
        try:
            self.status.fail_total = 0
            
            # Vérifier manifest.json
            if not Path(self.manifest_path).exists():
                self.status.failed(
                    (),
                    error=f"manifest.json non trouvé: {self.manifest_path}",
                    stack_trace=traceback.format_exc(),
                )
                return
            
            # Parse manifest.json
            with open(self.manifest_path) as f:
                manifest = json.load(f)
            
            # Extraire les modèles
            for model_name, model_data in manifest.get('nodes', {}).items():
                if model_data.get('resource_type') == 'model':
                    try:
                        yield {
                            'name': model_name,
                            'description': model_data.get('description', ''),
                            'materializedType': model_data.get('config', {}).get('materialized'),
                            'sql': model_data.get('compiled_sql', model_data.get('raw_sql', '')),
                            'upstream': model_data.get('depends_on', {}).get('nodes', []),
                            'tags': model_data.get('tags', [])
                        }
                    except Exception as e:
                        self.status.failed(
                            model_name,
                            error=f"Erreur parsing modèle {model_name}: {e}",
                            stack_trace=traceback.format_exc(),
                        )
                        self.status.fail_total += 1

        except Exception as exc:
            self.status.failed(
                (),
                error=f"Erreur next_record: {exc}",
                stack_trace=traceback.format_exc(),
            )
            self.status.fail_total += 1

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut d'exécution."""
        return {
            "success": self.status.success_total,
            "failures": self.status.fail_total,
            "warnings": self.status.warn_total,
            "filtered": self.status.filtered_total,
        }

    def close(self):
        """Nettoyage post-exécution."""
        super().close()
    
