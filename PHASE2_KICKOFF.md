# 🚀 Phase 2: Intégration dbt - Guide de Démarrage

**Date début**: 2025-01-10  
**Estimation**: 2-3 jours  
**Prérequis**: ✅ Phase 1 terminée

---

## 🎯 Objectifs Phase 2

### 1️⃣ Intégration dbt Core
- Parser `manifest.json` pour extraire les modèles dbt
- Ingérer modèles comme tables dans OpenMetadata
- Capturer métadonnées dbt (tests, descriptions, tags)

### 2️⃣ Lineage Automatique
- Extraire dépendances upstream/downstream du manifest
- Créer lineage automatique entre tables
- Gérer lineage stg_* → marts/* → reporting/*

### 3️⃣ Vérification Lineage
- Implémenter checker de lineage
- Valider cohérence lineage dans OpenMetadata
- Générer rapports de lineage

---

## 📋 Plan de Développement

### Étape 1: Structure de Base (30 min)

**Créer dossier dbt**:
```bash
mkdir src/dremio_connector/dbt
touch src/dremio_connector/dbt/__init__.py
touch src/dremio_connector/dbt/dbt_integration.py
touch src/dremio_connector/dbt/lineage_checker.py
```

**__init__.py**:
```python
"""Module dbt integration"""
from .dbt_integration import DbtIntegration
from .lineage_checker import LineageChecker

__all__ = ['DbtIntegration', 'LineageChecker']
```

---

### Étape 2: DbtIntegration (2-3h)

**Fichier**: `src/dremio_connector/dbt/dbt_integration.py`

**Classe principale**:
```python
class DbtIntegration:
    """Intégration dbt manifest → OpenMetadata"""
    
    def __init__(self, manifest_path: str, openmetadata_config: dict):
        """
        Args:
            manifest_path: Chemin vers dbt/target/manifest.json
            openmetadata_config: Config OpenMetadata (API URL, token, service)
        """
        self.manifest_path = manifest_path
        self.manifest = self._load_manifest()
        self.om_client = OpenMetadataClient(openmetadata_config)
        
    def _load_manifest(self) -> dict:
        """Charge et valide manifest.json"""
        # Lire manifest.json
        # Valider structure
        # Retourner dict
        
    def extract_models(self) -> List[Dict]:
        """
        Extrait tous les modèles dbt du manifest
        
        Returns:
            Liste de dicts:
            {
                'name': 'stg_customers',
                'database': 'Analytics',
                'schema': 'staging',
                'columns': [...],
                'depends_on': ['source.customers'],
                'description': '...',
                'tests': [...]
            }
        """
        models = []
        for node_id, node in self.manifest['nodes'].items():
            if node['resource_type'] == 'model':
                model = {
                    'name': node['name'],
                    'database': node['database'],
                    'schema': node['schema'],
                    'columns': self._extract_columns(node),
                    'depends_on': node['depends_on']['nodes'],
                    'description': node.get('description', ''),
                    'tests': self._extract_tests(node)
                }
                models.append(model)
        return models
    
    def _extract_columns(self, node: dict) -> List[Dict]:
        """Extrait colonnes avec types et descriptions"""
        # Parser node['columns']
        # Retourner [{'name': ..., 'type': ..., 'description': ...}]
        
    def _extract_tests(self, node: dict) -> List[str]:
        """Extrait tests dbt associés"""
        # Parser tests liés au modèle
        # Retourner ['unique', 'not_null', ...]
        
    def create_lineage(self, model: dict) -> Dict:
        """
        Crée lineage pour un modèle
        
        Args:
            model: Dict modèle extrait par extract_models()
            
        Returns:
            {
                'upstream': ['source.customers', 'stg_orders'],
                'downstream': ['marts.customers_enriched']
            }
        """
        # Parser depends_on pour upstream
        # Parcourir manifest pour trouver downstream
        # Retourner dict avec upstream/downstream
        
    def ingest_to_openmetadata(self, models: List[Dict]) -> Dict[str, int]:
        """
        Ingère modèles dbt dans OpenMetadata
        
        Args:
            models: Liste modèles de extract_models()
            
        Returns:
            Statistiques: {'tables_created': X, 'lineage_created': Y}
        """
        stats = {'tables_created': 0, 'lineage_created': 0}
        
        for model in models:
            # Créer table dans OpenMetadata
            table_fqn = self.om_client.create_table(
                database=model['database'],
                schema=model['schema'],
                name=model['name'],
                columns=model['columns'],
                description=model['description']
            )
            stats['tables_created'] += 1
            
            # Créer lineage
            lineage = self.create_lineage(model)
            self.om_client.add_lineage(
                from_entity=table_fqn,
                to_entities=lineage['downstream']
            )
            stats['lineage_created'] += len(lineage['downstream'])
            
        return stats
```

---

### Étape 3: LineageChecker (1-2h)

**Fichier**: `src/dremio_connector/dbt/lineage_checker.py`

**Classe principale**:
```python
class LineageChecker:
    """Vérification lineage dans OpenMetadata"""
    
    def __init__(self, openmetadata_config: dict):
        self.om_client = OpenMetadataClient(openmetadata_config)
        
    def check_table_lineage(self, table_fqn: str) -> Dict:
        """
        Vérifie lineage d'une table
        
        Args:
            table_fqn: FQN table (ex: dremio_dbt_service.Analytics.staging.stg_customers)
            
        Returns:
            {
                'table': 'stg_customers',
                'upstream': ['source.customers'],
                'downstream': ['marts.customers_enriched'],
                'complete': True/False,
                'issues': []
            }
        """
        # Récupérer lineage depuis OpenMetadata
        lineage = self.om_client.get_lineage(table_fqn)
        
        # Vérifier cohérence
        issues = []
        if not lineage.get('upstream'):
            issues.append(f"No upstream lineage for {table_fqn}")
        
        return {
            'table': table_fqn.split('.')[-1],
            'upstream': lineage.get('upstream', []),
            'downstream': lineage.get('downstream', []),
            'complete': len(issues) == 0,
            'issues': issues
        }
    
    def check_all_lineage(self, database: str = None) -> Dict:
        """
        Vérifie lineage de toutes les tables
        
        Args:
            database: Filtrer par database (optionnel)
            
        Returns:
            {
                'total_tables': X,
                'tables_with_lineage': Y,
                'tables_without_lineage': Z,
                'completion_rate': 0.XX,
                'details': [...]
            }
        """
        # Lister toutes les tables
        tables = self.om_client.list_tables(database=database)
        
        results = []
        for table in tables:
            result = self.check_table_lineage(table['fullyQualifiedName'])
            results.append(result)
        
        # Calculer statistiques
        with_lineage = sum(1 for r in results if r['upstream'] or r['downstream'])
        
        return {
            'total_tables': len(results),
            'tables_with_lineage': with_lineage,
            'tables_without_lineage': len(results) - with_lineage,
            'completion_rate': with_lineage / len(results) if results else 0,
            'details': results
        }
    
    def visualize_lineage(self, table_fqn: str, output_format='ascii') -> str:
        """
        Visualise lineage d'une table
        
        Args:
            table_fqn: FQN table
            output_format: 'ascii' ou 'json'
            
        Returns:
            Représentation textuelle du lineage
        """
        lineage = self.check_table_lineage(table_fqn)
        
        if output_format == 'ascii':
            # Générer arbre ASCII
            output = f"\n{lineage['table']}\n"
            output += "├── Upstream:\n"
            for up in lineage['upstream']:
                output += f"│   └── {up}\n"
            output += "└── Downstream:\n"
            for down in lineage['downstream']:
                output += f"    └── {down}\n"
            return output
        
        elif output_format == 'json':
            return json.dumps(lineage, indent=2)
```

---

### Étape 4: Exemple Complet (30 min)

**Fichier**: `examples/dbt_ingestion_example.py`

```python
#!/usr/bin/env python3
"""
Exemple complet: Ingestion dbt → OpenMetadata avec lineage
"""
import logging
from dremio_connector.dbt import DbtIntegration, LineageChecker

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Configuration
    config = {
        'manifest_path': 'c:/projets/dremiodbt/dbt/target/manifest.json',
        'openmetadata': {
            'api_url': 'http://localhost:8585/api',
            'token': 'YOUR_JWT_TOKEN',
            'service_name': 'dremio_dbt_service'
        }
    }
    
    # Initialiser intégration dbt
    logger.info("🚀 Initialisation intégration dbt...")
    dbt = DbtIntegration(
        manifest_path=config['manifest_path'],
        openmetadata_config=config['openmetadata']
    )
    
    # Extraire modèles
    logger.info("📦 Extraction modèles dbt...")
    models = dbt.extract_models()
    logger.info(f"✓ {len(models)} modèles trouvés")
    
    # Afficher modèles
    for model in models:
        logger.info(f"  - {model['database']}.{model['schema']}.{model['name']}")
    
    # Ingérer dans OpenMetadata
    logger.info("\n🔄 Ingestion dans OpenMetadata...")
    stats = dbt.ingest_to_openmetadata(models)
    
    # Afficher résultats
    logger.info("\n✅ Ingestion terminée!")
    logger.info(f"📊 Tables créées: {stats['tables_created']}")
    logger.info(f"🔗 Lineages créés: {stats['lineage_created']}")
    
    # Vérifier lineage
    logger.info("\n🔍 Vérification lineage...")
    checker = LineageChecker(config['openmetadata'])
    
    # Vérifier une table spécifique
    table_fqn = f"{config['openmetadata']['service_name']}.Analytics.staging.stg_customers"
    lineage = checker.check_table_lineage(table_fqn)
    
    logger.info(f"\n📈 Lineage de stg_customers:")
    logger.info(checker.visualize_lineage(table_fqn, output_format='ascii'))
    
    # Vérifier tout le lineage
    all_lineage = checker.check_all_lineage(database='Analytics')
    logger.info(f"\n📊 Rapport global:")
    logger.info(f"  Total tables: {all_lineage['total_tables']}")
    logger.info(f"  Avec lineage: {all_lineage['tables_with_lineage']}")
    logger.info(f"  Sans lineage: {all_lineage['tables_without_lineage']}")
    logger.info(f"  Taux complétion: {all_lineage['completion_rate']:.1%}")

if __name__ == '__main__':
    main()
```

---

### Étape 5: Tests (1-2h)

**Fichier**: `tests/test_dbt_integration.py`

```python
import pytest
from dremio_connector.dbt import DbtIntegration, LineageChecker

def test_load_manifest():
    """Test chargement manifest.json"""
    dbt = DbtIntegration(
        manifest_path='tests/fixtures/manifest.json',
        openmetadata_config={}
    )
    assert dbt.manifest is not None
    assert 'nodes' in dbt.manifest

def test_extract_models():
    """Test extraction modèles"""
    dbt = DbtIntegration(...)
    models = dbt.extract_models()
    
    assert len(models) > 0
    assert 'name' in models[0]
    assert 'columns' in models[0]
    assert 'depends_on' in models[0]

def test_create_lineage():
    """Test création lineage"""
    dbt = DbtIntegration(...)
    model = {'depends_on': ['source.customers']}
    lineage = dbt.create_lineage(model)
    
    assert 'upstream' in lineage
    assert 'downstream' in lineage
    assert 'source.customers' in lineage['upstream']

def test_check_table_lineage():
    """Test vérification lineage"""
    checker = LineageChecker(...)
    result = checker.check_table_lineage('service.db.schema.table')
    
    assert 'upstream' in result
    assert 'downstream' in result
    assert 'complete' in result
```

---

### Étape 6: Documentation (30 min)

**Fichier**: `docs/DBT_INTEGRATION.md`

Documenter:
- Architecture intégration dbt
- Format manifest.json
- Extraction lineage
- API OpenMetadata lineage
- Exemples d'utilisation
- Troubleshooting

---

## 📊 Checklist Phase 2

### Code
- [ ] `dbt/__init__.py` créé
- [ ] `dbt/dbt_integration.py` créé (classe DbtIntegration)
- [ ] `dbt/lineage_checker.py` créé (classe LineageChecker)
- [ ] Méthode `_load_manifest()` implémentée
- [ ] Méthode `extract_models()` implémentée
- [ ] Méthode `create_lineage()` implémentée
- [ ] Méthode `ingest_to_openmetadata()` implémentée
- [ ] Méthode `check_table_lineage()` implémentée
- [ ] Méthode `check_all_lineage()` implémentée
- [ ] Méthode `visualize_lineage()` implémentée

### Exemples
- [ ] `dbt_ingestion_example.py` créé
- [ ] Exemple testé avec manifest.json réel
- [ ] Statistiques affichées correctement
- [ ] Visualisation lineage fonctionnelle

### Tests
- [ ] `test_dbt_integration.py` créé
- [ ] Test chargement manifest
- [ ] Test extraction modèles
- [ ] Test création lineage
- [ ] Test vérification lineage
- [ ] Couverture > 80%

### Documentation
- [ ] `docs/DBT_INTEGRATION.md` créé
- [ ] README.md mis à jour (section dbt)
- [ ] ENRICHMENT_PLAN.md mis à jour (Phase 2 ✅)
- [ ] Exemples documentés

### Intégration
- [ ] API OpenMetadata lineage testée
- [ ] Lineage stg → marts validé
- [ ] Lineage marts → reporting validé
- [ ] Tests d'intégration complets

---

## 🎯 Résultats Attendus

### Fonctionnalités
✅ Parsing manifest.json automatique  
✅ Extraction 100% modèles dbt  
✅ Ingestion OpenMetadata avec métadonnées  
✅ Lineage automatique upstream/downstream  
✅ Vérification cohérence lineage  
✅ Visualisation lineage ASCII/JSON  

### Métriques
- **Modèles ingérés**: 100%
- **Lineage créé**: 100%
- **Cohérence lineage**: >95%
- **Performance**: <5s pour 50 modèles

---

## 🚀 Démarrage Phase 2

**Commande pour commencer**:
```bash
# Créer structure
mkdir src/dremio_connector/dbt
cd src/dremio_connector/dbt

# Créer fichiers
touch __init__.py
touch dbt_integration.py
touch lineage_checker.py

# Lancer éditeur
code dbt_integration.py
```

**Premier objectif**: Implémenter `DbtIntegration._load_manifest()`

---

**Prêt à démarrer la Phase 2 !** 🚀
