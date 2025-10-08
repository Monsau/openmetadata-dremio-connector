#!/usr/bin/env python3
"""
🎯 CRÉATION AUTOMATIQUE DES VDS COMME DES VUES
==============================================
Crée automatiquement des VDS (Virtual Data Sets) dans CustomDB_Analytics
qui apparaissent comme des vues SQL dans Dremio.

Basé sur la gist officielle Dremio de naren-dremio :
https://gist.github.com/naren-dremio/8ab2f72342b3e94718756e367a9a448b
"""

import logging
import sys
import requests
import json
import time
import traceback

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DremioVDSCreator:
    """Créateur de VDS automatique pour Dremio"""
    
    def __init__(self):
        self.base_url = "http://localhost:9047"
        self.username = "admin"
        self.password = "admin123"
        
        self.session = requests.Session()
        self.token = None
        self.auth_header = {}
        
        # VDS à créer automatiquement
        self.vds_definitions = [
            {
                "name": "vue_clients",
                "description": "Vue des clients PostgreSQL",
                "sql": 'SELECT client_id, nom, email, ville, date_creation FROM PostgreSQL_Business.business_db.public.clients ORDER BY client_id',
                "context": ["CustomDB_Analytics"]
            },
            {
                "name": "vue_produits", 
                "description": "Vue des produits PostgreSQL",
                "sql": 'SELECT produit_id, nom, categorie, prix, stock FROM PostgreSQL_Business.business_db.public.produits ORDER BY categorie, nom',
                "context": ["CustomDB_Analytics"]
            },
            {
                "name": "vue_commandes",
                "description": "Vue des commandes avec jointures",
                "sql": '''SELECT 
                    c.commande_id,
                    cl.nom as client_nom,
                    p.nom as produit_nom,
                    c.quantite,
                    c.prix_unitaire,
                    (c.quantite * c.prix_unitaire) as total,
                    c.date_commande
                FROM PostgreSQL_Business.business_db.public.commandes c
                JOIN PostgreSQL_Business.business_db.public.clients cl ON c.client_id = cl.client_id
                JOIN PostgreSQL_Business.business_db.public.produits p ON c.produit_id = p.produit_id
                ORDER BY c.date_commande DESC''',
                "context": ["CustomDB_Analytics"]
            },
            {
                "name": "vue_stats_clients",
                "description": "Statistiques clients agrégées", 
                "sql": '''SELECT 
                    cl.ville,
                    COUNT(*) as nb_clients,
                    COUNT(c.commande_id) as nb_commandes,
                    COALESCE(SUM(c.quantite * c.prix_unitaire), 0) as chiffre_affaires
                FROM PostgreSQL_Business.business_db.public.clients cl
                LEFT JOIN PostgreSQL_Business.business_db.public.commandes c ON cl.client_id = c.client_id
                GROUP BY cl.ville
                ORDER BY chiffre_affaires DESC''',
                "context": ["CustomDB_Analytics"]
            }
        ]
        
        # VDS pour OpenSearch (si disponible)
        self.opensearch_vds = [
            {
                "name": "vue_recherches_users",
                "description": "Vue des recherches utilisateurs OpenSearch",
                "sql": 'SELECT user_id, search_query, category, results_count, click_through FROM OpenSearch_Analytics.user_searches ORDER BY timestamp DESC',
                "context": ["CustomDB_Analytics"]
            }
        ]
        
        # VDS pour MinIO (si disponible)
        self.minio_vds = [
            {
                "name": "vue_fichiers_minio",
                "description": "Vue des fichiers MinIO",
                "sql": 'SELECT path, size, modified FROM MinIO_Storage WHERE path LIKE \'%.json\' OR path LIKE \'%.csv\' ORDER BY modified DESC',
                "context": ["CustomDB_Analytics"]
            }
        ]
    
    def login(self):
        """Connexion Dremio selon la méthode officielle"""
        logger.info("🔐 Connexion Dremio...")
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = json.dumps({
            "userName": self.username,
            "password": self.password
        })
        
        try:
            response = requests.post(
                f"{self.base_url}/apiv2/login", 
                headers=headers, 
                data=data, 
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                token = response.json()['token']
                # ⚡ IMPORTANT: Préfixe _dremio obligatoire selon la gist officielle
                authorization_code = '_dremio' + token
                
                self.auth_header = {
                    'Authorization': authorization_code,
                    'Content-Type': 'application/json',
                }
                
                # Mettre à jour la session
                self.session.headers.update(self.auth_header)
                
                logger.info("✅ Connexion Dremio réussie")
                return True
            else:
                logger.error(f"❌ Connexion échouée: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False
    
    def ensure_space_exists(self, space_name="CustomDB_Analytics"):
        """S'assurer que l'espace CustomDB_Analytics existe"""
        logger.info(f"🏗️ Vérification espace {space_name}...")
        
        # Essayer de récupérer l'espace
        try:
            response = requests.get(
                f"{self.base_url}/api/v3/catalog/by-path/{space_name}",
                headers=self.auth_header,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Espace {space_name} existe déjà")
                return True
                
        except Exception:
            pass  # Continue pour créer l'espace
        
        # Créer l'espace s'il n'existe pas
        logger.info(f"📁 Création espace {space_name}...")
        
        data = json.dumps({
            "name": space_name,
            "accessControlList": {
                "userControls": [],
                "groupControls": []
            }
        })
        
        try:
            response = requests.put(
                f"{self.base_url}/apiv2/space/{space_name}",
                headers=self.auth_header,
                data=data,
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Espace {space_name} créé")
                return True
            else:
                logger.error(f"❌ Erreur création espace: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur création espace: {e}")
            return False
    
    def create_vds(self, vds_definition):
        """Créer une VDS selon la méthode officielle Dremio"""
        name = vds_definition["name"]
        sql = vds_definition["sql"]
        context = vds_definition["context"]
        
        logger.info(f"🎯 Création VDS {name}...")
        
        # Construire la requête CREATE VDS selon la gist officielle
        create_sql = f'CREATE VDS {name} AS {sql}'
        
        data = json.dumps({
            "sql": create_sql,
            "context": context
        })
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v3/sql",
                headers=self.auth_header,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                job_id = response.json().get('id')
                logger.info(f"   ✅ Job VDS {name} créé: {job_id}")
                
                # Attendre completion du job (selon la gist officielle)
                return self._wait_for_job_completion(job_id, name)
            else:
                logger.error(f"   ❌ Erreur VDS {name}: {response.status_code}")
                logger.debug(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Exception VDS {name}: {e}")
            return False
    
    def _wait_for_job_completion(self, job_id, vds_name, max_wait=60):
        """Attendre la completion d'un job selon la gist officielle"""
        logger.info(f"   ⏳ Attente completion job {vds_name}...")
        
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v3/job/{job_id}",
                    headers=self.auth_header,
                    timeout=10
                )
                
                if response.status_code == 200:
                    job_state = response.json().get('jobState')
                    
                    if job_state == 'COMPLETED':
                        logger.info(f"   ✅ VDS {vds_name} créée avec succès")
                        return True
                    elif job_state == 'FAILED':
                        logger.error(f"   ❌ Job {vds_name} échoué")
                        return False
                    else:
                        logger.debug(f"   ⏳ Job {vds_name} état: {job_state}")
                        time.sleep(1)
                else:
                    logger.debug(f"   ⚠️ Erreur status job: {response.status_code}")
                    time.sleep(1)
                    
            except Exception as e:
                logger.debug(f"   ⚠️ Exception status job: {e}")
                time.sleep(1)
        
        logger.warning(f"   ⚠️ Timeout job {vds_name}")
        return False
    
    def test_vds_query(self, vds_name, space="CustomDB_Analytics"):
        """Tester une VDS avec une requête SELECT"""
        logger.info(f"🧪 Test VDS {vds_name}...")
        
        test_sql = f'SELECT * FROM {space}.{vds_name} LIMIT 3'
        
        data = json.dumps({
            "sql": test_sql
        })
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v3/sql",
                headers=self.auth_header,
                data=data,
                timeout=15
            )
            
            if response.status_code == 200:
                job_id = response.json().get('id')
                
                # Attendre et récupérer les résultats
                if self._wait_for_job_completion(job_id, f"test_{vds_name}", max_wait=30):
                    
                    # Récupérer les résultats
                    results_response = requests.get(
                        f"{self.base_url}/api/v3/job/{job_id}/results",
                        headers=self.auth_header,
                        timeout=10
                    )
                    
                    if results_response.status_code == 200:
                        results = results_response.json()
                        row_count = len(results.get('rows', []))
                        logger.info(f"   ✅ VDS {vds_name} fonctionnelle: {row_count} lignes")
                        return True
                    else:
                        logger.warning(f"   ⚠️ Pas de résultats pour {vds_name}")
                        return False
                else:
                    logger.warning(f"   ⚠️ Test {vds_name} timeout")
                    return False
            else:
                logger.error(f"   ❌ Erreur test {vds_name}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Exception test {vds_name}: {e}")
            return False
    
    def check_sources_availability(self):
        """Vérifier quelles sources sont disponibles"""
        logger.info("🔍 Vérification sources disponibles...")
        
        available_sources = {
            "PostgreSQL_Business": False,
            "OpenSearch_Analytics": False,
            "MinIO_Storage": False
        }
        
        for source_name in available_sources.keys():
            try:
                # Tenter une requête simple sur la source
                test_sql = f'SHOW TABLES IN {source_name}'
                
                data = json.dumps({"sql": test_sql})
                
                response = requests.post(
                    f"{self.base_url}/api/v3/sql",
                    headers=self.auth_header,
                    data=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    job_id = response.json().get('id')
                    if self._wait_for_job_completion(job_id, f"check_{source_name}", max_wait=15):
                        available_sources[source_name] = True
                        logger.info(f"   ✅ {source_name} disponible")
                    else:
                        logger.debug(f"   ⚠️ {source_name} timeout")
                else:
                    logger.debug(f"   ⚠️ {source_name} non disponible")
                    
            except Exception as e:
                logger.debug(f"   ⚠️ {source_name}: {e}")
        
        return available_sources
    
    def create_all_vds(self):
        """Créer toutes les VDS selon les sources disponibles"""
        logger.info("🎯 CRÉATION VDS AUTOMATIQUE")
        logger.info("=" * 50)
        
        # 1. Vérifier les sources
        logger.info("\n[1/4] Vérification sources...")
        available_sources = self.check_sources_availability()
        
        # 2. S'assurer que l'espace existe
        logger.info("\n[2/4] Espace CustomDB_Analytics...")
        if not self.ensure_space_exists():
            logger.error("❌ Impossible de créer l'espace CustomDB_Analytics")
            return False
        
        # 3. Créer les VDS selon les sources disponibles
        logger.info("\n[3/4] Création VDS...")
        
        created_vds = []
        failed_vds = []
        
        # VDS PostgreSQL (prioritaires)
        if available_sources["PostgreSQL_Business"]:
            logger.info("   📊 VDS PostgreSQL...")
            for vds_def in self.vds_definitions:
                if self.create_vds(vds_def):
                    created_vds.append(vds_def["name"])
                else:
                    failed_vds.append(vds_def["name"])
                time.sleep(2)  # Éviter surcharge
        
        # VDS OpenSearch (si disponible)
        if available_sources["OpenSearch_Analytics"]:
            logger.info("   🔍 VDS OpenSearch...")
            for vds_def in self.opensearch_vds:
                if self.create_vds(vds_def):
                    created_vds.append(vds_def["name"])
                else:
                    failed_vds.append(vds_def["name"])
                time.sleep(2)
        
        # VDS MinIO (si disponible)
        if available_sources["MinIO_Storage"]:
            logger.info("   📦 VDS MinIO...")
            for vds_def in self.minio_vds:
                if self.create_vds(vds_def):
                    created_vds.append(vds_def["name"])
                else:
                    failed_vds.append(vds_def["name"])
                time.sleep(2)
        
        # 4. Tester les VDS créées
        logger.info("\n[4/4] Test VDS...")
        working_vds = []
        
        for vds_name in created_vds:
            if self.test_vds_query(vds_name):
                working_vds.append(vds_name)
            time.sleep(1)
        
        # Résumé
        logger.info(f"\n📊 RÉSULTATS VDS")
        logger.info("=" * 50)
        logger.info(f"✅ VDS créées: {len(created_vds)}")
        logger.info(f"✅ VDS fonctionnelles: {len(working_vds)}")
        logger.info(f"❌ VDS échouées: {len(failed_vds)}")
        
        if working_vds:
            logger.info(f"\n🎊 VDS DISPONIBLES COMME VUES:")
            for vds in working_vds:
                logger.info(f"   📊 SELECT * FROM CustomDB_Analytics.{vds}")
        
        if failed_vds:
            logger.info(f"\n⚠️ VDS ÉCHOUÉES:")
            for vds in failed_vds:
                logger.info(f"   ❌ {vds}")
        
        return len(working_vds) > 0
    
    def run_complete_setup(self):
        """Configuration complète VDS"""
        logger.info("🚀 CRÉATION AUTOMATIQUE VDS DREMIO")
        logger.info("=" * 55)
        
        # 1. Connexion
        if not self.login():
            logger.error("❌ Échec connexion Dremio")
            return False
        
        # 2. Créer toutes les VDS
        success = self.create_all_vds()
        
        if success:
            logger.info("\n🎊 VDS CRÉÉES AVEC SUCCÈS!")
            logger.info("\n✨ UTILISATION:")
            logger.info("   1. Ouvrez Dremio UI: http://localhost:9047")
            logger.info("   2. Allez dans CustomDB_Analytics")
            logger.info("   3. Vos VDS apparaissent comme des VUES!")
            logger.info("\n🎯 EXEMPLE REQUÊTE:")
            logger.info("   SELECT * FROM CustomDB_Analytics.vue_clients")
            logger.info("   SELECT * FROM CustomDB_Analytics.vue_stats_clients")
        else:
            logger.warning("⚠️ Aucune VDS n'a pu être créée")
        
        return success

def main():
    """Fonction principale"""
    print("🎯 Création automatique VDS Dremio")
    
    try:
        creator = DremioVDSCreator()
        success = creator.run_complete_setup()
        
        if success:
            print("\n🎊 CONFIGURATION VDS TERMINÉE!")
            print("Vos VDS sont maintenant disponibles comme des vues SQL!")
        else:
            print("\n❌ Échec création VDS")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        logger.debug(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)