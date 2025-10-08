#!/usr/bin/env python3
"""
🔧 SCRIPT DE RÉPARATION ET CRÉATION VDS ROBUSTE  
===============================================
Crée des VDS robustes avec gestion d'erreurs avancée
et requêtes SQL adaptées aux schémas PostgreSQL réels
"""

import logging
import sys
import requests
import json
import time
import traceback

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DremioVDSFixer:
    """Réparateur et créateur VDS robuste"""
    
    def __init__(self):
        self.base_url = "http://localhost:9047"
        self.username = "admin"
        self.password = "admin123"
        
        self.session = requests.Session()
        self.auth_header = {}
        
        # VDS robustes avec requêtes simples
        self.vds_definitions = [
            {
                "name": "vue_clients_simple",
                "description": "Vue simple des clients",
                "sql": 'SELECT * FROM PostgreSQL_Business.business_db.public.clients',
                "context": ["CustomDB_Analytics"]
            },
            {
                "name": "vue_produits_simple", 
                "description": "Vue simple des produits",
                "sql": 'SELECT * FROM PostgreSQL_Business.business_db.public.produits',
                "context": ["CustomDB_Analytics"]
            },
            {
                "name": "vue_commandes_simple",
                "description": "Vue simple des commandes",
                "sql": 'SELECT * FROM PostgreSQL_Business.business_db.public.commandes',
                "context": ["CustomDB_Analytics"]
            },
            {
                "name": "vue_clients_count",
                "description": "Nombre de clients par ville",
                "sql": 'SELECT ville, COUNT(*) as nb_clients FROM PostgreSQL_Business.business_db.public.clients GROUP BY ville',
                "context": ["CustomDB_Analytics"]
            }
        ]
    
    def login(self):
        """Connexion Dremio"""
        logger.info("🔐 Connexion Dremio...")
        
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({"userName": self.username, "password": self.password})
        
        try:
            response = requests.post(f"{self.base_url}/apiv2/login", headers=headers, data=data, verify=False, timeout=10)
            
            if response.status_code == 200:
                token = response.json()['token']
                authorization_code = '_dremio' + token
                
                self.auth_header = {
                    'Authorization': authorization_code,
                    'Content-Type': 'application/json',
                }
                self.session.headers.update(self.auth_header)
                
                logger.info("✅ Connexion Dremio réussie")
                return True
            else:
                logger.error(f"❌ Connexion échouée: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False
    
    def inspect_postgresql_schema(self):
        """Inspecter le schéma PostgreSQL réel"""
        logger.info("🔍 Inspection schéma PostgreSQL...")
        
        queries = [
            ("Tables", "SHOW TABLES IN PostgreSQL_Business.business_db.public"),
            ("Clients", "SELECT * FROM PostgreSQL_Business.business_db.public.clients LIMIT 1"),
            ("Produits", "SELECT * FROM PostgreSQL_Business.business_db.public.produits LIMIT 1"),
            ("Commandes", "SELECT * FROM PostgreSQL_Business.business_db.public.commandes LIMIT 1")
        ]
        
        schema_info = {}
        
        for name, query in queries:
            logger.info(f"   🔍 {name}...")
            
            try:
                data = json.dumps({"sql": query})
                response = requests.post(f"{self.base_url}/api/v3/sql", headers=self.auth_header, data=data, timeout=15)
                
                if response.status_code == 200:
                    job_id = response.json().get('id')
                    
                    # Attendre completion
                    if self._wait_for_job_completion(job_id, f"inspect_{name}", max_wait=20):
                        # Récupérer résultats
                        results_response = requests.get(f"{self.base_url}/api/v3/job/{job_id}/results", headers=self.auth_header, timeout=10)
                        
                        if results_response.status_code == 200:
                            results = results_response.json()
                            schema_info[name] = {
                                'success': True,
                                'columns': results.get('schema', []),
                                'sample_data': results.get('rows', [])[:1]
                            }
                            logger.info(f"      ✅ {name}: {len(results.get('schema', []))} colonnes")
                        else:
                            schema_info[name] = {'success': False, 'error': 'No results'}
                    else:
                        schema_info[name] = {'success': False, 'error': 'Job timeout'}
                else:
                    schema_info[name] = {'success': False, 'error': f'HTTP {response.status_code}'}
                    
            except Exception as e:
                logger.error(f"      ❌ {name}: {e}")
                schema_info[name] = {'success': False, 'error': str(e)}
        
        return schema_info
    
    def create_vds_with_retry(self, vds_definition, retry_count=3):
        """Créer VDS avec retry et diagnostics"""
        name = vds_definition["name"]
        sql = vds_definition["sql"]
        context = vds_definition["context"]
        
        logger.info(f"🎯 Création VDS {name}...")
        
        for attempt in range(retry_count):
            logger.info(f"   🔄 Tentative {attempt + 1}/{retry_count}...")
            
            # Test de la requête SQL d'abord
            logger.info(f"   📋 Test SQL: {sql[:100]}...")
            
            try:
                # Tester la requête sans CREATE VDS
                test_data = json.dumps({"sql": sql})
                test_response = requests.post(f"{self.base_url}/api/v3/sql", headers=self.auth_header, data=test_data, timeout=30)
                
                if test_response.status_code == 200:
                    test_job_id = test_response.json().get('id')
                    
                    if self._wait_for_job_completion(test_job_id, f"test_{name}", max_wait=30):
                        logger.info(f"   ✅ SQL valide pour {name}")
                        
                        # Maintenant créer la VDS
                        create_sql = f'CREATE VDS {name} AS {sql}'
                        create_data = json.dumps({"sql": create_sql, "context": context})
                        
                        create_response = requests.post(f"{self.base_url}/api/v3/sql", headers=self.auth_header, data=create_data, timeout=30)
                        
                        if create_response.status_code == 200:
                            create_job_id = create_response.json().get('id')
                            
                            if self._wait_for_job_completion(create_job_id, name, max_wait=60):
                                logger.info(f"   ✅ VDS {name} créée avec succès")
                                return True
                            else:
                                logger.warning(f"   ⚠️ VDS {name} timeout tentative {attempt + 1}")
                        else:
                            logger.warning(f"   ⚠️ CREATE VDS {name} échoué: {create_response.status_code}")
                            if create_response.text:
                                logger.debug(f"      Response: {create_response.text[:200]}")
                    else:
                        logger.warning(f"   ⚠️ Test SQL {name} timeout tentative {attempt + 1}")
                else:
                    logger.warning(f"   ⚠️ Test SQL {name} échoué: {test_response.status_code}")
                    if test_response.text:
                        logger.debug(f"      Response: {test_response.text[:200]}")
                
                # Attendre avant retry
                if attempt < retry_count - 1:
                    time.sleep(5)
                    
            except Exception as e:
                logger.error(f"   ❌ Exception VDS {name} tentative {attempt + 1}: {e}")
                if attempt < retry_count - 1:
                    time.sleep(5)
        
        logger.error(f"   ❌ VDS {name} échouée après {retry_count} tentatives")
        return False
    
    def _wait_for_job_completion(self, job_id, job_name, max_wait=60):
        """Attendre completion job avec diagnostics"""
        start_time = time.time()
        last_state = None
        
        while (time.time() - start_time) < max_wait:
            try:
                response = requests.get(f"{self.base_url}/api/v3/job/{job_id}", headers=self.auth_header, timeout=10)
                
                if response.status_code == 200:
                    job_info = response.json()
                    job_state = job_info.get('jobState')
                    
                    if job_state != last_state:
                        logger.debug(f"      Job {job_name}: {job_state}")
                        last_state = job_state
                    
                    if job_state == 'COMPLETED':
                        return True
                    elif job_state in ['FAILED', 'CANCELLED']:
                        logger.error(f"      Job {job_name} état final: {job_state}")
                        # Log erreur si disponible
                        error_message = job_info.get('errorMessage', 'Pas de détail d\'erreur')
                        logger.debug(f"      Erreur: {error_message}")
                        return False
                    else:
                        time.sleep(1)
                else:
                    logger.debug(f"      Erreur status job: {response.status_code}")
                    time.sleep(1)
                    
            except Exception as e:
                logger.debug(f"      Exception status job: {e}")
                time.sleep(1)
        
        logger.warning(f"      Timeout job {job_name} après {max_wait}s")
        return False
    
    def cleanup_failed_vds(self):
        """Nettoyer les VDS échouées"""
        logger.info("🧹 Nettoyage VDS échouées...")
        
        failed_vds_names = ["vue_produits", "vue_commandes", "vue_stats_clients"]
        
        for vds_name in failed_vds_names:
            try:
                # Tenter de supprimer via l'API catalog
                response = requests.get(f"{self.base_url}/api/v3/catalog/by-path/CustomDB_Analytics/{vds_name}", headers=self.auth_header, timeout=10)
                
                if response.status_code == 200:
                    vds_info = response.json()
                    vds_id = vds_info.get('id')
                    
                    if vds_id:
                        delete_response = requests.delete(f"{self.base_url}/api/v3/catalog/{vds_id}", headers=self.auth_header, timeout=10)
                        
                        if delete_response.status_code in [200, 204]:
                            logger.info(f"   ✅ VDS {vds_name} supprimée")
                        else:
                            logger.debug(f"   ⚠️ Suppression {vds_name}: {delete_response.status_code}")
                    else:
                        logger.debug(f"   ⚠️ {vds_name}: pas d'ID trouvé")
                else:
                    logger.debug(f"   ⚠️ {vds_name}: non trouvée")
                    
            except Exception as e:
                logger.debug(f"   ⚠️ Erreur suppression {vds_name}: {e}")
    
    def run_robust_setup(self):
        """Configuration robuste avec diagnostics"""
        logger.info("🔧 RÉPARATION ET CRÉATION VDS ROBUSTE")
        logger.info("=" * 60)
        
        # 1. Connexion
        if not self.login():
            logger.error("❌ Échec connexion Dremio")
            return False
        
        # 2. Nettoyer VDS échouées
        logger.info("\n[1/4] Nettoyage VDS échouées...")
        self.cleanup_failed_vds()
        
        # 3. Inspecter schéma PostgreSQL
        logger.info("\n[2/4] Inspection schéma PostgreSQL...")
        schema_info = self.inspect_postgresql_schema()
        
        # Vérifier que PostgreSQL est accessible
        if not schema_info.get("Tables", {}).get("success"):
            logger.error("❌ PostgreSQL non accessible")
            return False
        
        # 4. Créer VDS robustes
        logger.info("\n[3/4] Création VDS robustes...")
        created_vds = []
        
        for vds_def in self.vds_definitions:
            if self.create_vds_with_retry(vds_def):
                created_vds.append(vds_def["name"])
            time.sleep(3)  # Éviter surcharge
        
        # 5. Tester toutes les VDS
        logger.info("\n[4/4] Test VDS finales...")
        working_vds = []
        
        for vds_name in created_vds:
            if self._test_vds_query(vds_name):
                working_vds.append(vds_name)
        
        # Résumé final
        logger.info(f"\n🎊 RÉSULTATS FINAUX")
        logger.info("=" * 60)
        logger.info(f"✅ VDS créées: {len(created_vds)}")
        logger.info(f"✅ VDS fonctionnelles: {len(working_vds)}")
        
        if working_vds:
            logger.info(f"\n🎯 VDS DISPONIBLES COMME VUES:")
            for vds in working_vds:
                logger.info(f"   📊 SELECT * FROM CustomDB_Analytics.{vds}")
            
            logger.info(f"\n✨ ACCÈS UI DREMIO:")
            logger.info("   🌐 http://localhost:9047")
            logger.info("   📂 CustomDB_Analytics → Vos VDS comme des vues!")
        
        return len(working_vds) > 0
    
    def _test_vds_query(self, vds_name):
        """Tester requête VDS"""
        try:
            test_sql = f'SELECT * FROM CustomDB_Analytics.{vds_name} LIMIT 2'
            data = json.dumps({"sql": test_sql})
            
            response = requests.post(f"{self.base_url}/api/v3/sql", headers=self.auth_header, data=data, timeout=15)
            
            if response.status_code == 200:
                job_id = response.json().get('id')
                
                if self._wait_for_job_completion(job_id, f"test_{vds_name}", max_wait=20):
                    results_response = requests.get(f"{self.base_url}/api/v3/job/{job_id}/results", headers=self.auth_header, timeout=10)
                    
                    if results_response.status_code == 200:
                        results = results_response.json()
                        row_count = len(results.get('rows', []))
                        logger.info(f"   ✅ VDS {vds_name}: {row_count} lignes")
                        return True
            
            logger.warning(f"   ⚠️ Test {vds_name} échoué")
            return False
            
        except Exception as e:
            logger.error(f"   ❌ Exception test {vds_name}: {e}")
            return False

def main():
    """Fonction principale"""
    print("🔧 Réparation et création VDS robuste")
    
    try:
        fixer = DremioVDSFixer()
        success = fixer.run_robust_setup()
        
        if success:
            print("\n🎊 VDS ROBUSTES CRÉÉES!")
            print("Vos VDS sont maintenant disponibles comme des vues SQL dans CustomDB_Analytics!")
        else:
            print("\n❌ Échec création VDS robustes")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        logger.debug(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)