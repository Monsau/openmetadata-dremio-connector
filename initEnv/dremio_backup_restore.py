#!/usr/bin/env python3
"""
🔄 DREMIO BACKUP & RESTORE - SOURCES ET VDS
===========================================
Script pour sauvegarder et restaurer les sources de données et VDS de Dremio.
Permet de récupérer la configuration complète d'un environnement Dremio.

Fonctionnalités :
- Sauvegarde de toutes les sources de données (PostgreSQL, MinIO, etc.)
- Sauvegarde de tous les VDS et leurs requêtes SQL
- Sauvegarde des espaces (Spaces) et dossiers
- Restauration complète de la configuration
- Export en JSON pour versioning
"""

import logging
import sys
import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DremioBackupRestore:
    """Gestionnaire de sauvegarde et restauration Dremio"""
    
    def __init__(self, host="localhost", port=9047, username="admin", password="admin123"):
        self.base_url = f"http://{host}:{port}"
        self.username = username
        self.password = password
        
        self.session = requests.Session()
        self.token = None
        self.backup_dir = Path("backup") / datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def login(self):
        """Connexion à Dremio"""
        logger.info("🔐 Connexion à Dremio...")
        
        login_url = f"{self.base_url}/apiv2/login"
        login_data = {
            "userName": self.username,
            "password": self.password
        }
        
        try:
            response = self.session.post(login_url, json=login_data, timeout=30)
            
            if response.status_code == 200:
                self.token = response.json().get('token')
                self.session.headers.update({'Authorization': f'_dremio{self.token}'})
                logger.info("✅ Connexion réussie")
                return True
            else:
                logger.error(f"❌ Échec connexion: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False
    
    def get_sources(self):
        """Récupérer toutes les sources de données"""
        logger.info("📋 Récupération des sources...")
        
        try:
            url = f"{self.base_url}/api/v3/source"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                sources = response.json().get('data', [])
                logger.info(f"✅ {len(sources)} sources trouvées")
                return sources
            else:
                logger.error(f"❌ Erreur récupération sources: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur get_sources: {e}")
            return []
    
    def get_source_details(self, source_id):
        """Récupérer les détails d'une source spécifique"""
        try:
            url = f"{self.base_url}/api/v3/source/{source_id}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ Erreur détails source {source_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur get_source_details {source_id}: {e}")
            return None
    
    def get_spaces(self):
        """Récupérer tous les espaces (Spaces)"""
        logger.info("📂 Récupération des espaces...")
        
        try:
            url = f"{self.base_url}/api/v3/space"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                spaces = response.json().get('data', [])
                logger.info(f"✅ {len(spaces)} espaces trouvés")
                return spaces
            else:
                logger.error(f"❌ Erreur récupération espaces: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erreur get_spaces: {e}")
            return []
    
    def get_datasets_in_path(self, path):
        """Récupérer tous les datasets dans un chemin donné"""
        try:
            # Encoder le chemin pour l'URL
            encoded_path = "/".join(path)
            url = f"{self.base_url}/api/v3/catalog/{encoded_path}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                catalog_data = response.json()
                return catalog_data.get('children', [])
            else:
                return []
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur récupération datasets {path}: {e}")
            return []
    
    def get_dataset_details(self, dataset_id):
        """Récupérer les détails d'un dataset (incluant la requête SQL pour les VDS)"""
        try:
            url = f"{self.base_url}/api/v3/catalog/{dataset_id}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur détails dataset {dataset_id}: {e}")
            return None
    
    def backup_all(self):
        """Sauvegarde complète de l'environnement Dremio"""
        logger.info("🔄 Début de la sauvegarde complète...")
        
        if not self.login():
            logger.error("❌ Impossible de se connecter à Dremio")
            return False
        
        # Créer le dossier de sauvegarde
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "dremio_url": self.base_url,
            "sources": [],
            "spaces": [],
            "datasets": []
        }
        
        # 1. Sauvegarder les sources
        logger.info("1️⃣ Sauvegarde des sources...")
        sources = self.get_sources()
        for source in sources:
            source_details = self.get_source_details(source['id'])
            if source_details:
                backup_data['sources'].append(source_details)
        
        # 2. Sauvegarder les espaces
        logger.info("2️⃣ Sauvegarde des espaces...")
        spaces = self.get_spaces()
        backup_data['spaces'] = spaces
        
        # 3. Sauvegarder les datasets dans chaque espace
        logger.info("3️⃣ Sauvegarde des datasets et VDS...")
        for space in spaces:
            space_name = space['name']
            logger.info(f"   📂 Analyse espace: {space_name}")
            
            datasets_in_space = self.get_datasets_in_path([space_name])
            for dataset in datasets_in_space:
                if dataset.get('type') in ['VIRTUAL_DATASET', 'PHYSICAL_DATASET']:
                    dataset_details = self.get_dataset_details(dataset['id'])
                    if dataset_details:
                        backup_data['datasets'].append(dataset_details)
        
        # Sauvegarder en JSON
        backup_file = self.backup_dir / "dremio_backup.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        # Créer un résumé lisible
        summary_file = self.backup_dir / "backup_summary.md"
        self.create_backup_summary(backup_data, summary_file)
        
        logger.info(f"✅ Sauvegarde terminée dans: {self.backup_dir}")
        logger.info(f"📊 Résumé: {len(backup_data['sources'])} sources, {len(backup_data['spaces'])} espaces, {len(backup_data['datasets'])} datasets")
        
        return True
    
    def create_backup_summary(self, backup_data, summary_file):
        """Créer un fichier résumé lisible de la sauvegarde"""
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Sauvegarde Dremio - {backup_data['timestamp']}\n\n")
            
            f.write("## Sources de données\n\n")
            for source in backup_data['sources']:
                f.write(f"- **{source['name']}** ({source['type']})\n")
                if 'config' in source and source['config']:
                    config = source['config']
                    if 'hostname' in config:
                        f.write(f"  - Host: {config.get('hostname', 'N/A')}\n")
                    if 'port' in config:
                        f.write(f"  - Port: {config.get('port', 'N/A')}\n")
                f.write("\n")
            
            f.write("## Espaces\n\n")
            for space in backup_data['spaces']:
                f.write(f"- **{space['name']}**\n")
            f.write("\n")
            
            f.write("## Datasets et VDS\n\n")
            for dataset in backup_data['datasets']:
                f.write(f"- **{dataset['path'][-1]}** ({dataset['type']})\n")
                if dataset['type'] == 'VIRTUAL_DATASET' and 'sql' in dataset:
                    f.write(f"  - SQL: `{dataset['sql'][:100]}...`\n")
                f.write("\n")
    
    def restore_sources(self, backup_file):
        """Restaurer les sources depuis un fichier de sauvegarde"""
        logger.info("🔄 Restauration des sources...")
        
        if not self.login():
            logger.error("❌ Impossible de se connecter à Dremio")
            return False
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            created_count = 0
            for source_data in backup_data['sources']:
                if self.create_source(source_data):
                    created_count += 1
                time.sleep(2)  # Pause entre les créations
            
            logger.info(f"✅ {created_count}/{len(backup_data['sources'])} sources restaurées")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur restauration sources: {e}")
            return False
    
    def create_source(self, source_data):
        """Créer une source de données"""
        try:
            # Nettoyer les données pour la création (enlever les IDs, etc.)
            clean_source = {
                'name': source_data['name'],
                'type': source_data['type'],
                'config': source_data.get('config', {})
            }
            
            url = f"{self.base_url}/api/v3/source"
            response = self.session.post(url, json=clean_source, timeout=30)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Source créée: {clean_source['name']}")
                return True
            else:
                logger.warning(f"⚠️ Erreur création source {clean_source['name']}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur create_source: {e}")
            return False
    
    def restore_spaces(self, backup_file):
        """Restaurer les espaces depuis un fichier de sauvegarde"""
        logger.info("🔄 Restauration des espaces...")
        
        if not self.login():
            return False
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            created_count = 0
            for space_data in backup_data['spaces']:
                if self.create_space(space_data):
                    created_count += 1
                time.sleep(1)
            
            logger.info(f"✅ {created_count}/{len(backup_data['spaces'])} espaces restaurés")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur restauration espaces: {e}")
            return False
    
    def create_space(self, space_data):
        """Créer un espace"""
        try:
            clean_space = {
                'name': space_data['name']
            }
            
            url = f"{self.base_url}/api/v3/space"
            response = self.session.post(url, json=clean_space, timeout=30)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Espace créé: {clean_space['name']}")
                return True
            else:
                logger.warning(f"⚠️ Erreur création espace {clean_space['name']}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur create_space: {e}")
            return False
    
    def restore_datasets(self, backup_file):
        """Restaurer les datasets et VDS depuis un fichier de sauvegarde"""
        logger.info("🔄 Restauration des datasets et VDS...")
        
        if not self.login():
            return False
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            created_count = 0
            for dataset_data in backup_data['datasets']:
                if dataset_data['type'] == 'VIRTUAL_DATASET':
                    if self.create_vds(dataset_data):
                        created_count += 1
                    time.sleep(2)
            
            logger.info(f"✅ {created_count} VDS restaurés")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur restauration datasets: {e}")
            return False
    
    def create_vds(self, vds_data):
        """Créer un Virtual Dataset"""
        try:
            if 'sql' not in vds_data:
                logger.warning(f"⚠️ Pas de SQL pour VDS: {vds_data.get('path', 'Unknown')}")
                return False
            
            vds_payload = {
                'path': vds_data['path'],
                'sql': vds_data['sql'],
                'sqlContext': vds_data.get('sqlContext', [])
            }
            
            url = f"{self.base_url}/api/v3/dataset"
            response = self.session.post(url, json=vds_payload, timeout=30)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ VDS créé: {'/'.join(vds_data['path'])}")
                return True
            else:
                logger.warning(f"⚠️ Erreur création VDS: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur create_vds: {e}")
            return False
    
    def list_available_backups(self):
        """Lister les sauvegardes disponibles"""
        backup_root = Path("backup")
        if not backup_root.exists():
            logger.info("📂 Aucun dossier de sauvegarde trouvé")
            return []
        
        backups = []
        for backup_dir in backup_root.iterdir():
            if backup_dir.is_dir():
                backup_file = backup_dir / "dremio_backup.json"
                if backup_file.exists():
                    backups.append({
                        'path': backup_file,
                        'date': backup_dir.name,
                        'dir': backup_dir
                    })
        
        backups.sort(key=lambda x: x['date'], reverse=True)
        return backups

