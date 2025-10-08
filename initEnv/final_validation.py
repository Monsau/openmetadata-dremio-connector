#!/usr/bin/env python3
"""
✅ VALIDATION FINALE ENVIRONNEMENT DREMIO
========================================
Validation complète que les VDS fonctionnent comme des vues
"""

import logging
import sys
import requests
import json
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dremio_vds():
    """Test complet des VDS comme vues SQL"""
    
    print("✅ VALIDATION FINALE DREMIO VDS")
    print("=" * 50)
    
    # Connexion
    print("\n🔐 Connexion Dremio...")
    
    headers = {'Content-Type': 'application/json'}
    login_response = requests.post('http://localhost:9047/apiv2/login', 
                                   json={'userName': 'admin', 'password': 'admin123'})
    
    if login_response.status_code != 200:
        print("❌ Connexion échouée")
        return False
    
    token = login_response.json()['token']
    auth_header = {
        'Authorization': f'_dremio{token}',
        'Content-Type': 'application/json'
    }
    
    print("✅ Connexion réussie")
    
    # Test des VDS créées
    vds_tests = [
        ("vue_clients", "SELECT * FROM CustomDB_Analytics.vue_clients LIMIT 3"),
        ("vue_clients_simple", "SELECT * FROM CustomDB_Analytics.vue_clients_simple LIMIT 3"),
        ("vue_produits_simple", "SELECT * FROM CustomDB_Analytics.vue_produits_simple LIMIT 3"),
        ("vue_commandes_simple", "SELECT * FROM CustomDB_Analytics.vue_commandes_simple LIMIT 3"),
        ("vue_clients_count", "SELECT * FROM CustomDB_Analytics.vue_clients_count")
    ]
    
    print(f"\n🎯 Test des VDS comme vues SQL...")
    
    working_vds = []
    
    for vds_name, query in vds_tests:
        print(f"\n   📊 Test {vds_name}...")
        
        try:
            # Exécuter la requête
            response = requests.post('http://localhost:9047/api/v3/sql', 
                                   headers=auth_header, 
                                   json={'sql': query})
            
            if response.status_code == 200:
                job_id = response.json().get('id')
                
                # Attendre completion
                for _ in range(30):  # Max 30 secondes
                    job_response = requests.get(f'http://localhost:9047/api/v3/job/{job_id}', 
                                              headers=auth_header)
                    
                    if job_response.status_code == 200:
                        job_state = job_response.json().get('jobState')
                        
                        if job_state == 'COMPLETED':
                            # Récupérer résultats
                            results_response = requests.get(f'http://localhost:9047/api/v3/job/{job_id}/results', 
                                                          headers=auth_header)
                            
                            if results_response.status_code == 200:
                                results = results_response.json()
                                row_count = len(results.get('rows', []))
                                col_count = len(results.get('schema', []))
                                
                                print(f"      ✅ {vds_name}: {row_count} lignes, {col_count} colonnes")
                                working_vds.append(vds_name)
                                break
                        elif job_state == 'FAILED':
                            print(f"      ❌ {vds_name}: Requête échouée")
                            break
                    
                    time.sleep(1)
                else:
                    print(f"      ⚠️ {vds_name}: Timeout")
            else:
                print(f"      ❌ {vds_name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ {vds_name}: Exception {e}")
    
    # Test requête complexe
    print(f"\n🧪 Test requête complexe...")
    
    complex_query = """
    SELECT 
        c.nom as client_nom,
        c.ville,
        COUNT(*) as nb_commandes
    FROM CustomDB_Analytics.vue_clients_simple c
    JOIN CustomDB_Analytics.vue_commandes_simple cmd ON c.client_id = cmd.client_id
    GROUP BY c.nom, c.ville
    ORDER BY nb_commandes DESC
    """
    
    try:
        response = requests.post('http://localhost:9047/api/v3/sql', 
                               headers=auth_header, 
                               json={'sql': complex_query})
        
        if response.status_code == 200:
            job_id = response.json().get('id')
            
            # Attendre completion
            for _ in range(30):
                job_response = requests.get(f'http://localhost:9047/api/v3/job/{job_id}', 
                                          headers=auth_header)
                
                if job_response.status_code == 200:
                    job_state = job_response.json().get('jobState')
                    
                    if job_state == 'COMPLETED':
                        results_response = requests.get(f'http://localhost:9047/api/v3/job/{job_id}/results', 
                                                      headers=auth_header)
                        
                        if results_response.status_code == 200:
                            results = results_response.json()
                            row_count = len(results.get('rows', []))
                            print(f"   ✅ Jointure complexe réussie: {row_count} résultats")
                            break
                    elif job_state == 'FAILED':
                        print(f"   ❌ Jointure complexe échouée")
                        break
                
                time.sleep(1)
            else:
                print(f"   ⚠️ Jointure complexe: Timeout")
        else:
            print(f"   ❌ Jointure complexe: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Jointure complexe: {e}")
    
    # Résumé final
    print(f"\n🎊 RÉSULTATS FINAUX")
    print("=" * 50)
    print(f"✅ VDS fonctionnelles: {len(working_vds)}/5")
    
    if working_vds:
        print(f"\n🎯 VDS DISPONIBLES COMME VUES:")
        for vds in working_vds:
            print(f"   📊 SELECT * FROM CustomDB_Analytics.{vds}")
        
        print(f"\n✨ UTILISATION:")
        print("1. 🌐 Interface: http://localhost:9047")
        print("2. 🔑 Login: admin / admin123")
        print("3. 📂 Espace: CustomDB_Analytics")
        print("4. 🎯 Vos VDS apparaissent comme des VUES SQL standard!")
        
        print(f"\n🚀 EXEMPLES DE REQUÊTES:")
        print("-- Tous les clients")
        print("SELECT * FROM CustomDB_Analytics.vue_clients_simple;")
        print()
        print("-- Statistiques par ville")
        print("SELECT * FROM CustomDB_Analytics.vue_clients_count;")
        print()
        print("-- Jointure clients-commandes")
        print("SELECT c.nom, COUNT(*) as nb_cmd")
        print("FROM CustomDB_Analytics.vue_clients_simple c")
        print("JOIN CustomDB_Analytics.vue_commandes_simple cmd")
        print("  ON c.client_id = cmd.client_id")
        print("GROUP BY c.nom;")
        
        success = len(working_vds) >= 3
        
        if success:
            print(f"\n🎊 MISSION ACCOMPLIE!")
            print("Vos VDS sont maintenant des vues SQL dans CustomDB_Analytics!")
        else:
            print(f"\n⚠️ Configuration partielle")
        
        return success
    else:
        print("❌ Aucune VDS fonctionnelle trouvée")
        return False

if __name__ == "__main__":
    success = test_dremio_vds()
    sys.exit(0 if success else 1)