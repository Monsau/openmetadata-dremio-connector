#!/usr/bin/env python3
"""
Exemple complet: Ingestion dbt → OpenMetadata avec lineage.

Ce script:
1. Parse manifest.json dbt
2. Extrait les modèles dbt
3. Ingère dans OpenMetadata
4. Crée le lineage automatique
5. Vérifie la cohérence du lineage
6. Génère un rapport

Usage:
    python dbt_ingestion_example.py
"""

import logging
import sys
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dremio_connector.dbt import DbtIntegration, LineageChecker

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Fonction principale."""
    
    print("\n" + "="*80)
    print("🚀 Ingestion dbt → OpenMetadata")
    print("="*80 + "\n")
    
    # ========================================================================
    # Configuration
    # ========================================================================
    
    config = {
        'manifest_path': r'c:\projets\dremiodbt\dbt\target\manifest.json',
        'openmetadata': {
            'api_url': 'http://localhost:8585/api',
            'token': 'eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImlzQm90IjpmYWxzZSwiaXNzIjoib3Blbi1tZXRhZGF0YS5vcmciLCJpYXQiOjE3MzQxMjgzODQsImVtYWlsIjoiYWRtaW5Ab3Blbm1ldGFkYXRhLm9yZyJ9.eQxVFJw3fOIUpQrHchMdvD5K2nE6EBx4gg8Tv0h48VJhQQ6cH_Y6wRKC3qg8lQFPCIQTdSZMFQDrAGbQKvnNlb7Dg8mLRO6v8_UO-mOQTQMYgkP-Zt7_YYQfSYs3L35T5UlGRrBzVHKQXP10oj9XbQtXGKPy9BVzJ8EqB8xvTQKfOXOQRHKB8bT3NtlYpQhVLaFGkR3ZQq5GXZM9VQFXKqB3Y8RQMQvT9OQF3BqXY5OQ8F7VQY3KQB8XqTOQF5BqY3VQKQx8FQ7BQY3KQR8XQqOQF9BQY3VQK',  # Remplacer par votre token
            'service_name': 'dremio_dbt_service'
        }
    }
    
    # Vérifier que le manifest existe
    manifest_path = Path(config['manifest_path'])
    if not manifest_path.exists():
        logger.error(f"❌ Manifest introuvable: {manifest_path}")
        logger.error("   Exécutez 'dbt compile' ou 'dbt run' dans le projet dremiodbt")
        return 1
    
    # ========================================================================
    # Étape 1: Initialiser intégration dbt
    # ========================================================================
    
    logger.info("📦 Étape 1: Initialisation intégration dbt")
    
    try:
        dbt = DbtIntegration(
            manifest_path=config['manifest_path'],
            openmetadata_config=config['openmetadata']
        )
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        return 1
    
    # ========================================================================
    # Étape 2: Extraire modèles dbt
    # ========================================================================
    
    logger.info("\n📦 Étape 2: Extraction modèles dbt")
    
    try:
        models = dbt.extract_models()
        
        if not models:
            logger.warning("⚠️ Aucun modèle trouvé dans le manifest")
            return 1
        
        logger.info(f"\n✓ {len(models)} modèles extraits:\n")
        
        # Afficher modèles par database/schema
        by_location = {}
        for model in models:
            location = f"{model['database']}.{model['schema']}"
            if location not in by_location:
                by_location[location] = []
            by_location[location].append(model['name'])
        
        for location, model_names in sorted(by_location.items()):
            print(f"  📁 {location}")
            for name in sorted(model_names):
                print(f"     └─ {name}")
        
    except Exception as e:
        logger.error(f"❌ Erreur extraction: {e}")
        return 1
    
    # ========================================================================
    # Étape 3: Afficher quelques modèles détaillés
    # ========================================================================
    
    logger.info("\n📋 Étape 3: Détails de quelques modèles")
    
    for model in models[:3]:  # Afficher 3 premiers modèles
        print(f"\n  📄 {model['name']}")
        print(f"     Database: {model['database']}")
        print(f"     Schema: {model['schema']}")
        print(f"     Matérialisation: {model['materialization']}")
        print(f"     Colonnes: {len(model['columns'])}")
        print(f"     Dépendances: {len(model['depends_on'])}")
        print(f"     Tests: {len(model['tests'])}")
        if model['description']:
            desc = model['description'][:100] + '...' if len(model['description']) > 100 else model['description']
            print(f"     Description: {desc}")
    
    # ========================================================================
    # Étape 4: Afficher lineage de quelques modèles
    # ========================================================================
    
    logger.info("\n🔗 Étape 4: Aperçu du lineage")
    
    for model in models[:3]:
        lineage = dbt.create_lineage(model)
        print(f"\n  📊 {model['name']}")
        print(f"     ⬆️  Upstream: {len(lineage['upstream'])}")
        for up in lineage['upstream'][:2]:
            print(f"        └─ {up.split('.')[-1]}")
        if len(lineage['upstream']) > 2:
            print(f"        ... ({len(lineage['upstream']) - 2} autres)")
        
        print(f"     ⬇️  Downstream: {len(lineage['downstream'])}")
        for down in lineage['downstream'][:2]:
            print(f"        └─ {down.split('.')[-1]}")
        if len(lineage['downstream']) > 2:
            print(f"        ... ({len(lineage['downstream']) - 2} autres)")
    
    # ========================================================================
    # Étape 5: Ingestion dans OpenMetadata
    # ========================================================================
    
    logger.info("\n🔄 Étape 5: Ingestion dans OpenMetadata")
    
    # Demander confirmation
    response = input("\n⚠️  Voulez-vous lancer l'ingestion dans OpenMetadata? (o/N): ")
    if response.lower() != 'o':
        logger.info("Ingestion annulée par l'utilisateur")
        logger.info("\n✅ Script terminé (mode lecture seule)")
        return 0
    
    try:
        stats = dbt.ingest_to_openmetadata(models)
        
        # Afficher résultats
        print("\n" + "="*80)
        print("📊 Résultats de l'ingestion")
        print("="*80)
        print(f"  Modèles traités:     {stats['models_processed']}/{len(models)}")
        print(f"  Tables créées/màj:   {stats['tables_created']}")
        print(f"  Lineages créés:      {stats['lineage_created']}")
        print(f"  Erreurs:             {len(stats['errors'])}")
        
        if stats['errors']:
            print("\n⚠️  Erreurs détectées:")
            for error in stats['errors'][:10]:  # Max 10
                print(f"  - {error}")
        
        print("="*80)
        
    except Exception as e:
        logger.error(f"❌ Erreur ingestion: {e}")
        return 1
    
    # ========================================================================
    # Étape 6: Vérifier lineage (si ingestion effectuée)
    # ========================================================================
    
    if stats['tables_created'] > 0:
        logger.info("\n🔍 Étape 6: Vérification lineage")
        
        try:
            checker = LineageChecker(config['openmetadata'])
            
            # Vérifier une table spécifique (première table ingérée)
            if models:
                first_model = models[0]
                table_fqn = f"{config['openmetadata']['service_name']}.{first_model['database']}.{first_model['schema']}.{first_model['alias']}"
                
                logger.info(f"\n📊 Exemple de lineage: {first_model['name']}")
                print(checker.visualize_lineage(table_fqn))
            
            # Vérifier tout le lineage
            logger.info("\n📈 Vérification globale du lineage...")
            report = checker.check_all_lineage()
            
            print("\n" + "="*80)
            print("📊 Rapport Global de Lineage")
            print("="*80)
            print(f"  Total tables:           {report['total_tables']}")
            print(f"  Avec lineage:           {report['tables_with_lineage']}")
            print(f"  Sans lineage:           {report['tables_without_lineage']}")
            print(f"  Taux complétion:        {report['completion_rate']:.1%}")
            print(f"  Avec problèmes:         {report['tables_with_issues']}")
            print("="*80)
            
            # Générer rapport markdown
            report_file = 'lineage_report.md'
            markdown = checker.generate_lineage_report(output_file=report_file)
            logger.info(f"\n✓ Rapport détaillé généré: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification lineage: {e}")
    
    # ========================================================================
    # Fin
    # ========================================================================
    
    print("\n" + "="*80)
    print("✅ Script terminé avec succès!")
    print("="*80 + "\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
