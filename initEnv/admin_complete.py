#!/usr/bin/env python3
"""
🎛️ SCRIPT D'ADMINISTRATION DREMIO COMPLET
========================================
Gère l'environnement Dremio complet : sources, VDS, tests
"""

import logging
import sys
import requests
import json
import time
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DremioAdmin:
    """Administration complète Dremio"""
    
    def __init__(self):
        self.base_url = "http://localhost:9047"
        self.username = "admin"
        self.password = "admin123"
        self.auth_header = {}
    
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
                
                logger.info("✅ Connexion Dremio réussie")
                return True
            else:
                logger.error(f"❌ Connexion échouée: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False
    
    def check_docker_status(self):
        """Vérifier status des containers Docker"""
        logger.info("🐳 Vérification containers Docker...")
        
        containers = [
            "dremio_engine",
            "dremio_postgres", 
            "dremio_opensearch",
            "dremio_minio"
        ]
        
        status = {}
        
        for container in containers:
            try:
                result = subprocess.run(
                    ["docker", "ps", "--filter", f"name={container}", "--format", "table {{.Names}}\\t{{.Status}}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if container in result.stdout and "Up" in result.stdout:
                    status[container] = "✅ Running"
                    logger.info(f"   ✅ {container}: Running")
                else:
                    status[container] = "❌ Stopped"
                    logger.warning(f"   ❌ {container}: Stopped")
                    
            except Exception as e:
                status[container] = f"❌ Error: {e}"
                logger.error(f"   ❌ {container}: {e}")
        
        return status
    
    def list_sources(self):
        """Lister toutes les sources Dremio"""
        logger.info("📂 Sources Dremio...")
        
        try:
            response = requests.get(f"{self.base_url}/api/v3/source/", headers=self.auth_header, timeout=15)
            
            if response.status_code == 200:
                sources = response.json().get('data', [])
                
                if sources:
                    logger.info(f"   🎯 {len(sources)} sources trouvées:")
                    for source in sources:
                        name = source.get('name', 'Unknown')
                        source_type = source.get('type', 'Unknown')
                        logger.info(f"      📊 {name} ({source_type})")
                    return sources
                else:
                    logger.info("   ⚠️ Aucune source trouvée")
                    return []
            else:
                logger.error(f"   ❌ Erreur API: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"   ❌ Exception: {e}")
            return []
    
    def list_vds(self, space_name="CustomDB_Analytics"):
        """Lister toutes les VDS dans un espace"""
        logger.info(f"🎯 VDS dans {space_name}...")
        
        try:
            response = requests.get(f"{self.base_url}/api/v3/catalog/by-path/{space_name}", headers=self.auth_header, timeout=15)
            
            if response.status_code == 200:
                space_info = response.json()
                children = space_info.get('children', [])
                
                vds_list = [child for child in children if child.get('type') == 'VIRTUAL_DATASET']
                
                if vds_list:
                    logger.info(f"   🎯 {len(vds_list)} VDS trouvées:")
                    for vds in vds_list:
                        name = vds.get('name', 'Unknown')
                        logger.info(f"      📊 {name}")
                    return vds_list
                else:
                    logger.info("   ⚠️ Aucune VDS trouvée")
                    return []
            else:
                logger.error(f"   ❌ Erreur espace: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"   ❌ Exception: {e}")
            return []
    
    def test_vds_performance(self, vds_name, space="CustomDB_Analytics"):
        """Tester performance d'une VDS"""
        logger.info(f"⚡ Test performance {vds_name}...")
        
        queries = [
            f"SELECT COUNT(*) FROM {space}.{vds_name}",
            f"SELECT * FROM {space}.{vds_name} LIMIT 10"
        ]
        
        results = {}
        
        for query in queries:
            start_time = time.time()
            
            try:
                data = json.dumps({"sql": query})
                response = requests.post(f"{self.base_url}/api/v3/sql", headers=self.auth_header, data=data, timeout=30)
                
                if response.status_code == 200:
                    job_id = response.json().get('id')
                    
                    if self._wait_for_job_completion(job_id, f"perf_{vds_name}", max_wait=30):
                        execution_time = time.time() - start_time
                        
                        # Récupérer résultats
                        results_response = requests.get(f"{self.base_url}/api/v3/job/{job_id}/results", headers=self.auth_header, timeout=10)
                        
                        if results_response.status_code == 200:
                            result_data = results_response.json()
                            row_count = len(result_data.get('rows', []))
                            
                            results[query[:30]] = {
                                'success': True,
                                'execution_time': round(execution_time, 2),
                                'rows': row_count
                            }
                            
                            logger.info(f"   ✅ {query[:50]}... -> {row_count} rows in {execution_time:.2f}s")
                        else:
                            results[query[:30]] = {'success': False, 'error': 'No results'}
                    else:
                        results[query[:30]] = {'success': False, 'error': 'Timeout'}
                else:
                    results[query[:30]] = {'success': False, 'error': f'HTTP {response.status_code}'}
                    
            except Exception as e:
                results[query[:30]] = {'success': False, 'error': str(e)}
                logger.error(f"   ❌ {query[:50]}...: {e}")
        
        return results
    
    def generate_sample_queries(self):
        """Générer exemples de requêtes SQL"""
        logger.info("💡 Exemples de requêtes SQL...")
        
        queries = [
            {
                "title": "Tous les clients",
                "sql": "SELECT * FROM CustomDB_Analytics.vue_clients_simple"
            },
            {
                "title": "Produits par catégorie",
                "sql": "SELECT * FROM CustomDB_Analytics.vue_produits_simple ORDER BY categorie"
            },
            {
                "title": "Commandes récentes",
                "sql": "SELECT * FROM CustomDB_Analytics.vue_commandes_simple ORDER BY date_commande DESC LIMIT 10"
            },
            {
                "title": "Statistiques clients par ville",
                "sql": "SELECT * FROM CustomDB_Analytics.vue_clients_count ORDER BY nb_clients DESC"
            },
            {
                "title": "Jointure clients-commandes",
                "sql": """SELECT 
                    c.nom as client,
                    COUNT(cmd.commande_id) as nb_commandes,
                    SUM(cmd.quantite * cmd.prix_unitaire) as total_achats
                FROM CustomDB_Analytics.vue_clients_simple c
                LEFT JOIN CustomDB_Analytics.vue_commandes_simple cmd 
                    ON c.client_id = cmd.client_id
                GROUP BY c.client_id, c.nom
                ORDER BY total_achats DESC"""
            }
        ]
        
        logger.info(f"   🎯 {len(queries)} exemples générés:")
        for i, query in enumerate(queries, 1):
            logger.info(f"\n   📊 {i}. {query['title']}:")
            logger.info(f"      {query['sql']}")
        
        return queries
    
    def _wait_for_job_completion(self, job_id, job_name, max_wait=60):
        """Attendre completion job"""
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            try:
                response = requests.get(f"{self.base_url}/api/v3/job/{job_id}", headers=self.auth_header, timeout=10)
                
                if response.status_code == 200:
                    job_state = response.json().get('jobState')
                    
                    if job_state == 'COMPLETED':
                        return True
                    elif job_state in ['FAILED', 'CANCELLED']:
                        return False
                    else:
                        time.sleep(0.5)
                else:
                    time.sleep(0.5)
                    
            except Exception:
                time.sleep(0.5)
        
        return False
    
    def run_full_status_check(self):
        """Status complet de l'environnement"""
        logger.info("🚀 STATUS COMPLET ENVIRONNEMENT DREMIO")
        logger.info("=" * 70)
        
        # 1. Docker containers
        logger.info("\n[1/6] Containers Docker...")
        docker_status = self.check_docker_status()
        docker_ok = all("Running" in status for status in docker_status.values())
        
        if not docker_ok:
            logger.error("❌ Certains containers ne sont pas running")
            logger.info("💡 Exécutez: docker-compose up -d")
            return False
        
        # 2. Connexion Dremio
        logger.info("\n[2/6] Connexion Dremio...")
        if not self.login():
            logger.error("❌ Connexion Dremio échouée")
            return False
        
        # 3. Sources
        logger.info("\n[3/6] Sources Dremio...")
        sources = self.list_sources()
        
        # 4. VDS
        logger.info("\n[4/6] VDS CustomDB_Analytics...")
        vds_list = self.list_vds()
        
        # 5. Tests performance
        logger.info("\n[5/6] Tests performance VDS...")
        if vds_list:
            for vds in vds_list[:2]:  # Tester seulement les 2 premières
                vds_name = vds.get('name')
                if vds_name:
                    self.test_vds_performance(vds_name)
        
        # 6. Exemples de requêtes
        logger.info("\n[6/6] Exemples de requêtes...")
        queries = self.generate_sample_queries()
        
        # Résumé final
        logger.info(f"\n🎊 RÉSUMÉ ENVIRONNEMENT")
        logger.info("=" * 70)
        logger.info(f"🐳 Containers Docker: {len([s for s in docker_status.values() if 'Running' in s])}/4 running")
        logger.info(f"📂 Sources Dremio: {len(sources)} sources")
        logger.info(f"🎯 VDS CustomDB_Analytics: {len(vds_list)} VDS")
        logger.info(f"💡 Exemples SQL: {len(queries)} requêtes")
        
        if docker_ok and sources and vds_list:
            logger.info(f"\n✨ ENVIRONNEMENT PRÊT!")
            logger.info("🌐 Interface Dremio: http://localhost:9047")
            logger.info("🎯 CustomDB_Analytics → Vos VDS comme des vues!")
            
            logger.info(f"\n🚀 DÉMARRAGE RAPIDE:")
            logger.info("1. Ouvrez http://localhost:9047")
            logger.info("2. Login: admin / admin123")
            logger.info("3. Allez dans CustomDB_Analytics")
            logger.info("4. Testez: SELECT * FROM vue_clients_simple")
            
            return True
        else:
            logger.warning("⚠️ Environnement partiellement configuré")
            return False

def main():
    """Fonction principale"""
    print("🎛️ Administration Dremio complète")
    
    try:
        admin = DremioAdmin()
        success = admin.run_full_status_check()
        
        if success:
            print("\n🎊 ENVIRONNEMENT DREMIO OPÉRATIONNEL!")
            print("Tous les composants sont prêts pour l'utilisation!")
        else:
            print("\n⚠️ Problèmes détectés dans l'environnement")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)