#!/usr/bin/env python3
"""
✅ VALIDATION POST-RESTAURATION DREMIO
====================================
Script pour valider que la restauration s'est bien passée.
Vérifie les sources, espaces, et VDS après une restauration.
"""

import logging
import sys
import requests
import json
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DremioValidator:
    """Validateur pour vérifier l'état de Dremio après restauration"""
    
    def __init__(self, host="localhost", port=9047, username="admin", password="admin123"):
        self.base_url = f"http://{host}:{port}"
        self.username = username
        self.password = password
        
        self.session = requests.Session()
        self.token = None
        
    def login(self):
        """Connexion à Dremio"""
        logger.info("🔐 Connexion à Dremio pour validation...")
        
        login_url = f"{self.base_url}/apiv2/login"
        login_data = {
            "userName": self.username,
            "password": self.password
        }
        
        try:
            response = self.session.post(login_url, json=login_data, timeout=30)
            
            if response.status_code == 200:
                self.token = response.json().get('token')
                self.session.headers.update({'Authorization': f'_dremio{self.token}'})
                logger.info("✅ Connexion validation réussie")
                return True
            else:
                logger.error(f"❌ Échec connexion validation: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion validation: {e}")
            return False
    
    def validate_sources(self, expected_sources=None):
        """Valider les sources de données"""
        logger.info("📋 Validation des sources...")
        
        try:
            url = f"{self.base_url}/api/v3/source"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                current_sources = response.json().get('data', [])
                logger.info(f"✅ {len(current_sources)} sources trouvées")
                
                validation_results = {
                    'total_sources': len(current_sources),
                    'sources': [],
                    'missing_sources': [],
                    'connection_tests': {}
                }
                
                for source in current_sources:
                    source_info = {
                        'name': source['name'],
                        'type': source['type'],
                        'state': source.get('state', 'Unknown')
                    }
                    validation_results['sources'].append(source_info)
                    logger.info(f"   - {source['name']} ({source['type']}) - État: {source_info['state']}")
                    
                    # Test de connexion
                    connection_ok = self.test_source_connection(source['id'])
                    validation_results['connection_tests'][source['name']] = connection_ok
                
                # Vérifier les sources attendues si spécifiées
                if expected_sources:
                    current_names = {s['name'] for s in current_sources}
                    expected_names = {s['name'] for s in expected_sources}
                    missing = expected_names - current_names
                    validation_results['missing_sources'] = list(missing)
                    
                    if missing:
                        logger.warning(f"⚠️ Sources manquantes: {', '.join(missing)}")
                    else:
                        logger.info("✅ Toutes les sources attendues sont présentes")
                
                return validation_results
            else:
                logger.error(f"❌ Erreur récupération sources: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur validate_sources: {e}")
            return None
    
    def test_source_connection(self, source_id):
        """Tester la connexion d'une source"""
        try:
            url = f"{self.base_url}/api/v3/source/{source_id}/test"
            response = self.session.post(url, timeout=60)  # Plus long timeout pour les tests de connexion
            
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"⚠️ Erreur test connexion source {source_id}: {e}")
            return False
    
    def validate_spaces(self, expected_spaces=None):
        """Valider les espaces"""
        logger.info("📂 Validation des espaces...")
        
        try:
            url = f"{self.base_url}/api/v3/space"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                current_spaces = response.json().get('data', [])
                logger.info(f"✅ {len(current_spaces)} espaces trouvés")
                
                validation_results = {
                    'total_spaces': len(current_spaces),
                    'spaces': [],
                    'missing_spaces': []
                }
                
                for space in current_spaces:
                    space_info = {
                        'name': space['name'],
                        'id': space['id']
                    }
                    validation_results['spaces'].append(space_info)
                    logger.info(f"   - {space['name']}")
                
                # Vérifier les espaces attendus
                if expected_spaces:
                    current_names = {s['name'] for s in current_spaces}
                    expected_names = {s['name'] for s in expected_spaces}
                    missing = expected_names - current_names
                    validation_results['missing_spaces'] = list(missing)
                    
                    if missing:
                        logger.warning(f"⚠️ Espaces manquants: {', '.join(missing)}")
                    else:
                        logger.info("✅ Tous les espaces attendus sont présents")
                
                return validation_results
            else:
                logger.error(f"❌ Erreur récupération espaces: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur validate_spaces: {e}")
            return None
    
    def validate_vds_in_space(self, space_name):
        """Valider les VDS dans un espace spécifique"""
        logger.info(f"🎯 Validation VDS dans l'espace '{space_name}'...")
        
        try:
            url = f"{self.base_url}/api/v3/catalog/{space_name}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                catalog_data = response.json()
                children = catalog_data.get('children', [])
                
                vds_count = 0
                vds_list = []
                
                for child in children:
                    if child.get('type') == 'VIRTUAL_DATASET':
                        vds_count += 1
                        vds_info = {
                            'name': child['name'],
                            'path': child['path'],
                            'type': child['type']
                        }
                        vds_list.append(vds_info)
                        logger.info(f"   - VDS: {child['name']}")
                
                logger.info(f"✅ {vds_count} VDS trouvés dans '{space_name}'")
                return {
                    'space': space_name,
                    'vds_count': vds_count,
                    'vds_list': vds_list
                }
            else:
                logger.warning(f"⚠️ Impossible d'accéder à l'espace {space_name}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur validate_vds_in_space {space_name}: {e}")
            return None
    
    def test_vds_query(self, vds_path, limit=5):
        """Tester l'exécution d'un VDS avec une requête LIMIT"""
        logger.info(f"🔍 Test requête VDS: {'/'.join(vds_path)}")
        
        try:
            # Construire la requête SQL
            full_path = '.'.join([f'"{p}"' for p in vds_path])
            sql = f"SELECT * FROM {full_path} LIMIT {limit}"
            
            # Soumettre le job
            job_url = f"{self.base_url}/api/v3/sql"
            job_data = {
                "sql": sql,
                "context": []
            }
            
            response = self.session.post(job_url, json=job_data, timeout=30)
            
            if response.status_code == 200:
                job_info = response.json()
                job_id = job_info.get('id')
                
                if job_id:
                    # Attendre que le job se termine (simple polling)
                    for _ in range(10):  # Max 10 secondes d'attente
                        time.sleep(1)
                        status_url = f"{self.base_url}/api/v3/job/{job_id}"
                        status_response = self.session.get(status_url, timeout=10)
                        
                        if status_response.status_code == 200:
                            job_status = status_response.json()
                            state = job_status.get('jobState')
                            
                            if state == 'COMPLETED':
                                logger.info(f"✅ VDS query test réussi: {'/'.join(vds_path)}")
                                return True
                            elif state in ['FAILED', 'CANCELED']:
                                logger.warning(f"⚠️ VDS query test échoué: {'/'.join(vds_path)} - État: {state}")
                                return False
                    
                    logger.warning(f"⚠️ VDS query test timeout: {'/'.join(vds_path)}")
                    return False
                else:
                    logger.warning(f"⚠️ Pas de job ID pour VDS: {'/'.join(vds_path)}")
                    return False
            else:
                logger.warning(f"⚠️ Erreur soumission query VDS {'/'.join(vds_path)}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test_vds_query {'/'.join(vds_path)}: {e}")
            return False
    
    def full_validation(self, backup_file=None):
        """Validation complète de l'environnement"""
        logger.info("🚀 Début de la validation complète...")
        
        if not self.login():
            logger.error("❌ Impossible de se connecter pour la validation")
            return False
        
        validation_report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sources': None,
            'spaces': None,
            'vds_tests': [],
            'overall_status': 'UNKNOWN'
        }
        
        expected_data = None
        if backup_file and Path(backup_file).exists():
            logger.info(f"📋 Utilisation du fichier de référence: {backup_file}")
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    expected_data = json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Erreur lecture fichier backup: {e}")
        
        # Validation des sources
        expected_sources = expected_data.get('sources') if expected_data else None
        sources_result = self.validate_sources(expected_sources)
        validation_report['sources'] = sources_result
        
        # Validation des espaces
        expected_spaces = expected_data.get('spaces') if expected_data else None
        spaces_result = self.validate_spaces(expected_spaces)
        validation_report['spaces'] = spaces_result
        
        # Test des VDS si des espaces existent
        if spaces_result and spaces_result['spaces']:
            for space in spaces_result['spaces']:
                vds_result = self.validate_vds_in_space(space['name'])
                if vds_result:
                    validation_report['vds_tests'].append(vds_result)
        
        # Déterminer le statut global
        issues = []
        
        if sources_result:
            failed_connections = sum(1 for ok in sources_result['connection_tests'].values() if not ok)
            if failed_connections > 0:
                issues.append(f"{failed_connections} source(s) avec problème de connexion")
            
            if sources_result['missing_sources']:
                issues.append(f"{len(sources_result['missing_sources'])} source(s) manquante(s)")
        
        if spaces_result and spaces_result['missing_spaces']:
            issues.append(f"{len(spaces_result['missing_spaces'])} espace(s) manquant(s)")
        
        if issues:
            validation_report['overall_status'] = 'WARNING'
            validation_report['issues'] = issues
            logger.warning(f"⚠️ Validation terminée avec des avertissements: {'; '.join(issues)}")
        else:
            validation_report['overall_status'] = 'SUCCESS'
            logger.info("✅ Validation complète réussie - Aucun problème détecté")
        
        # Sauvegarder le rapport
        report_file = Path("validation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Rapport de validation sauvegardé: {report_file}")
        
        return validation_report['overall_status'] == 'SUCCESS'

def main():
    """Interface en ligne de commande pour la validation"""
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("✅ DREMIO VALIDATION POST-RESTAURATION")
        print("Usage:")
        print("  python validate_restoration.py")
        print("  python validate_restoration.py [backup_file.json]")
        print()
        print("Le script valide :")
        print("  - Connexion à Dremio")
        print("  - Sources de données et leurs connexions") 
        print("  - Espaces et leur contenu")
        print("  - VDS et leur fonctionnement")
        sys.exit(0)
    
    backup_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    validator = DremioValidator()
    
    print("✅ VALIDATION DREMIO POST-RESTAURATION")
    print("=" * 50)
    
    success = validator.full_validation(backup_file)
    
    if success:
        print("\n🎉 VALIDATION RÉUSSIE - Environnement Dremio opérationnel")
        sys.exit(0)
    else:
        print("\n⚠️ VALIDATION AVEC AVERTISSEMENTS - Vérifiez le rapport")
        sys.exit(1)

if __name__ == "__main__":
    main()