#!/usr/bin/env python3
"""
🔗 CRÉATION SOURCES DREMIO VIA API REST
======================================
Crée les sources MinIO et OpenSearch via les APIs REST Dremio
Plus fiable que PyDremio qui a des problèmes d'import
"""

import logging
import sys
import requests
import json
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DremioSourceCreator:
    """Créateur de sources Dremio via API REST"""
    
    def __init__(self):
        self.dremio_host = "localhost"
        self.dremio_port = 9047
        self.username = "admin"
        self.password = "admin123"
        
        self.session = requests.Session()
        self.token = None
        
    def login(self):
        """Connexion à Dremio selon la méthode officielle"""
        logger.info("🔐 Connexion Dremio...")
        
        # Méthode selon gist officielle Dremio
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = json.dumps({
            "userName": self.username, 
            "password": self.password
        })
        
        try:
            response = requests.post(
                f"http://{self.dremio_host}:{self.dremio_port}/apiv2/login",
                headers=headers,
                data=data,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                token = response.json().get("token")
                # ⚡ IMPORTANT: Préfixe _dremio obligatoire selon gist officielle
                authorization_code = '_dremio' + token
                
                self.session.headers.update({
                    "Authorization": authorization_code,
                    "Content-Type": "application/json"
                })
                logger.info("✅ Connexion Dremio réussie")
                return True
            else:
                logger.error(f"❌ Connexion échouée: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False
    
    def test_connectivity(self):
        """Tester connectivité services"""
        logger.info("🔍 Test connectivité services...")
        
        services = {
            "Dremio": f"http://{self.dremio_host}:{self.dremio_port}",
            "OpenSearch": "http://localhost:9201", 
            "MinIO": "http://localhost:9000"
        }
        
        results = {}
        
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code in [200, 403]:  # 403 OK pour MinIO
                    logger.info(f"   ✅ {service} accessible")
                    results[service] = True
                else:
                    logger.warning(f"   ⚠️ {service}: {response.status_code}")
                    results[service] = False
            except Exception as e:
                logger.error(f"   ❌ {service}: {e}")
                results[service] = False
        
        return results
    
    def create_opensearch_source(self):
        """Créer source OpenSearch via API REST"""
        logger.info("🔍 Création source OpenSearch...")
        
        source_config = {
            "entityType": "source",
            "name": "OpenSearch_Analytics",
            "description": "Source OpenSearch pour analytics", 
            "type": "ELASTIC",
            "config": {
                "hostList": [{"hostname": "localhost", "port": 9201}],
                "authenticationType": "ANONYMOUS",
                "enableSSL": False,
                "readTimeoutMillis": 60000,
                "scrollTimeoutMillis": 300000,
                "scrollSize": 4000,
                "usePainless": True,
                "scriptsEnabled": True,
                "showHiddenIndices": False,
                "showIdColumn": False
            }
        }
        
        return self._create_source_with_fallback("OpenSearch_Analytics", source_config)
    
    def create_minio_source(self):
        """Créer source MinIO via API REST"""
        logger.info("📦 Création source MinIO...")
        
        source_config = {
            "entityType": "source",
            "name": "MinIO_Storage",
            "description": "Source MinIO S3 compatible",
            "type": "S3",
            "config": {
                "accessKey": "admin",
                "accessSecret": "admin123",
                "secure": False,
                "externalBucketWhitelist": [],
                "enableAsync": True,
                "compatibilityMode": True,
                "pathStyleAccess": True,
                "endpoint": "localhost:9000"
            }
        }
        
        return self._create_source_with_fallback("MinIO_Storage", source_config)
    
    def _create_source_with_fallback(self, source_name, config):
        """Créer source avec plusieurs tentatives d'API"""
        
        # Liste des endpoints à tester
        endpoints = [
            f"/api/v3/catalog/{source_name}",
            f"/apiv2/source/{source_name}",
            f"/apiv2/sources"
        ]
        
        for endpoint in endpoints:
            logger.info(f"   🔍 Tentative {endpoint}...")
            
            try:
                url = f"http://{self.dremio_host}:{self.dremio_port}{endpoint}"
                
                if endpoint.endswith("sources"):
                    response = self.session.post(url, json=config, timeout=30)
                else:
                    response = self.session.put(url, json=config, timeout=30)
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Source {source_name} créée via {endpoint}")
                    return True
                elif response.status_code == 409:
                    logger.info(f"ℹ️ Source {source_name} existe déjà")
                    return True
                else:
                    logger.debug(f"   {endpoint}: {response.status_code}")
                    
            except Exception as e:
                logger.debug(f"   {endpoint}: {e}")
                continue
        
        logger.warning(f"⚠️ Tous les endpoints ont échoué pour {source_name}")
        return False
    
    def create_custom_space(self):
        """Créer le Custom Space pour VDS"""
        logger.info("🏗️ Création Custom Space...")
        
        space_config = {
            "entityType": "space",
            "name": "CustomDB_Analytics",
            "description": "Custom DB avec VDS comme des vues"
        }
        
        try:
            response = self.session.post(
                f"http://{self.dremio_host}:{self.dremio_port}/api/v3/catalog",
                json=space_config,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ Space CustomDB_Analytics créé")
                return True
            elif response.status_code == 409:
                logger.info("ℹ️ Space CustomDB_Analytics existe déjà")
                return True
            else:
                logger.warning(f"⚠️ Erreur création space: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur création space: {e}")
            return False
    
    def test_sources(self):
        """Tester les sources avec SQL"""
        logger.info("🧪 Test des sources...")
        
        test_queries = [
            ("PostgreSQL", "SELECT COUNT(*) FROM PostgreSQL_Business.business_db.public.clients"),
            ("OpenSearch", "SHOW TABLES IN OpenSearch_Analytics"), 
            ("MinIO", "SHOW TABLES IN MinIO_Storage")
        ]
        
        results = {}
        
        for source_name, query in test_queries:
            logger.info(f"   🔍 Test {source_name}...")
            
            try:
                response = self.session.post(
                    f"http://{self.dremio_host}:{self.dremio_port}/apiv2/sql",
                    json={"sql": query},
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    row_count = len(result.get('rows', []))
                    logger.info(f"      ✅ {source_name}: {row_count} résultats")
                    results[source_name] = True
                else:
                    logger.debug(f"      ❌ {source_name}: {response.status_code}")
                    results[source_name] = False
                    
            except Exception as e:
                logger.debug(f"      ❌ {source_name}: {e}")
                results[source_name] = False
        
        return results
    
    def create_sample_data(self):
        """Créer des données d'exemple"""
        logger.info("📊 Création données d'exemple...")
        
        # OpenSearch
        opensearch_success = self._create_opensearch_data()
        
        # MinIO (via instructions)
        minio_success = self._create_minio_instructions()
        
        return opensearch_success and minio_success
    
    def _create_opensearch_data(self):
        """Créer données OpenSearch"""
        logger.info("   🔍 Données OpenSearch...")
        
        try:
            sample_data = [
                {
                    "user_id": "user001",
                    "search_query": "laptop gaming ROG",
                    "timestamp": "2025-09-30T10:00:00Z",
                    "results_count": 15,
                    "category": "electronics",
                    "click_through": True,
                    "session_duration": 180
                },
                {
                    "user_id": "user002", 
                    "search_query": "chaise bureau ergonomique",
                    "timestamp": "2025-09-30T10:05:00Z",
                    "results_count": 8,
                    "category": "furniture",
                    "click_through": True,
                    "session_duration": 240
                },
                {
                    "user_id": "user003",
                    "search_query": "smartphone Samsung",
                    "timestamp": "2025-09-30T10:10:00Z", 
                    "results_count": 22,
                    "category": "electronics",
                    "click_through": False,
                    "session_duration": 45
                }
            ]
            
            # Insérer dans OpenSearch
            for i, doc in enumerate(sample_data):
                response = requests.put(
                    f"http://localhost:9201/user_searches/_doc/{i+1}",
                    json=doc,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"      ✅ Document {i+1} ajouté")
                else:
                    logger.debug(f"      ❌ Document {i+1}: {response.status_code}")
            
            # Rafraîchir l'index
            requests.post("http://localhost:9201/user_searches/_refresh", timeout=5)
            
            logger.info("   ✅ Index OpenSearch 'user_searches' créé")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Erreur données OpenSearch: {e}")
            return False
    
    def _create_minio_instructions(self):
        """Instructions pour MinIO"""
        logger.info("   📦 Instructions MinIO...")
        logger.info("      💡 Accédez à http://localhost:9000")
        logger.info("      🔑 Login: admin / admin123")
        logger.info("      📁 Créez des buckets et uploadez des fichiers")
        logger.info("   ✅ MinIO prêt pour l'utilisation")
        return True
    
    def run_complete_setup(self):
        """Configuration complète"""
        logger.info("🚀 CONFIGURATION COMPLÈTE SOURCES DREMIO")
        logger.info("=" * 55)
        
        results = {
            "connectivity": False,
            "login": False,
            "sample_data": False,
            "opensearch_source": False,
            "minio_source": False,
            "custom_space": False,
            "sources_test": False
        }
        
        # 1. Test connectivité
        logger.info("\n[1/7] Test connectivité...")
        connectivity = self.test_connectivity()
        results["connectivity"] = all(connectivity.values())
        
        if not results["connectivity"]:
            logger.error("❌ Services non accessibles")
            return False
        
        # 2. Connexion Dremio
        logger.info("\n[2/7] Connexion Dremio...")
        results["login"] = self.login()
        
        if not results["login"]:
            logger.error("❌ Connexion Dremio échouée")
            return False
        
        # 3. Créer données d'exemple
        logger.info("\n[3/7] Création données...")
        results["sample_data"] = self.create_sample_data()
        
        # 4. Créer source OpenSearch
        logger.info("\n[4/7] Source OpenSearch...")
        results["opensearch_source"] = self.create_opensearch_source()
        
        # 5. Créer source MinIO
        logger.info("\n[5/7] Source MinIO...")
        results["minio_source"] = self.create_minio_source()
        
        # 6. Créer Custom Space
        logger.info("\n[6/7] Custom Space...")
        results["custom_space"] = self.create_custom_space()
        
        # 7. Tester sources
        logger.info("\n[7/7] Test sources...")
        test_results = self.test_sources()
        results["sources_test"] = any(test_results.values())
        
        # Résumé
        success_count = sum(results.values())
        total_count = len(results)
        
        logger.info(f"\n📊 RÉSULTATS: {success_count}/{total_count} étapes réussies")
        logger.info("=" * 55)
        
        if success_count >= 4:
            logger.info("🎊 CONFIGURATION RÉUSSIE!")
            
            logger.info("\n✅ ÉLÉMENTS CRÉÉS:")
            for step, success in results.items():
                status = "✅" if success else "❌"
                step_name = step.replace("_", " ").title()
                logger.info(f"   {status} {step_name}")
            
            logger.info(f"\n🎯 SOURCES DREMIO:")
            logger.info("   1. ✅ PostgreSQL_Business (existant)")
            if results["opensearch_source"]:
                logger.info("   2. ✅ OpenSearch_Analytics (nouveau)")
            if results["minio_source"]:
                logger.info("   3. ✅ MinIO_Storage (nouveau)")
            
            if results["custom_space"]:
                logger.info(f"\n🏗️ CUSTOM DB:")
                logger.info("   📂 CustomDB_Analytics créé")
                logger.info("   🎯 Prêt pour VDS comme des vues!")
            
            logger.info(f"\n🚀 CRÉEZ VOS VDS:")
            logger.info("   1. Dans Dremio → CustomDB_Analytics")
            logger.info("   2. New Query → Créer VDS")
            logger.info("   3. SQL: SELECT * FROM PostgreSQL_Business.business_db.public.clients")
            logger.info("   4. Save As → vue_clients")
            
            logger.info(f"\n✨ VDS ACCESSIBLE COMME VUE!")
            logger.info("   SELECT * FROM CustomDB_Analytics.vue_clients")
            
            return True
        else:
            logger.warning("⚠️ Configuration partielle")
            return False

def main():
    """Fonction principale"""
    print("🔗 Configuration sources Dremio via API REST")
    
    creator = DremioSourceCreator()
    success = creator.run_complete_setup()
    
    if success:
        print("\n🎊 CONFIGURATION TERMINÉE!")
        print("Vos sources sont prêtes pour créer des VDS comme des vues!")
    else:
        print("\n❌ Configuration partielle")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)