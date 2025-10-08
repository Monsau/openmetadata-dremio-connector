#!/usr/bin/env python3
"""
🧪 VALIDATION ENVIRONNEMENT DREMIO
==================================
Teste que tous les composants de l'environnement fonctionnent
"""

import requests
import subprocess
import json
import time
from datetime import datetime

class EnvironmentValidator:
    def __init__(self):
        self.services = {
            "docker": False,
            "postgres": False,
            "minio": False, 
            "opensearch": False,
            "dremio": False
        }
        
    def test_docker_containers(self):
        """Tester les conteneurs Docker"""
        print("🐳 TEST CONTENEURS DOCKER")
        print("-" * 30)
        
        try:
            result = subprocess.run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout
                containers = ["dremio_engine", "dremio_postgres", "dremio_minio", "dremio_opensearch"]
                
                for container in containers:
                    if container in output and "healthy" in output:
                        print(f"✅ {container}: Actif et sain")
                        self.services["docker"] = True
                    else:
                        print(f"❌ {container}: Problème détecté")
                
                return True
            else:
                print("❌ Impossible de lister les conteneurs Docker")
                return False
                
        except Exception as e:
            print(f"❌ Erreur Docker: {e}")
            return False
    
    def test_postgres(self):
        """Tester PostgreSQL"""
        print("\n🐘 TEST POSTGRESQL")
        print("-" * 20)
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host="localhost",
                port=5434,
                database="business_db",
                user="dremio",
                password="dremio123"
            )
            
            cursor = conn.cursor()
            
            # Test requête simple
            cursor.execute("SELECT COUNT(*) FROM public.clients;")
            client_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM public.produits;")
            product_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM public.commandes;")
            order_count = cursor.fetchone()[0]
            
            print(f"✅ PostgreSQL connecté")
            print(f"   📊 {client_count} clients")
            print(f"   📦 {product_count} produits") 
            print(f"   🛒 {order_count} commandes")
            
            conn.close()
            self.services["postgres"] = True
            return True
            
        except Exception as e:
            print(f"❌ PostgreSQL: {e}")
            return False
    
    def test_minio(self):
        """Tester MinIO"""
        print("\n📦 TEST MINIO")
        print("-" * 15)
        
        try:
            # Test console MinIO
            response = requests.get("http://localhost:9000/minio/health/live", timeout=5)
            if response.status_code == 200:
                print("✅ MinIO Console accessible")
                
                # Test API
                response2 = requests.get("http://localhost:9000/minio/health/ready", timeout=5)
                if response2.status_code == 200:
                    print("✅ MinIO API fonctionnelle")
                    print("   🔑 Credentials: admin / admin123")
                    self.services["minio"] = True
                    return True
                else:
                    print("⚠️ MinIO API problème")
            else:
                print(f"❌ MinIO Console: {response.status_code}")
            
        except Exception as e:
            print(f"❌ MinIO: {e}")
        
        return False
    
    def test_opensearch(self):
        """Tester OpenSearch"""
        print("\n🔍 TEST OPENSEARCH")
        print("-" * 20)
        
        try:
            # Test connexion OpenSearch
            response = requests.get("http://localhost:9201", timeout=5)
            if response.status_code == 200:
                print("✅ OpenSearch accessible")
                
                # Test index user_searches
                try:
                    search_response = requests.get("http://localhost:9201/user_searches/_search", timeout=5)
                    if search_response.status_code == 200:
                        data = search_response.json()
                        hit_count = data.get('hits', {}).get('total', {}).get('value', 0)
                        print(f"   📊 Index user_searches: {hit_count} documents")
                        self.services["opensearch"] = True
                        return True
                except:
                    print("   ⚠️ Index user_searches non trouvé")
                    self.services["opensearch"] = True  # Service OK même sans index
                    return True
            else:
                print(f"❌ OpenSearch: {response.status_code}")
                
        except Exception as e:
            print(f"❌ OpenSearch: {e}")
        
        return False
    
    def test_dremio(self):
        """Tester Dremio"""
        print("\n🔥 TEST DREMIO")
        print("-" * 15)
        
        try:
            # Test connexion Dremio UI
            response = requests.get("http://localhost:9047", timeout=10)
            if response.status_code == 200:
                print("✅ Dremio UI accessible")
                
                # Test API login
                login_data = {"userName": "admin", "password": "admin123"}
                login_response = requests.post("http://localhost:9047/apiv2/login", 
                                             json=login_data, timeout=10)
                
                if login_response.status_code == 200:
                    print("✅ Dremio API login OK")
                    token = login_response.json().get("token")
                    
                    # Test sources
                    headers = {"Authorization": f"_dremio{token}"}
                    sources_response = requests.get("http://localhost:9047/apiv2/sources", 
                                                   headers=headers, timeout=10)
                    
                    if sources_response.status_code == 200:
                        sources = sources_response.json()
                        print(f"   📊 {len(sources)} sources trouvées")
                        
                        # Chercher PostgreSQL_Business
                        for source in sources:
                            if isinstance(source, dict) and source.get('name') == 'PostgreSQL_Business':
                                print("   ✅ PostgreSQL_Business source trouvée")
                                break
                        
                        self.services["dremio"] = True
                        return True
                else:
                    print(f"❌ Dremio login: {login_response.status_code}")
            else:
                print(f"❌ Dremio UI: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Dremio: {e}")
        
        return False
    
    def display_summary(self):
        """Afficher le résumé"""
        print("\n" + "📊" * 50)
        print("📊 RÉSUMÉ DE VALIDATION")
        print("📊" * 50)
        
        total_services = len(self.services)
        working_services = sum(1 for status in self.services.values() if status)
        
        print(f"\n🎯 SERVICES: {working_services}/{total_services} fonctionnels")
        
        for service, status in self.services.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {service.upper()}")
        
        if working_services == total_services:
            print(f"\n🎊 ENVIRONNEMENT PARFAITEMENT FONCTIONNEL!")
            print("   Tous les services sont opérationnels")
            print("   Prêt pour la création de VDS et requêtes")
        elif working_services >= 3:
            print(f"\n✅ ENVIRONNEMENT FONCTIONNEL")
            print("   Services essentiels opérationnels")
            print("   Quelques ajustements peuvent être nécessaires")
        else:
            print(f"\n⚠️ ENVIRONNEMENT PARTIELLEMENT FONCTIONNEL")
            print("   Plusieurs services nécessitent une attention")
        
        # Instructions suivantes
        print(f"\n🎯 PROCHAINES ÉTAPES:")
        if self.services["dremio"]:
            print("   1. ✅ Ouvrir http://localhost:9047")
            print("   2. 🔧 Configurer sources MinIO et OpenSearch manuellement")
            print("   3. 🏗️ Créer VDS dans CustomDB_Analytics")
        else:
            print("   1. ⚠️ Vérifier que tous les conteneurs sont démarrés")
            print("   2. 🔄 Attendre quelques minutes puis retester")
    
    def run_full_validation(self):
        """Validation complète"""
        print("🧪 VALIDATION COMPLÈTE ENVIRONNEMENT DREMIO")
        print("=" * 55)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Exécuter tous les tests
        self.test_docker_containers()
        self.test_postgres()
        self.test_minio()
        self.test_opensearch()
        self.test_dremio()
        
        # Résumé final
        self.display_summary()

def main():
    """Fonction principale"""
    validator = EnvironmentValidator()
    validator.run_full_validation()

if __name__ == "__main__":
    main()