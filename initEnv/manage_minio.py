#!/usr/bin/env python3
"""
📦 GESTIONNAIRE MINIO COMPLET POUR DREMIO
=========================================
Gère MinIO : buckets, fichiers, configuration et source Dremio
"""

import logging
import sys
import requests
import json
import time
import os
import io
import csv
from datetime import datetime, timedelta
import traceback

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinIOManager:
    """Gestionnaire MinIO complet"""
    
    def __init__(self):
        self.minio_endpoint = "http://localhost:9000"
        self.minio_console = "http://localhost:9001"
        self.access_key = "admin"
        self.secret_key = "admin123"
        
        # Configuration Dremio
        self.dremio_url = "http://localhost:9047"
        self.dremio_user = "admin"
        self.dremio_pass = "admin123"
        self.dremio_headers = {}
        
        # Buckets à créer
        self.buckets_config = [
            {
                "name": "data-lake",
                "description": "Lac de données principal",
                "files": ["customers.csv", "products.json", "sales.parquet"]
            },
            {
                "name": "analytics",
                "description": "Données d'analyse",
                "files": ["user_behavior.json", "metrics.csv"]
            },
            {
                "name": "raw-data", 
                "description": "Données brutes",
                "files": ["logs.txt", "events.json"]
            }
        ]
    
    def check_minio_status(self):
        """Vérifier status MinIO"""
        logger.info("📦 Vérification MinIO...")
        
        services = {
            "MinIO API": self.minio_endpoint,
            "MinIO Console": self.minio_console
        }
        
        status = {}
        
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code in [200, 403, 404]:  # 403/404 OK pour MinIO
                    status[service_name] = "✅ Accessible"
                    logger.info(f"   ✅ {service_name}: Accessible ({response.status_code})")
                else:
                    status[service_name] = f"⚠️ Status {response.status_code}"
                    logger.warning(f"   ⚠️ {service_name}: Status {response.status_code}")
                    
            except Exception as e:
                status[service_name] = f"❌ {str(e)}"
                logger.error(f"   ❌ {service_name}: {e}")
        
        return status
    
    def install_minio_client(self):
        """Installer le client MinIO (minio-py)"""
        logger.info("🔧 Installation client MinIO...")
        
        try:
            import subprocess
            
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "minio", "pandas"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("✅ Client MinIO installé")
                return True
            else:
                logger.error(f"❌ Erreur installation: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception installation: {e}")
            return False
    
    def connect_minio_client(self):
        """Connexion client MinIO"""
        try:
            from minio import Minio
            from minio.error import S3Error
            
            # Créer client MinIO
            self.minio_client = Minio(
                "localhost:9000",
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=False  # HTTP, pas HTTPS
            )
            
            # Test connexion
            buckets = list(self.minio_client.list_buckets())
            logger.info(f"✅ Connexion MinIO réussie - {len(buckets)} buckets existants")
            return True
            
        except ImportError:
            logger.error("❌ Module minio non installé")
            return False
        except Exception as e:
            logger.error(f"❌ Connexion MinIO échouée: {e}")
            return False
    
    def create_sample_data(self):
        """Créer des données d'exemple"""
        logger.info("📊 Création données d'exemple...")
        
        sample_data = {}
        
        # 1. Customers CSV
        customers_data = [
            ["customer_id", "name", "email", "city", "country", "signup_date"],
            ["1001", "Alice Martin", "alice@email.com", "Paris", "France", "2025-01-15"],
            ["1002", "Bob Smith", "bob@email.com", "London", "UK", "2025-02-20"],
            ["1003", "Carlos Garcia", "carlos@email.com", "Madrid", "Spain", "2025-03-10"],
            ["1004", "Diana Chen", "diana@email.com", "Tokyo", "Japan", "2025-04-05"],
            ["1005", "Erik Johnson", "erik@email.com", "Stockholm", "Sweden", "2025-05-12"]
        ]
        
        csv_content = io.StringIO()
        writer = csv.writer(csv_content)
        writer.writerows(customers_data)
        sample_data["customers.csv"] = csv_content.getvalue().encode('utf-8')
        
        # 2. Products JSON
        products_data = {
            "products": [
                {
                    "product_id": "P001",
                    "name": "Laptop Pro 15",
                    "category": "Electronics", 
                    "price": 1299.99,
                    "stock": 50,
                    "supplier": "TechCorp"
                },
                {
                    "product_id": "P002",
                    "name": "Office Chair Deluxe",
                    "category": "Furniture",
                    "price": 299.99, 
                    "stock": 25,
                    "supplier": "ComfortPlus"
                },
                {
                    "product_id": "P003",
                    "name": "Smartphone X12",
                    "category": "Electronics",
                    "price": 799.99,
                    "stock": 100,
                    "supplier": "MobileTech"
                }
            ],
            "last_updated": "2025-09-30T17:00:00Z"
        }
        sample_data["products.json"] = json.dumps(products_data, indent=2).encode('utf-8')
        
        # 3. User Behavior JSON
        user_behavior = {
            "sessions": [
                {
                    "session_id": "s001",
                    "user_id": "1001",
                    "start_time": "2025-09-30T09:00:00Z",
                    "pages_viewed": 5,
                    "duration_minutes": 12,
                    "actions": ["login", "browse", "search", "add_to_cart"]
                },
                {
                    "session_id": "s002", 
                    "user_id": "1002",
                    "start_time": "2025-09-30T10:15:00Z",
                    "pages_viewed": 3,
                    "duration_minutes": 8,
                    "actions": ["login", "browse", "logout"]
                }
            ],
            "analytics_date": "2025-09-30"
        }
        sample_data["user_behavior.json"] = json.dumps(user_behavior, indent=2).encode('utf-8')
        
        # 4. Metrics CSV
        metrics_data = [
            ["date", "page_views", "unique_visitors", "conversion_rate", "revenue"],
            ["2025-09-29", "1250", "320", "3.2", "4567.89"],
            ["2025-09-30", "1456", "398", "3.8", "5234.12"]
        ]
        
        metrics_csv = io.StringIO()
        writer = csv.writer(metrics_csv)
        writer.writerows(metrics_data)
        sample_data["metrics.csv"] = metrics_csv.getvalue().encode('utf-8')
        
        # 5. Events JSON
        events_data = {
            "events": [
                {
                    "event_id": "e001",
                    "timestamp": "2025-09-30T17:00:00Z",
                    "event_type": "purchase",
                    "user_id": "1001",
                    "product_id": "P001",
                    "value": 1299.99
                },
                {
                    "event_id": "e002",
                    "timestamp": "2025-09-30T17:05:00Z", 
                    "event_type": "view",
                    "user_id": "1002",
                    "product_id": "P002",
                    "value": 0
                }
            ]
        }
        sample_data["events.json"] = json.dumps(events_data, indent=2).encode('utf-8')
        
        # 6. Logs TXT
        logs_content = """2025-09-30 17:00:01 INFO User 1001 logged in
2025-09-30 17:00:15 INFO User 1001 viewed product P001
2025-09-30 17:00:45 INFO User 1001 added P001 to cart
2025-09-30 17:01:20 INFO User 1001 completed purchase P001
2025-09-30 17:02:05 INFO User 1002 logged in
2025-09-30 17:02:30 INFO User 1002 searched "office chair"
2025-09-30 17:03:00 INFO User 1002 viewed product P002
2025-09-30 17:03:45 INFO User 1002 logged out
"""
        sample_data["logs.txt"] = logs_content.encode('utf-8')
        
        logger.info(f"✅ {len(sample_data)} fichiers d'exemple créés")
        return sample_data
    
    def create_buckets_and_upload(self):
        """Créer buckets et uploader fichiers"""
        logger.info("🪣 Création buckets MinIO...")
        
        if not hasattr(self, 'minio_client'):
            logger.error("❌ Client MinIO non connecté")
            return False
        
        try:
            from minio.error import S3Error
            import io
            
            # Créer données d'exemple
            sample_data = self.create_sample_data()
            
            created_buckets = 0
            uploaded_files = 0
            
            for bucket_config in self.buckets_config:
                bucket_name = bucket_config["name"]
                files_to_create = bucket_config["files"]
                
                try:
                    # Créer bucket s'il n'existe pas
                    if not self.minio_client.bucket_exists(bucket_name):
                        self.minio_client.make_bucket(bucket_name)
                        logger.info(f"   ✅ Bucket '{bucket_name}' créé")
                        created_buckets += 1
                    else:
                        logger.info(f"   ℹ️ Bucket '{bucket_name}' existe déjà")
                    
                    # Uploader fichiers d'exemple
                    for filename in files_to_create:
                        if filename in sample_data:
                            file_data = sample_data[filename]
                            
                            # Upload avec stream
                            self.minio_client.put_object(
                                bucket_name,
                                filename,
                                io.BytesIO(file_data),
                                len(file_data),
                                content_type=self._get_content_type(filename)
                            )
                            
                            logger.info(f"      📄 {filename} uploadé dans {bucket_name}")
                            uploaded_files += 1
                        else:
                            logger.warning(f"      ⚠️ Données pour {filename} non trouvées")
                
                except S3Error as e:
                    logger.error(f"   ❌ Erreur bucket {bucket_name}: {e}")
                except Exception as e:
                    logger.error(f"   ❌ Exception bucket {bucket_name}: {e}")
            
            logger.info(f"✅ {created_buckets} buckets créés, {uploaded_files} fichiers uploadés")
            return created_buckets > 0 or uploaded_files > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur création buckets: {e}")
            return False
    
    def _get_content_type(self, filename):
        """Déterminer le type de contenu"""
        if filename.endswith('.json'):
            return 'application/json'
        elif filename.endswith('.csv'):
            return 'text/csv'
        elif filename.endswith('.txt'):
            return 'text/plain'
        elif filename.endswith('.parquet'):
            return 'application/octet-stream'
        else:
            return 'application/octet-stream'
    
    def list_buckets_and_objects(self):
        """Lister buckets et objets"""
        logger.info("📋 Listing buckets MinIO...")
        
        if not hasattr(self, 'minio_client'):
            logger.error("❌ Client MinIO non connecté")
            return {}
        
        try:
            buckets_info = {}
            
            buckets = self.minio_client.list_buckets()
            
            for bucket in buckets:
                bucket_name = bucket.name
                logger.info(f"   🪣 {bucket_name} (créé: {bucket.creation_date})")
                
                # Lister objets dans le bucket
                objects = []
                try:
                    for obj in self.minio_client.list_objects(bucket_name, recursive=True):
                        objects.append({
                            'name': obj.object_name,
                            'size': obj.size,
                            'last_modified': obj.last_modified,
                            'etag': obj.etag
                        })
                        
                        size_mb = obj.size / 1024 / 1024 if obj.size > 0 else 0
                        logger.info(f"      📄 {obj.object_name} ({size_mb:.2f} MB)")
                    
                    buckets_info[bucket_name] = {
                        'creation_date': bucket.creation_date,
                        'objects': objects,
                        'total_objects': len(objects)
                    }
                    
                except Exception as e:
                    logger.warning(f"      ⚠️ Erreur listing objets: {e}")
                    buckets_info[bucket_name] = {'error': str(e)}
            
            return buckets_info
            
        except Exception as e:
            logger.error(f"❌ Erreur listing buckets: {e}")
            return {}
    
    def login_dremio(self):
        """Connexion Dremio pour créer source MinIO"""
        logger.info("🔐 Connexion Dremio...")
        
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({"userName": self.dremio_user, "password": self.dremio_pass})
        
        try:
            response = requests.post(f"{self.dremio_url}/apiv2/login", headers=headers, data=data, verify=False, timeout=10)
            
            if response.status_code == 200:
                token = response.json()['token']
                authorization_code = '_dremio' + token
                
                self.dremio_headers = {
                    'Authorization': authorization_code,
                    'Content-Type': 'application/json',
                }
                
                logger.info("✅ Connexion Dremio réussie")
                return True
            else:
                logger.error(f"❌ Connexion Dremio échouée: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion Dremio: {e}")
            return False
    
    def create_dremio_source(self):
        """Créer source MinIO dans Dremio"""
        logger.info("🔗 Création source MinIO dans Dremio...")
        
        if not self.dremio_headers:
            logger.error("❌ Non connecté à Dremio")
            return False
        
        source_config = {
            "entityType": "source",
            "name": "MinIO_DataLake",
            "description": "MinIO S3 Data Lake", 
            "type": "S3",
            "config": {
                "credentialType": "ACCESS_KEY",
                "accessKey": self.access_key,
                "accessSecret": self.secret_key,
                "secure": False,
                "externalBucketWhitelist": [],
                "enableAsync": True,
                "compatibilityMode": True,
                "pathStyleAccess": True,
                "endpoint": "localhost:9000",
                "enableSSL": False,
                "rootPath": "/"
            },
            "accelerationRefreshPeriod": 3600000,
            "accelerationGracePeriod": 10800000,
            "metadataPolicy": {
                "deleteUnavailableDatasets": True,
                "autoPromoteDatasets": False,
                "namesRefreshMillis": 3600000,
                "datasetDefinitionRefreshAfterMillis": 3600000,
                "datasetDefinitionExpireAfterMillis": 10800000,
                "authTTLMillis": 86400000,
                "updateMode": "PREFETCH_QUERIED"
            }
        }
        
        # Essayer plusieurs endpoints
        endpoints = [
            f"/api/v3/catalog/MinIO_DataLake",
            f"/apiv2/source/MinIO_DataLake"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.dremio_url}{endpoint}"
                
                response = requests.put(url, headers=self.dremio_headers, json=source_config, timeout=30)
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Source MinIO_DataLake créée via {endpoint}")
                    return True
                elif response.status_code == 409:
                    logger.info("ℹ️ Source MinIO_DataLake existe déjà")
                    return True
                else:
                    logger.debug(f"   {endpoint}: {response.status_code}")
                    
            except Exception as e:
                logger.debug(f"   {endpoint}: {e}")
                continue
        
        logger.warning("⚠️ Tous les endpoints ont échoué pour MinIO_DataLake")
        return False
    
    def create_minio_vds(self):
        """Créer VDS pour MinIO dans CustomDB_Analytics"""
        logger.info("🎯 Création VDS MinIO...")
        
        if not self.dremio_headers:
            logger.error("❌ Non connecté à Dremio")
            return False
        
        vds_definitions = [
            {
                "name": "vue_minio_customers",
                "sql": 'SELECT * FROM MinIO_DataLake."data-lake".customers',
                "context": ["CustomDB_Analytics"]
            },
            {
                "name": "vue_minio_products", 
                "sql": 'SELECT * FROM MinIO_DataLake."data-lake".products',
                "context": ["CustomDB_Analytics"]
            },
            {
                "name": "vue_minio_analytics",
                "sql": 'SELECT * FROM MinIO_DataLake.analytics."user_behavior"',
                "context": ["CustomDB_Analytics"]  
            }
        ]
        
        created_vds = []
        
        for vds_def in vds_definitions:
            name = vds_def["name"]
            sql = vds_def["sql"] 
            context = vds_def["context"]
            
            logger.info(f"   🎯 Création VDS {name}...")
            
            try:
                # Test SQL d'abord
                test_data = json.dumps({"sql": sql})
                test_response = requests.post(f"{self.dremio_url}/api/v3/sql", headers=self.dremio_headers, data=test_data, timeout=30)
                
                if test_response.status_code == 200:
                    # Créer VDS
                    create_sql = f'CREATE VDS {name} AS {sql}'
                    create_data = json.dumps({"sql": create_sql, "context": context})
                    
                    create_response = requests.post(f"{self.dremio_url}/api/v3/sql", headers=self.dremio_headers, data=create_data, timeout=30)
                    
                    if create_response.status_code == 200:
                        job_id = create_response.json().get('id')
                        
                        # Attendre completion
                        if self._wait_for_job_completion(job_id, name):
                            logger.info(f"      ✅ VDS {name} créée")
                            created_vds.append(name)
                        else:
                            logger.warning(f"      ⚠️ VDS {name} timeout")
                    else:
                        logger.warning(f"      ⚠️ CREATE VDS {name} échoué: {create_response.status_code}")
                else:
                    logger.warning(f"      ⚠️ Test SQL {name} échoué: {test_response.status_code}")
                
            except Exception as e:
                logger.error(f"      ❌ Exception VDS {name}: {e}")
        
        logger.info(f"✅ {len(created_vds)} VDS MinIO créées: {created_vds}")
        return created_vds
    
    def _wait_for_job_completion(self, job_id, job_name, max_wait=60):
        """Attendre completion job Dremio"""
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            try:
                response = requests.get(f"{self.dremio_url}/api/v3/job/{job_id}", headers=self.dremio_headers, timeout=10)
                
                if response.status_code == 200:
                    job_state = response.json().get('jobState')
                    
                    if job_state == 'COMPLETED':
                        return True
                    elif job_state in ['FAILED', 'CANCELLED']:
                        return False
                    else:
                        time.sleep(1)
                else:
                    time.sleep(1)
                    
            except Exception:
                time.sleep(1)
        
        return False
    
    def run_complete_minio_setup(self):
        """Setup complet MinIO"""
        logger.info("📦 SETUP COMPLET MINIO POUR DREMIO")
        logger.info("=" * 60)
        
        results = {
            "minio_status": False,
            "client_install": False,
            "client_connect": False,
            "buckets_created": False,
            "dremio_login": False,
            "dremio_source": False,
            "vds_created": False
        }
        
        # 1. Status MinIO
        logger.info("\n[1/7] Status MinIO...")
        minio_status = self.check_minio_status()
        results["minio_status"] = all("Accessible" in status for status in minio_status.values())
        
        if not results["minio_status"]:
            logger.error("❌ MinIO non accessible")
            return False
        
        # 2. Installation client
        logger.info("\n[2/7] Client MinIO...")
        results["client_install"] = self.install_minio_client()
        
        if not results["client_install"]:
            logger.error("❌ Installation client échouée")
            return False
        
        # 3. Connexion client
        logger.info("\n[3/7] Connexion client...")
        results["client_connect"] = self.connect_minio_client()
        
        if not results["client_connect"]:
            logger.error("❌ Connexion client échouée")
            return False
        
        # 4. Création buckets
        logger.info("\n[4/7] Buckets et fichiers...")
        results["buckets_created"] = self.create_buckets_and_upload()
        
        # 5. Listing buckets
        logger.info("\n[5/7] Listing MinIO...")
        buckets_info = self.list_buckets_and_objects()
        
        # 6. Connexion Dremio
        logger.info("\n[6/7] Connexion Dremio...")
        results["dremio_login"] = self.login_dremio()
        
        if results["dremio_login"]:
            # 7a. Source Dremio
            logger.info("\n[7a/7] Source Dremio...")
            results["dremio_source"] = self.create_dremio_source()
            
            # 7b. VDS MinIO
            logger.info("\n[7b/7] VDS MinIO...")
            created_vds = self.create_minio_vds()
            results["vds_created"] = len(created_vds) > 0
        
        # Résumé final
        success_count = sum(results.values())
        total_count = len(results)
        
        logger.info(f"\n🎊 RÉSULTATS MINIO")
        logger.info("=" * 60)
        logger.info(f"✅ Étapes réussies: {success_count}/{total_count}")
        
        for step, success in results.items():
            status = "✅" if success else "❌"
            step_name = step.replace("_", " ").title()
            logger.info(f"   {status} {step_name}")
        
        if success_count >= 5:
            logger.info(f"\n🎯 MINIO CONFIGURÉ!")
            logger.info("🌐 Console MinIO: http://localhost:9001")
            logger.info("🔑 Credentials: admin / admin123")
            
            if buckets_info:
                logger.info(f"\n📦 BUCKETS CRÉÉS:")
                for bucket_name, info in buckets_info.items():
                    obj_count = info.get('total_objects', 0)
                    logger.info(f"   🪣 {bucket_name}: {obj_count} fichiers")
            
            if results["dremio_source"]:
                logger.info(f"\n🔗 SOURCE DREMIO:")
                logger.info("   📊 MinIO_DataLake créée dans Dremio")
            
            if results["vds_created"]:
                logger.info(f"\n🎯 VDS MINIO:")
                logger.info("   📊 SELECT * FROM CustomDB_Analytics.vue_minio_customers")
                logger.info("   📊 SELECT * FROM CustomDB_Analytics.vue_minio_products")
            
            logger.info(f"\n✨ ACCÈS COMPLET:")
            logger.info("1. Console MinIO: http://localhost:9001")
            logger.info("2. Dremio UI: http://localhost:9047")
            logger.info("3. CustomDB_Analytics → VDS MinIO disponibles!")
            
            return True
        else:
            logger.warning("⚠️ Configuration MinIO partielle")
            return False

def main():
    """Fonction principale"""
    print("📦 Gestionnaire MinIO pour Dremio")
    
    try:
        manager = MinIOManager()
        success = manager.run_complete_minio_setup()
        
        if success:
            print("\n🎊 MINIO CONFIGURÉ AVEC SUCCÈS!")
            print("MinIO est maintenant intégré à Dremio avec des VDS!")
        else:
            print("\n❌ Configuration MinIO partielle")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        logger.debug(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)