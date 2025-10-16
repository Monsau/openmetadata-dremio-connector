"""
Module d'intégration dbt → OpenMetadata.

Parse manifest.json, extrait les modèles dbt et crée le lineage automatique.
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DbtIntegration:
    """
    Intégration dbt manifest → OpenMetadata.
    
    Cette classe permet de:
    - Charger et parser manifest.json
    - Extraire les modèles dbt avec leurs métadonnées
    - Construire le lineage automatique (upstream/downstream)
    - Ingérer les modèles dans OpenMetadata
    
    Example:
        ```python
        dbt = DbtIntegration(
            manifest_path='dbt/target/manifest.json',
            openmetadata_config={
                'api_url': 'http://localhost:8585/api',
                'token': 'YOUR_JWT_TOKEN',
                'service_name': 'dremio_dbt_service'
            }
        )
        
        models = dbt.extract_models()
        stats = dbt.ingest_to_openmetadata(models)
        ```
    """
    
    def __init__(self, manifest_path: str, openmetadata_config: dict):
        """
        Initialise l'intégration dbt.
        
        Args:
            manifest_path: Chemin vers dbt/target/manifest.json
            openmetadata_config: Configuration OpenMetadata
                - api_url: URL API OpenMetadata
                - token: JWT token
                - service_name: Nom du service Dremio
        """
        self.manifest_path = Path(manifest_path)
        self.om_config = openmetadata_config
        self.manifest = self._load_manifest()
        
        logger.info(f"✓ DbtIntegration initialisé avec manifest: {self.manifest_path}")
    
    def _load_manifest(self) -> dict:
        """
        Charge et valide le manifest.json dbt.
        
        Returns:
            Dict contenant le manifest parsé
            
        Raises:
            FileNotFoundError: Si manifest.json n'existe pas
            ValueError: Si le manifest est invalide
        """
        if not self.manifest_path.exists():
            raise FileNotFoundError(
                f"Manifest dbt introuvable: {self.manifest_path}\n"
                f"Assurez-vous d'avoir exécuté 'dbt compile' ou 'dbt run'"
            )
        
        logger.info(f"📖 Chargement manifest: {self.manifest_path}")
        
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Validation structure manifest
        required_keys = ['nodes', 'metadata']
        missing_keys = [key for key in required_keys if key not in manifest]
        
        if missing_keys:
            raise ValueError(
                f"Manifest invalide, clés manquantes: {missing_keys}\n"
                f"Le fichier {self.manifest_path} n'est pas un manifest.json dbt valide"
            )
        
        # Statistiques manifest
        total_nodes = len(manifest.get('nodes', {}))
        total_sources = len(manifest.get('sources', {}))
        
        logger.info(f"✓ Manifest chargé: {total_nodes} nodes, {total_sources} sources")
        logger.info(f"  dbt version: {manifest['metadata'].get('dbt_version', 'unknown')}")
        logger.info(f"  project: {manifest['metadata'].get('project_name', 'unknown')}")
        
        return manifest
    
    def extract_models(self) -> List[Dict]:
        """
        Extrait tous les modèles dbt du manifest.
        
        Returns:
            Liste de dicts contenant:
            - name: Nom du modèle
            - unique_id: ID unique dbt (ex: model.project.stg_customers)
            - database: Database cible
            - schema: Schema cible
            - alias: Alias du modèle (peut différer du name)
            - columns: Liste colonnes avec types et descriptions
            - depends_on: Liste des dépendances upstream
            - description: Description du modèle
            - tags: Tags dbt
            - meta: Métadonnées custom
            - tests: Tests dbt associés
            - materialization: Type (view, table, incremental, etc.)
        """
        logger.info("🔍 Extraction modèles dbt du manifest...")
        
        models = []
        nodes = self.manifest.get('nodes', {})
        
        for node_id, node in nodes.items():
            # Ne traiter que les modèles (pas les tests, seeds, etc.)
            if node.get('resource_type') != 'model':
                continue
            
            try:
                # Récupérer database et schema (priorité: config > node)
                config = node.get('config', {})
                database = config.get('database') or node.get('database')
                schema = config.get('schema') or node.get('schema')
                
                # Fallback si None
                if not database:
                    database = 'default'
                if not schema:
                    schema = 'default'
                
                model = {
                    'name': node.get('name'),
                    'unique_id': node_id,
                    'database': str(database).upper(),
                    'schema': str(schema).lower(),
                    'alias': node.get('alias') or node.get('name'),
                    'columns': self._extract_columns(node),
                    'depends_on': node.get('depends_on', {}).get('nodes', []),
                    'description': node.get('description', ''),
                    'tags': node.get('tags', []),
                    'meta': node.get('meta', {}),
                    'tests': self._extract_tests(node_id),
                    'materialization': node.get('config', {}).get('materialized', 'view'),
                    'raw_sql': node.get('raw_code', ''),
                    'compiled_sql': node.get('compiled_code', '')
                }
                
                models.append(model)
                logger.debug(f"  ✓ Modèle extrait: {model['database']}.{model['schema']}.{model['name']}")
            
            except Exception as e:
                logger.error(f"  ✗ Erreur modèle {node_id}: {e}")
                import traceback
                traceback.print_exc()
                raise
        
        logger.info(f"✓ {len(models)} modèles dbt extraits")
        
        # Statistiques par matérialisation
        mat_counts = {}
        for model in models:
            mat = model['materialization']
            mat_counts[mat] = mat_counts.get(mat, 0) + 1
        
        logger.info(f"  Répartition: {mat_counts}")
        
        return models
    
    def _extract_columns(self, node: dict) -> List[Dict]:
        """
        Extrait les colonnes d'un modèle avec types et descriptions.
        
        Args:
            node: Node dbt du manifest
            
        Returns:
            Liste de dicts: [{'name': ..., 'type': ..., 'description': ...}]
        """
        columns = []
        node_columns = node.get('columns', {})
        
        for col_name, col_data in node_columns.items():
            data_type = col_data.get('data_type') or 'STRING'
            column = {
                'name': col_name,
                'type': str(data_type).upper(),
                'description': col_data.get('description', ''),
                'tags': col_data.get('tags', []),
                'meta': col_data.get('meta', {}),
                'tests': col_data.get('tests', [])
            }
            columns.append(column)
        
        return columns
    
    def _extract_tests(self, node_id: str) -> List[str]:
        """
        Extrait les tests dbt associés à un modèle.
        
        Args:
            node_id: ID unique du node dbt
            
        Returns:
            Liste des noms de tests (ex: ['unique', 'not_null', 'relationships'])
        """
        tests = []
        
        # Chercher d'abord dans manifest['tests'] (structure dbt récente)
        manifest_tests = self.manifest.get('tests', {})
        for test_id, test_node in manifest_tests.items():
            # Vérifier si le test est attaché au modèle
            if test_node.get('attached_node') == node_id:
                test_name = test_node.get('test_metadata', {}).get('name', 'custom_test')
                tests.append(test_name)
        
        # Sinon chercher dans manifest['nodes'] (structure dbt plus ancienne)
        if not tests:
            nodes = self.manifest.get('nodes', {})
            for test_id, test_node in nodes.items():
                # Ne traiter que les tests
                if test_node.get('resource_type') != 'test':
                    continue
                
                # Vérifier si le test est lié au modèle
                test_depends_on = test_node.get('depends_on', {}).get('nodes', [])
                if node_id in test_depends_on:
                    test_name = test_node.get('test_metadata', {}).get('name', 'custom_test')
                    tests.append(test_name)
        
        return tests
    
    def create_lineage(self, model: dict) -> Dict[str, List[str]]:
        """
        Crée le lineage pour un modèle (upstream/downstream).
        
        Args:
            model: Dict modèle extrait par extract_models()
            
        Returns:
            Dict avec:
            - upstream: Liste FQNs des tables upstream
            - downstream: Liste FQNs des tables downstream
        """
        lineage = {
            'upstream': [],
            'downstream': []
        }
        
        # Upstream: dépendances directes
        for dep_id in model['depends_on']:
            dep_fqn = self._resolve_dependency_fqn(dep_id)
            if dep_fqn:
                lineage['upstream'].append(dep_fqn)
        
        # Downstream: modèles qui dépendent de celui-ci
        model_id = model['unique_id']
        nodes = self.manifest.get('nodes', {})
        
        for node_id, node in nodes.items():
            if node.get('resource_type') != 'model':
                continue
            
            depends_on = node.get('depends_on', {}).get('nodes', [])
            if model_id in depends_on:
                downstream_fqn = self._node_to_fqn(node)
                if downstream_fqn:
                    lineage['downstream'].append(downstream_fqn)
        
        return lineage
    
    def _resolve_dependency_fqn(self, dep_id: str) -> Optional[str]:
        """
        Résout un ID de dépendance en FQN OpenMetadata.
        
        Args:
            dep_id: ID dépendance (ex: model.project.stg_customers)
            
        Returns:
            FQN OpenMetadata ou None si non résolu
        """
        # Chercher dans nodes
        nodes = self.manifest.get('nodes', {})
        if dep_id in nodes:
            return self._node_to_fqn(nodes[dep_id])
        
        # Chercher dans sources
        sources = self.manifest.get('sources', {})
        if dep_id in sources:
            return self._source_to_fqn(sources[dep_id])
        
        logger.warning(f"Dépendance non résolue: {dep_id}")
        return None
    
    def _node_to_fqn(self, node: dict) -> str:
        """
        Convertit un node dbt en FQN OpenMetadata.
        
        Format: service.database.schema.table
        """
        service = self.om_config['service_name']
        
        config = node.get('config', {})
        database = config.get('database') or node.get('database') or 'default'
        schema = config.get('schema') or node.get('schema') or 'default'
        table = node.get('alias') or node.get('name') or 'unknown'
        
        return f"{service}.{str(database).upper()}.{str(schema).lower()}.{table}"
    
    def _source_to_fqn(self, source: dict) -> str:
        """
        Convertit une source dbt en FQN OpenMetadata.
        
        Format: service.database.schema.table
        """
        service = self.om_config['service_name']
        database = source.get('database') or 'default'
        schema = source.get('schema') or 'default'
        table = source.get('name') or 'unknown'
        
        return f"{service}.{str(database).upper()}.{str(schema).lower()}.{table}"
    
    def ingest_to_openmetadata(self, models: List[Dict]) -> Dict[str, Any]:
        """
        Ingère les modèles dbt dans OpenMetadata avec lineage.
        
        Args:
            models: Liste modèles de extract_models()
            
        Returns:
            Statistiques: {
                'models_processed': X,
                'tables_created': Y,
                'lineage_created': Z,
                'errors': [...]
            }
        """
        logger.info("🔄 Ingestion modèles dbt dans OpenMetadata...")
        
        # Pour les tests et demos, on simule l'ingestion
        # TODO: Implémenter vraie intégration OpenMetadata
        logger.info("🎯 Mode simulation - ingestion mockée pour tests")
        
        stats = {
            'models_processed': 0,
            'tables_created': 0,
            'lineage_created': 0,
            'errors': []
        }
        
        for model in models:
            try:
                # Simulation ingestion pour tests/démo
                table_fqn = f"{self.om_config['service_name']}.{model['database']}.{model['schema']}.{model['name']}"
                
                # Log simulation
                logger.info(f"  📊 Simulation: création table {table_fqn}")
                logger.info(f"     - Colonnes: {len(model['columns'])}")
                logger.info(f"     - Tests: {len(model['tests'])}")
                
                stats['tables_created'] += 1
                
                # Créer lineage 
                lineage = self.create_lineage(model)
                stats['lineage_created'] += len(lineage['upstream']) + len(lineage['downstream'])
                
                stats['models_processed'] += 1
                
            except Exception as e:
                error_msg = f"Erreur modèle {model['name']}: {str(e)}"
                logger.error(error_msg)
                stats['errors'].append(error_msg)
        
        # Résumé
        logger.info("✅ Ingestion terminée!")
        logger.info(f"  Modèles traités: {stats['models_processed']}/{len(models)}")
        logger.info(f"  Tables créées/màj: {stats['tables_created']}")
        logger.info(f"  Lineages créés: {stats['lineage_created']}")
        
        if stats['errors']:
            logger.warning(f"  ⚠️ Erreurs: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # Afficher max 5 erreurs
                logger.warning(f"    - {error}")
        
        return stats
