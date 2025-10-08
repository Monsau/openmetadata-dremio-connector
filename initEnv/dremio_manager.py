#!/usr/bin/env python3
"""
🎯 ORCHESTRATEUR DREMIO - BACKUP, RESTORE, VALIDATE
==================================================
Script principal pour orchestrer les opérations de sauvegarde/restauration Dremio
"""

import sys
import os
import time
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.append(str(Path(__file__).parent))

def show_menu():
    """Afficher le menu principal"""
    print("\n" + "=" * 60)
    print("🎯 GESTIONNAIRE DREMIO - BACKUP & RESTORE")
    print("=" * 60)
    print("📋 SAUVEGARDES:")
    print("  1. Créer une sauvegarde complète")
    print("  2. Lister les sauvegardes existantes")
    print()
    print("🔄 RESTAURATIONS:")
    print("  3. Restauration complète (dernière sauvegarde)")
    print("  4. Restauration complète (choisir sauvegarde)")
    print("  5. Restaurer seulement les sources")
    print("  6. Restaurer seulement les espaces")
    print("  7. Restaurer seulement les VDS")
    print()
    print("✅ VALIDATION:")
    print("  8. Valider l'environnement actuel")
    print("  9. Valider contre une sauvegarde")
    print()
    print("🔧 OUTILS:")
    print("  10. Test de connexion Dremio")
    print("  11. Afficher l'aide détaillée")
    print()
    print("  0. Quitter")
    print()

def run_backup():
    """Exécuter une sauvegarde"""
    print("\n🔄 Lancement de la sauvegarde complète...")
    result = os.system("python dremio_backup_restore.py backup")
    
    if result == 0:
        print("✅ Sauvegarde terminée avec succès")
        
        # Proposer validation immédiate
        validate = input("\n🔍 Voulez-vous valider la sauvegarde ? (o/N): ").lower().strip()
        if validate in ['o', 'oui', 'y', 'yes']:
            run_validation()
    else:
        print("❌ Erreur lors de la sauvegarde")

def list_backups():
    """Lister les sauvegardes disponibles"""
    print("\n📋 Sauvegardes disponibles:")
    result = os.system("python dremio_backup_restore.py list")
    return result == 0

def run_full_restore(backup_file=None):
    """Exécuter une restauration complète"""
    if backup_file:
        cmd = f"python dremio_backup_restore.py restore {backup_file}"
        print(f"\n🔄 Restauration depuis: {backup_file}")
    else:
        cmd = "python dremio_backup_restore.py restore"
        print("\n🔄 Restauration depuis la sauvegarde la plus récente...")
    
    result = os.system(cmd)
    
    if result == 0:
        print("✅ Restauration terminée avec succès")
        
        # Validation post-restauration
        print("\n⏳ Attente de 10 secondes pour stabilisation...")
        time.sleep(10)
        
        validate = input("🔍 Voulez-vous valider la restauration ? (O/n): ").lower().strip()
        if validate not in ['n', 'non', 'no']:
            run_validation(backup_file)
    else:
        print("❌ Erreur lors de la restauration")

def run_selective_restore(component):
    """Exécuter une restauration sélective"""
    component_names = {
        'sources': 'sources de données',
        'spaces': 'espaces',
        'vds': 'VDS'
    }
    
    print(f"\n🔄 Restauration des {component_names.get(component, component)}...")
    result = os.system(f"python dremio_backup_restore.py restore-{component}")
    
    if result == 0:
        print(f"✅ Restauration des {component_names.get(component, component)} réussie")
    else:
        print(f"❌ Erreur lors de la restauration des {component_names.get(component, component)}")

def run_validation(backup_file=None):
    """Exécuter la validation"""
    if backup_file:
        cmd = f"python validate_restoration.py {backup_file}"
        print(f"\n✅ Validation contre: {backup_file}")
    else:
        cmd = "python validate_restoration.py"
        print("\n✅ Validation de l'environnement actuel...")
    
    result = os.system(cmd)
    
    if result == 0:
        print("✅ Validation réussie - Environnement opérationnel")
    else:
        print("⚠️ Validation avec avertissements - Consultez le rapport")

