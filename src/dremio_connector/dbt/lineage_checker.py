"""
Module de vérification du lineage dans OpenMetadata.

Permet de vérifier la cohérence et la complétude du lineage.
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class LineageChecker:
    """
    Vérification et visualisation du lineage dans OpenMetadata.
    
    Cette classe permet de:
    - Vérifier le lineage d'une table spécifique
    - Vérifier le lineage de toutes les tables
    - Visualiser le lineage (ASCII, JSON)
    - Générer des rapports de cohérence
    
    Example:
        ```python
        checker = LineageChecker({
            'api_url': 'http://localhost:8585/api',
            'token': 'YOUR_JWT_TOKEN',
            'service_name': 'dremio_dbt_service'
        })
        
        # Vérifier une table
        result = checker.check_table_lineage('service.db.schema.table')
        
        # Vérifier toutes les tables
        report = checker.check_all_lineage(database='Analytics')
        
        # Visualiser
        print(checker.visualize_lineage('service.db.schema.table'))
        ```
    """
    
    def __init__(self, openmetadata_config: dict):
        """
        Initialise le checker de lineage.
        
        Args:
            openmetadata_config: Configuration OpenMetadata
                - api_url: URL API OpenMetadata
                - token: JWT token
                - service_name: Nom du service Dremio
        """
        self.api_url = openmetadata_config['api_url'].rstrip('/')
        self.token = openmetadata_config['token']
        self.service_name = openmetadata_config['service_name']
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"✓ LineageChecker initialisé pour service: {self.service_name}")
    
    def check_table_lineage(self, table_fqn: str) -> Dict[str, Any]:
        """
        Vérifie le lineage d'une table spécifique.
        
        Args:
            table_fqn: FQN de la table (ex: service.database.schema.table)
            
        Returns:
            Dict avec:
            - table: Nom de la table
            - fqn: FQN complet
            - upstream: Liste des tables upstream
            - downstream: Liste des tables downstream
            - upstream_count: Nombre upstream
            - downstream_count: Nombre downstream
            - has_lineage: True si au moins un upstream ou downstream
            - complete: True si lineage semble complet
            - issues: Liste des problèmes détectés
        """
        logger.info(f"🔍 Vérification lineage: {table_fqn}")
        
        result = {
            'table': table_fqn.split('.')[-1],
            'fqn': table_fqn,
            'upstream': [],
            'downstream': [],
            'upstream_count': 0,
            'downstream_count': 0,
            'has_lineage': False,
            'complete': False,
            'issues': []
        }
        
        try:
            # Récupérer lineage depuis OpenMetadata
            lineage_data = self._get_lineage_from_api(table_fqn)
            
            if not lineage_data:
                result['issues'].append(f"Table not found: {table_fqn}")
                return result
            
            # Parser upstream
            upstream_edges = lineage_data.get('upstreamEdges', [])
            for edge in upstream_edges:
                from_entity = edge.get('fromEntity', {})
                from_fqn = from_entity.get('fullyQualifiedName', '')
                if from_fqn:
                    result['upstream'].append(from_fqn)
            
            # Parser downstream
            downstream_edges = lineage_data.get('downstreamEdges', [])
            for edge in downstream_edges:
                to_entity = edge.get('toEntity', {})
                to_fqn = to_entity.get('fullyQualifiedName', '')
                if to_fqn:
                    result['downstream'].append(to_fqn)
            
            # Calculer métriques
            result['upstream_count'] = len(result['upstream'])
            result['downstream_count'] = len(result['downstream'])
            result['has_lineage'] = result['upstream_count'] > 0 or result['downstream_count'] > 0
            
            # Vérifier complétude (heuristique)
            # Une table staging devrait avoir des upstream (sources)
            if 'stg_' in result['table'] and result['upstream_count'] == 0:
                result['issues'].append(f"Staging table {result['table']} has no upstream lineage")
            
            # Une table mart devrait avoir des upstream (staging) et peut avoir downstream
            if 'marts' in table_fqn or 'mart_' in result['table']:
                if result['upstream_count'] == 0:
                    result['issues'].append(f"Mart table {result['table']} has no upstream lineage")
            
            result['complete'] = len(result['issues']) == 0
            
            logger.info(f"  ✓ Upstream: {result['upstream_count']}, Downstream: {result['downstream_count']}")
            
        except Exception as e:
            error_msg = f"Error checking lineage: {str(e)}"
            logger.error(error_msg)
            result['issues'].append(error_msg)
        
        return result
    
    def _get_lineage_from_api(self, table_fqn: str) -> Optional[Dict]:
        """
        Récupère le lineage d'une table via l'API OpenMetadata.
        
        Args:
            table_fqn: FQN de la table
            
        Returns:
            Dict lineage ou None si erreur
        """
        url = f"{self.api_url}/v1/lineage/table/name/{table_fqn}"
        
        try:
            response = requests.get(url, headers=self.headers, params={'upstreamDepth': 3, 'downstreamDepth': 3})
            
            if response.status_code == 404:
                logger.warning(f"Table not found in OpenMetadata: {table_fqn}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API error getting lineage: {e}")
            return None
    
    def check_all_lineage(self, database: Optional[str] = None, schema: Optional[str] = None) -> Dict[str, Any]:
        """
        Vérifie le lineage de toutes les tables.
        
        Args:
            database: Filtrer par database (optionnel)
            schema: Filtrer par schema (optionnel)
            
        Returns:
            Dict avec:
            - total_tables: Nombre total de tables
            - tables_with_lineage: Nombre avec lineage
            - tables_without_lineage: Nombre sans lineage
            - completion_rate: Taux de complétion (0.0-1.0)
            - tables_with_issues: Nombre avec problèmes
            - details: Liste résultats par table
        """
        logger.info("🔍 Vérification lineage de toutes les tables...")
        
        # Récupérer toutes les tables
        tables = self._list_tables(database=database, schema=schema)
        
        if not tables:
            logger.warning("Aucune table trouvée")
            return {
                'total_tables': 0,
                'tables_with_lineage': 0,
                'tables_without_lineage': 0,
                'completion_rate': 0.0,
                'tables_with_issues': 0,
                'details': []
            }
        
        logger.info(f"  {len(tables)} tables à vérifier")
        
        # Vérifier chaque table
        results = []
        for table in tables:
            table_fqn = table.get('fullyQualifiedName')
            if not table_fqn:
                continue
            
            result = self.check_table_lineage(table_fqn)
            results.append(result)
        
        # Calculer statistiques globales
        with_lineage = sum(1 for r in results if r['has_lineage'])
        with_issues = sum(1 for r in results if r['issues'])
        
        report = {
            'total_tables': len(results),
            'tables_with_lineage': with_lineage,
            'tables_without_lineage': len(results) - with_lineage,
            'completion_rate': with_lineage / len(results) if results else 0.0,
            'tables_with_issues': with_issues,
            'details': results
        }
        
        # Résumé
        logger.info("✅ Vérification terminée!")
        logger.info(f"  Total tables: {report['total_tables']}")
        logger.info(f"  Avec lineage: {report['tables_with_lineage']}")
        logger.info(f"  Sans lineage: {report['tables_without_lineage']}")
        logger.info(f"  Taux complétion: {report['completion_rate']:.1%}")
        logger.info(f"  Avec problèmes: {report['tables_with_issues']}")
        
        return report
    
    def _list_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> List[Dict]:
        """
        Liste toutes les tables du service.
        
        Args:
            database: Filtrer par database
            schema: Filtrer par schema
            
        Returns:
            Liste de dicts tables
        """
        url = f"{self.api_url}/v1/tables"
        params = {
            'service': self.service_name,
            'limit': 1000
        }
        
        if database:
            params['database'] = database
        if schema:
            params['databaseSchema'] = schema
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            tables = data.get('data', [])
            
            logger.debug(f"  {len(tables)} tables récupérées")
            return tables
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing tables: {e}")
            return []
    
    def visualize_lineage(self, table_fqn: str, output_format: str = 'ascii', max_depth: int = 2) -> str:
        """
        Visualise le lineage d'une table.
        
        Args:
            table_fqn: FQN de la table
            output_format: Format de sortie ('ascii' ou 'json')
            max_depth: Profondeur max pour la visualisation
            
        Returns:
            Représentation textuelle du lineage
        """
        result = self.check_table_lineage(table_fqn)
        
        if output_format == 'json':
            return json.dumps(result, indent=2)
        
        # Format ASCII
        table_name = result['table']
        output = []
        output.append("\n" + "="*80)
        output.append(f"📊 Lineage: {table_name}")
        output.append("="*80)
        output.append(f"FQN: {result['fqn']}")
        output.append("")
        
        # Upstream
        output.append(f"⬆️  Upstream ({result['upstream_count']}):")
        if result['upstream']:
            for up in result['upstream']:
                up_name = up.split('.')[-1]
                output.append(f"   └─ {up_name}")
                output.append(f"      ({up})")
        else:
            output.append("   (aucun)")
        
        output.append("")
        
        # Downstream
        output.append(f"⬇️  Downstream ({result['downstream_count']}):")
        if result['downstream']:
            for down in result['downstream']:
                down_name = down.split('.')[-1]
                output.append(f"   └─ {down_name}")
                output.append(f"      ({down})")
        else:
            output.append("   (aucun)")
        
        output.append("")
        
        # Problèmes
        if result['issues']:
            output.append(f"⚠️  Problèmes ({len(result['issues'])}):")
            for issue in result['issues']:
                output.append(f"   - {issue}")
        else:
            output.append("✅ Pas de problème détecté")
        
        output.append("="*80)
        
        return "\n".join(output)
    
    def generate_lineage_report(self, database: Optional[str] = None, output_file: Optional[str] = None) -> str:
        """
        Génère un rapport complet du lineage.
        
        Args:
            database: Filtrer par database
            output_file: Fichier de sortie (optionnel)
            
        Returns:
            Contenu du rapport (markdown)
        """
        logger.info("📝 Génération rapport lineage...")
        
        # Vérifier tout le lineage
        report = self.check_all_lineage(database=database)
        
        # Générer markdown
        lines = []
        lines.append("# 📊 Rapport de Lineage OpenMetadata")
        lines.append("")
        lines.append(f"**Service**: {self.service_name}")
        if database:
            lines.append(f"**Database**: {database}")
        lines.append("")
        
        # Statistiques globales
        lines.append("## 📈 Statistiques Globales")
        lines.append("")
        lines.append(f"- **Total tables**: {report['total_tables']}")
        lines.append(f"- **Tables avec lineage**: {report['tables_with_lineage']}")
        lines.append(f"- **Tables sans lineage**: {report['tables_without_lineage']}")
        lines.append(f"- **Taux de complétion**: {report['completion_rate']:.1%}")
        lines.append(f"- **Tables avec problèmes**: {report['tables_with_issues']}")
        lines.append("")
        
        # Tables sans lineage
        lines.append("## ⚠️ Tables Sans Lineage")
        lines.append("")
        tables_without = [d for d in report['details'] if not d['has_lineage']]
        if tables_without:
            for detail in tables_without:
                lines.append(f"- `{detail['fqn']}`")
        else:
            lines.append("✅ Toutes les tables ont du lineage!")
        lines.append("")
        
        # Tables avec problèmes
        lines.append("## 🔍 Tables avec Problèmes")
        lines.append("")
        tables_with_issues = [d for d in report['details'] if d['issues']]
        if tables_with_issues:
            for detail in tables_with_issues:
                lines.append(f"### `{detail['table']}`")
                lines.append("")
                lines.append(f"FQN: `{detail['fqn']}`")
                lines.append("")
                lines.append("Problèmes:")
                for issue in detail['issues']:
                    lines.append(f"- {issue}")
                lines.append("")
        else:
            lines.append("✅ Aucun problème détecté!")
        lines.append("")
        
        # Détails complets
        lines.append("## 📋 Détails Complets")
        lines.append("")
        for detail in report['details']:
            lines.append(f"### `{detail['table']}`")
            lines.append("")
            lines.append(f"- **FQN**: `{detail['fqn']}`")
            lines.append(f"- **Upstream**: {detail['upstream_count']}")
            for up in detail['upstream'][:3]:  # Max 3
                lines.append(f"  - `{up.split('.')[-1]}`")
            if len(detail['upstream']) > 3:
                lines.append(f"  - ... ({len(detail['upstream']) - 3} autres)")
            lines.append(f"- **Downstream**: {detail['downstream_count']}")
            for down in detail['downstream'][:3]:  # Max 3
                lines.append(f"  - `{down.split('.')[-1]}`")
            if len(detail['downstream']) > 3:
                lines.append(f"  - ... ({len(detail['downstream']) - 3} autres)")
            lines.append("")
        
        markdown = "\n".join(lines)
        
        # Sauvegarder si demandé
        if output_file:
            from pathlib import Path
            Path(output_file).write_text(markdown, encoding='utf-8')
            logger.info(f"✓ Rapport sauvegardé: {output_file}")
        
        return markdown
