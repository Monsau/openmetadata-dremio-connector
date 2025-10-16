"""
Module d'intégration dbt pour le connecteur Dremio-OpenMetadata.

Ce module permet:
- Parser manifest.json pour extraire les modèles dbt
- Créer le lineage automatique entre modèles
- Ingérer les modèles dans OpenMetadata
- Vérifier la cohérence du lineage
"""

from .dbt_integration import DbtIntegration
from .lineage_checker import LineageChecker

__all__ = ['DbtIntegration', 'LineageChecker']
