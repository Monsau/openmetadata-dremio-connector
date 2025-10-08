#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Setup pour l'ingestion Dremio → OpenMetadata
=====================================================

Ce script facilite la configuration initiale de l'environnement d'ingestion.
Il vérifie les prérequis, aide à la configuration et teste les connexions.

Utilisation:
    python setup_ingestion.py
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """Affiche la bannière du setup"""
    print("=" * 60)
    print(" SETUP DREMIO TO OPENMETADATA INGESTION")
    print("=" * 60)
    print()


def check_python_version():
    """Vérifie la version Python"""
    print("🐍 Vérification de la version Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis. Version actuelle:", sys.version)
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    return True


def install_dependencies():
    """Installe les dépendances"""
    print("\n📦 Installation des dépendances...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation des dépendances: {e}")
        return False


def setup_environment_file():
    """Configure le fichier d'environnement"""
    print("\n🔧 Configuration de l'environnement...")
    
    env_file = Path(".env")
    template_file = Path(".env.template")
    
    if env_file.exists():
        print("✅ Fichier .env existe déjà")
        return True
    
    if not template_file.exists():
        print("❌ Fichier .env.template non trouvé")
        return False
    
    # Copie du template
    import shutil
    shutil.copy(template_file, env_file)
    print(f"✅ Fichier .env créé depuis le template")
    
    print("\n🔧 Veuillez maintenant éditer le fichier .env avec vos paramètres:")
    print("   - DREMIO_HOST, DREMIO_PORT, DREMIO_USERNAME, DREMIO_PASSWORD")
    print("   - OPENMETADATA_HOST, OPENMETADATA_PORT, OPENMETADATA_JWT_TOKEN")
    
    return True


def test_configuration():
    """Teste la configuration"""
    print("\n🧪 Test de la configuration...")
    
    # Vérification des variables d'environnement requises
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'DREMIO_HOST', 'DREMIO_PORT', 'DREMIO_USERNAME', 'DREMIO_PASSWORD',
        'OPENMETADATA_HOST', 'OPENMETADATA_PORT', 'OPENMETADATA_JWT_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables manquantes dans .env: {', '.join(missing_vars)}")
        print("   Veuillez éditer le fichier .env et relancer ce script")
        return False
    
    print("✅ Toutes les variables d'environnement sont configurées")
    
    # Test des connexions
    print("\n🔗 Test des connexions...")
    try:
        result = subprocess.run([
            sys.executable, "dremio_ingestion_clean.py", "--mode", "dry-run"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Test des connexions réussi")
            return True
        else:
            print("❌ Test des connexions échoué")
            print("Sortie d'erreur:", result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ Script dremio_ingestion_clean.py non trouvé")
        return False


def show_next_steps():
    """Affiche les prochaines étapes"""
    print("\n🎉 SETUP TERMINÉ!")
    print("\nPROCHAINES ÉTAPES:")
    print("\n1. 🧪 Tester l'ingestion:")
    print("   python dremio_ingestion_clean.py --mode test")
    print("\n2. 🚀 Lancer l'ingestion complète:")
    print("   python dremio_ingestion_clean.py --mode ingestion")
    print("\n3. 🌐 Vérifier dans OpenMetadata:")
    print("   Naviguer vers http://localhost:8585 (ou votre instance)")
    print("   Aller dans: Databases > dremio-custom-service")
    
    print("\n📚 DOCUMENTATION:")
    print("   Consultez README_CLEAN.md pour les détails complets")
    
    print("\n🆘 AIDE:")
    print("   En cas de problème, vérifiez les logs dans dremio_ingestion.log")
    print()


def main():
    """Fonction principale du setup"""
    print_banner()
    
    # Vérifications et configuration
    steps = [
        ("Vérification Python", check_python_version),
        ("Installation dépendances", install_dependencies),
        ("Configuration environnement", setup_environment_file),
        ("Test configuration", test_configuration)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ ÉCHEC DE L'ÉTAPE: {step_name}")
            print("Veuillez corriger les erreurs et relancer le setup.")
            return 1
    
    show_next_steps()
    return 0


if __name__ == "__main__":
    sys.exit(main())