def main():
    """Interface en ligne de commande"""
    if len(sys.argv) < 2:
        print("🔄 DREMIO BACKUP & RESTORE")
        print("Usage:")
        print("  python dremio_backup_restore.py backup")
        print("  python dremio_backup_restore.py restore [backup_file]")
        print("  python dremio_backup_restore.py list")
        print("  python dremio_backup_restore.py restore-sources [backup_file]")
        print("  python dremio_backup_restore.py restore-spaces [backup_file]")
        print("  python dremio_backup_restore.py restore-vds [backup_file]")
        sys.exit(1)
    
    action = sys.argv[1]
    backup_restore = DremioBackupRestore()
    
    if action == "backup":
        logger.info("🚀 Démarrage de la sauvegarde complète...")
        backup_restore.backup_all()
        
    elif action == "list":
        backups = backup_restore.list_available_backups()
        if backups:
            logger.info("📋 Sauvegardes disponibles:")
            for backup in backups:
                logger.info(f"  - {backup['date']} ({backup['path']})")
        else:
            logger.info("📂 Aucune sauvegarde trouvée")
            
    elif action == "restore":
        if len(sys.argv) < 3:
            # Utiliser la sauvegarde la plus récente
            backups = backup_restore.list_available_backups()
            if backups:
                backup_file = backups[0]['path']
                logger.info(f"📂 Utilisation de la sauvegarde la plus récente: {backup_file}")
            else:
                logger.error("❌ Aucune sauvegarde trouvée")
                sys.exit(1)
        else:
            backup_file = sys.argv[2]
        
        logger.info("🚀 Restauration complète...")
        backup_restore.restore_sources(backup_file)
        time.sleep(5)
        backup_restore.restore_spaces(backup_file)
        time.sleep(5)
        backup_restore.restore_datasets(backup_file)
        
    elif action == "restore-sources":
        backup_file = sys.argv[2] if len(sys.argv) > 2 else backup_restore.list_available_backups()[0]['path']
        backup_restore.restore_sources(backup_file)
        
    elif action == "restore-spaces":
        backup_file = sys.argv[2] if len(sys.argv) > 2 else backup_restore.list_available_backups()[0]['path']
        backup_restore.restore_spaces(backup_file)
        
    elif action == "restore-vds":
        backup_file = sys.argv[2] if len(sys.argv) > 2 else backup_restore.list_available_backups()[0]['path']
        backup_restore.restore_datasets(backup_file)
        
    else:
        logger.error(f"❌ Action inconnue: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()