def test_connection():
    """Tester la connexion Dremio"""
    print("\n🔍 Test de connexion à Dremio...")
    
    try:
        from dremio_backup_restore import DremioBackupRestore
        
        backup_restore = DremioBackupRestore()
        if backup_restore.login():
            print("✅ Connexion Dremio réussie")
            
            # Informations basiques
            sources = backup_restore.get_sources()
            spaces = backup_restore.get_spaces()
            
            print(f"📊 État actuel:")
            print(f"   - Sources: {len(sources)}")
            print(f"   - Espaces: {len(spaces)}")
            
            return True
        else:
            print("❌ Échec de connexion à Dremio")
            return False
            
    except ImportError:
        print("❌ Module dremio_backup_restore non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def choose_backup_file():
    """Permettre à l'utilisateur de choisir un fichier de sauvegarde"""
    backup_root = Path("backup")
    if not backup_root.exists():
        print("❌ Aucun dossier de sauvegarde trouvé")
        return None
    
    backups = []
    for backup_dir in backup_root.iterdir():
        if backup_dir.is_dir():
            backup_file = backup_dir / "dremio_backup.json"
            if backup_file.exists():
                backups.append({
                    'path': str(backup_file),
                    'date': backup_dir.name,
                    'dir': backup_dir
                })
    
    if not backups:
        print("❌ Aucune sauvegarde trouvée")
        return None
    
    backups.sort(key=lambda x: x['date'], reverse=True)
    
    print("\n📋 Sauvegardes disponibles:")
    for i, backup in enumerate(backups, 1):
        print(f"  {i}. {backup['date']}")
    
    try:
        choice = int(input(f"\nChoisissez une sauvegarde (1-{len(backups)}): ")) - 1
        if 0 <= choice < len(backups):
            return backups[choice]['path']
        else:
            print("❌ Choix invalide")
            return None
    except ValueError:
        print("❌ Choix invalide")
        return None

def show_help():
    """Afficher l'aide détaillée"""
    print("\n📖 AIDE DÉTAILLÉE")
    print("=" * 50)
    print()
    print("🔄 SAUVEGARDE:")
    print("  - Sauvegarde complète des sources, espaces et VDS")
    print("  - Génération automatique d'un horodatage")
    print("  - Format JSON + résumé Markdown")
    print()
    print("🔄 RESTAURATION:")
    print("  - Restauration complète ou sélective")
    print("  - Choix de la sauvegarde source")
    print("  - Validation automatique proposée")
    print()
    print("✅ VALIDATION:")
    print("  - Test de connexion des sources")
    print("  - Vérification de la présence des espaces et VDS")
    print("  - Génération d'un rapport détaillé")
    print()
    print("📂 STRUCTURE DES FICHIERS:")
    print("  backup/YYYYMMDD_HHMMSS/")
    print("    ├── dremio_backup.json")
    print("    └── backup_summary.md")
    print()
    print("🔧 CONFIGURATION:")
    print("  - Serveur Dremio: localhost:9047")
    print("  - Identifiants: admin/admin123")
    print("  - Timeout: 30-60 secondes")

def main():
    """Fonction principale"""
    
    print("🎯 GESTIONNAIRE DREMIO - Initialisation...")
    
    # Vérifier la présence des scripts requis
    required_scripts = [
        "dremio_backup_restore.py",
        "validate_restoration.py"
    ]
    
    missing_scripts = []
    for script in required_scripts:
        if not Path(script).exists():
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"❌ Scripts manquants: {', '.join(missing_scripts)}")
        print("Assurez-vous que tous les scripts sont présents dans le même dossier.")
        return
    
    # Test de connexion initial
    print("🔍 Test de connexion initial...")
    connection_ok = test_connection()
    
    if not connection_ok:
        print("\n⚠️ ATTENTION: Connexion Dremio impossible")
        print("Vérifiez que Dremio est démarré et accessible sur localhost:9047")
        
        continue_anyway = input("\nContinuer quand même ? (o/N): ").lower().strip()
        if continue_anyway not in ['o', 'oui', 'y', 'yes']:
            return
    
    # Boucle principale du menu
    while True:
        try:
            show_menu()
            choice = input("Votre choix (0-11): ").strip()
            
            if choice == "0":
                print("👋 Au revoir !")
                break
                
            elif choice == "1":
                run_backup()
                
            elif choice == "2":
                list_backups()
                
            elif choice == "3":
                run_full_restore()
                
            elif choice == "4":
                backup_file = choose_backup_file()
                if backup_file:
                    run_full_restore(backup_file)
                    
            elif choice == "5":
                run_selective_restore("sources")
                
            elif choice == "6":
                run_selective_restore("spaces")
                
            elif choice == "7":
                run_selective_restore("vds")
                
            elif choice == "8":
                run_validation()
                
            elif choice == "9":
                backup_file = choose_backup_file()
                if backup_file:
                    run_validation(backup_file)
                    
            elif choice == "10":
                test_connection()
                
            elif choice == "11":
                show_help()
                
            else:
                print("❌ Choix invalide")
                
        except KeyboardInterrupt:
            print("\n👋 Interruption utilisateur, au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            
        # Pause avant de continuer
        if choice != "0":
            input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()