#!/usr/bin/env python3
"""
🚀 SCRIPT DE DÉMARRAGE COMPLET - ENVIRONNEMENT DREMIO
====================================================
Lance l'infrastructure complète et configure les sources
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_command(command, description, check_success=True):
    """Exécuter une commande avec gestion d'erreurs"""
    print(f"\n🔧 {description}...")
    
    try:
        if isinstance(command, list):
            result = subprocess.run(command, check=check_success, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=check_success, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCÈS")
            return True
        else:
            print(f"❌ {description} - ÉCHEC")
            if result.stderr:
                print(f"   Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERREUR: {e}")
        return False

def check_docker_running():
    """Vérifier que Docker est en marche"""
    print("🐳 Vérification Docker...")
    
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker est actif")
            return True
        else:
            print("❌ Docker n'est pas accessible")
            return False
    except Exception as e:
        print(f"❌ Erreur Docker: {e}")
        return False

def start_infrastructure():
    """Démarrer l'infrastructure Docker"""
    print("\n🏗️ DÉMARRAGE INFRASTRUCTURE DOCKER")
    print("=" * 50)
    
    # Aller dans le dossier env
    env_dir = Path(__file__).parent / "env"
    if not env_dir.exists():
        print("❌ Dossier env/ non trouvé")
        return False
    
    os.chdir(env_dir)
    
    # Démarrer les conteneurs
    if not run_command("docker-compose up -d", "Démarrage des conteneurs"):
        return False
    
    # Attendre que les conteneurs soient sains
    print("\n⏳ Attente que les conteneurs soient sains...")
    for i in range(12):  # 2 minutes max
        time.sleep(10)
        result = subprocess.run(["docker-compose", "ps"], capture_output=True, text=True)
        if "healthy" in result.stdout and result.stdout.count("healthy") >= 3:
            print("✅ Tous les conteneurs sont sains")
            return True
        print(f"   Vérification {i+1}/12...")
    
    print("⚠️ Certains conteneurs peuvent ne pas être complètement sains")
    return True

def setup_python_env():
    """Configurer l'environnement Python"""
    print("\n🐍 CONFIGURATION ENVIRONNEMENT PYTHON")
    print("=" * 50)
    
    # Retour au dossier principal
    os.chdir(Path(__file__).parent)
    
    # Vérifier requirements.txt
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt non trouvé")
        return False
    
    # Installer les dépendances
    return run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      "Installation des dépendances Python")

def configure_dremio():
    """Configurer Dremio avec les sources"""
    print("\n🔥 CONFIGURATION DREMIO")
    print("=" * 50)
    
    # Attendre que Dremio soit prêt
    print("⏳ Attente que Dremio soit prêt...")
    time.sleep(30)
    
    # Exécuter le script de configuration
    if Path("create_sources_rest_api.py").exists():
        return run_command([sys.executable, "create_sources_rest_api.py"], 
                          "Configuration des sources Dremio", check_success=False)
    else:
        print("⚠️ Script de configuration non trouvé")
        return False

def display_final_status():
    """Afficher le statut final"""
    print("\n" + "🎊" * 50)
    print("🎊 ENVIRONNEMENT DREMIO DÉMARRÉ!")
    print("🎊" * 50)
    
    print(f"\n✅ SERVICES DISPONIBLES:")
    print("   🐘 PostgreSQL: localhost:5434 (dremio/dremio123)")
    print("   📦 MinIO Console: http://localhost:9000 (admin/admin123)")
    print("   🔍 OpenSearch: localhost:9201")
    print("   🔥 Dremio UI: http://localhost:9047 (admin/admin123)")
    
    print(f"\n🎯 PROCHAINES ÉTAPES:")
    print("   1. Ouvrir http://localhost:9047")
    print("   2. Configurer sources MinIO et OpenSearch manuellement")
    print("   3. Créer VDS dans CustomDB_Analytics")
    print("   4. Utiliser VDS comme des vues SQL")
    
    print(f"\n📋 EXEMPLE VDS:")
    print("   CREATE VIEW CustomDB_Analytics.vue_clients AS")
    print("   SELECT * FROM PostgreSQL_Business.business_db.public.clients;")

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE AUTOMATIQUE ENVIRONNEMENT DREMIO")
    print("=" * 60)
    print("Architecture: PostgreSQL + MinIO + OpenSearch + Dremio OSS 26")
    print("=" * 60)
    
    # 1. Vérifier Docker
    if not check_docker_running():
        print("\n❌ ÉCHEC: Docker requis")
        return False
    
    # 2. Démarrer infrastructure
    if not start_infrastructure():
        print("\n❌ ÉCHEC: Infrastructure Docker")
        return False
    
    # 3. Configurer Python
    if not setup_python_env():
        print("\n⚠️ AVERTISSEMENT: Problème environnement Python")
    
    # 4. Configurer Dremio
    configure_dremio()  # Non-bloquant
    
    # 5. Statut final
    display_final_status()
    
    print(f"\n🎊 ENVIRONNEMENT PRÊT!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)