#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dremio to OpenMetadata Ingestion System - Version Nettoyée
=========================================================

Système d'ingestion optimisé pour transférer les métadonnées Dremio vers OpenMetadata.
Cette version contient uniquement les fonctionnalités essentielles pour l'ingestion.

Auteur: Équipe Data Engineering
Date: Octobre 2024
Version: 2.0-clean

Architecture:
- DremioClient: Interaction avec l'API Dremio pour récupérer sources et VDS
- OpenMetadataClient: Interaction avec l'API OpenMetadata pour créer les entités
- DremioIngestion: Orchestrateur principal de l'ingestion

Fonctionnalités:
✅ Découverte automatique des sources Dremio (PostgreSQL, MinIO, etc.)
✅ Récupération des tables et schémas de chaque source
✅ Découverte des VDS (Virtual Data Sets) dans tous les espaces Dremio
✅ Création du service CustomDatabase dans OpenMetadata
✅ Création des schémas correspondant aux sources/espaces Dremio
✅ Création des tables et vues avec métadonnées complètes
✅ Gestion automatique des types de données et colonnes
✅ Support des espaces VDS multiples (Analytics, DataLake, CustomDB_Analytics, etc.)

Utilisation:
    python dremio_ingestion_clean.py --mode ingestion
    python dremio_ingestion_clean.py --mode test
    python dremio_ingestion_clean.py --mode dry-run
"""

import logging
import sys
import argparse
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Configuration du chemin pour l'import des modules locaux
sys.path.insert(0, str(Path(__file__).parent))

from src.client.dremio_client import DremioClient
from src.client.openmetadata_client import OpenMetadataClient


class DremioIngestion:
    """
    Système d'ingestion Dremio vers OpenMetadata - Version optimisée
    
    Cette classe orchestre l'ensemble du processus d'ingestion en suivant ces étapes:
    1. Test et validation des connexions
    2. Création du service CustomDatabase dans OpenMetadata
    3. Découverte et ingestion des sources Dremio
    4. Découverte et ingestion des VDS (Virtual Data Sets)
    5. Création du pipeline de métadonnées
    """
    
    def __init__(self):
        """Initialise le système d'ingestion avec la configuration depuis les variables d'environnement"""
        self.logger = self._setup_logging()
        self.dremio_client = None
        self.openmetadata_client = None
        self.service_name = "dremio-custom-service"
        self._initialize_clients()
        
    def _setup_logging(self) -> logging.Logger:
        """Configure le système de logging avec format uniforme"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('dremio_ingestion.log', encoding='utf-8')
            ]
        )
        return logging.getLogger(self.__class__.__name__)
        
    def _initialize_clients(self):
        """Initialise les clients Dremio et OpenMetadata depuis les variables d'environnement"""
        try:
            # Configuration Dremio depuis variables d'environnement
            dremio_host = os.getenv('DREMIO_HOST', 'localhost')
            dremio_port = int(os.getenv('DREMIO_PORT', '9047'))
            dremio_username = os.getenv('DREMIO_USERNAME', 'admin')
            dremio_password = os.getenv('DREMIO_PASSWORD', 'admin123')
            
            self.dremio_client = DremioClient(
                host=dremio_host,
                port=dremio_port,
                username=dremio_username,
                password=dremio_password
            )
            
            # Configuration OpenMetadata depuis variables d'environnement
            om_host = os.getenv('OPENMETADATA_HOST', 'localhost')
            om_port = os.getenv('OPENMETADATA_PORT', '8585')
            om_token = os.getenv('OPENMETADATA_JWT_TOKEN', '')
            
            if not om_token:
                raise ValueError("OPENMETADATA_JWT_TOKEN variable d'environnement requise")
            
            self.openmetadata_client = OpenMetadataClient(
                base_url=f"http://{om_host}:{om_port}",
                jwt_token=om_token
            )
            
            self.logger.info("[OK] Clients Dremio et OpenMetadata initialisés")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur initialisation clients: {e}")
            raise
    
    def run_ingestion(self) -> bool:
        """
        Lance l'ingestion complète Dremio vers OpenMetadata
        
        Returns:
            bool: True si l'ingestion s'est déroulée avec succès, False sinon
        """
        try:
            self.logger.info("[START] Début de l'ingestion Dremio vers OpenMetadata")
            
            # Étape 1: Validation des connexions
            if not self._validate_connections():
                return False
            
            # Étape 2: Création du service CustomDatabase
            if not self._create_database_service():
                return False
            
            # Étape 3: Ingestion des sources Dremio (tables physiques)
            if not self._ingest_sources():
                return False
            
            # Étape 4: Ingestion des VDS (Virtual Data Sets)
            if not self._ingest_vds():
                return False
            
            # Étape 5: Création du pipeline de métadonnées
            if not self._create_metadata_pipeline():
                return False
            
            self.logger.info("[SUCCESS] Ingestion Dremio vers OpenMetadata terminée avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur lors de l'ingestion: {e}")
            return False
    
    def _validate_connections(self) -> bool:
        """Valide que les connexions Dremio et OpenMetadata sont opérationnelles"""
        self.logger.info("[TEST] Test des connexions...")
        
        # Test connexion Dremio
        if not self.dremio_client.test_connection():
            self.logger.error("[ERROR] Connexion Dremio échouée")
            return False
        
        # Test connexion OpenMetadata
        if not self.openmetadata_client.health_check():
            self.logger.error("[ERROR] Connexion OpenMetadata échouée")
            return False
        
        self.logger.info("[OK] Toutes les connexions sont opérationnelles")
        return True
    
    def _create_database_service(self) -> bool:
        """Crée le service CustomDatabase dans OpenMetadata pour représenter Dremio"""
        self.logger.info("[CREATE] Création du service CustomDB pour Dremio...")
        
        try:
            service_definition = {
                "name": self.service_name,
                "displayName": "Dremio Data Lake Platform",
                "description": "Service personnalisé pour exposer les sources et VDS Dremio dans OpenMetadata",
                "serviceType": "CustomDatabase",
                "connection": {
                    "config": {
                        "type": "CustomDatabase",
                        "sourcePythonClass": "metadata.ingestion.source.database.customdatabase.source.CustomDatabaseSource",
                        "connectionOptions": {
                            "dremio_host": self.dremio_client.host,
                            "dremio_port": str(self.dremio_client.port)
                        }
                    }
                }
            }
            
            success = self.openmetadata_client.create_database_service(service_definition)
            
            if success:
                self.logger.info("[OK] Service CustomDB Dremio créé avec succès")
                return True
            else:
                self.logger.error("[ERROR] Échec création service CustomDB")
                return False
                
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur création service CustomDB: {e}")
            return False
    
    def _ingest_sources(self) -> bool:
        """
        Ingère les sources Dremio (PostgreSQL, MinIO, etc.) comme schémas dans OpenMetadata
        Chaque source devient un schéma, ses tables deviennent des tables OpenMetadata
        """
        self.logger.info("[INGEST] Ingestion des sources Dremio...")
        
        try:
            # Récupération des sources depuis Dremio
            sources = self.dremio_client.get_sources()
            
            for source in sources:
                self.logger.info(f"[SOURCE] Traitement source: {source['name']}")
                
                # Création du schéma dans OpenMetadata pour cette source
                schema_definition = {
                    "name": source['name'],
                    "description": f"Source Dremio: {source.get('type', 'Unknown')} - {source.get('description', '')}"
                }
                
                self.openmetadata_client.create_database_schema(schema_definition)
                
                # Ingestion des tables de cette source
                self._ingest_source_tables(source)
            
            self.logger.info("[OK] Sources Dremio ingérées avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur ingestion sources: {e}")
            return False
    
    def _ingest_source_tables(self, source: Dict[str, Any]):
        """
        Ingère les tables d'une source Dremio spécifique
        
        Args:
            source: Dictionnaire contenant les informations de la source
        """
        try:
            # Récupération des datasets/tables de la source
            tables = self.dremio_client.get_source_datasets(source['id'])
            
            for table in tables:
                self.logger.info(f"[TABLE] Traitement table: {table['path']}")
                
                # Récupération du schéma de la table
                table_schema = self.dremio_client.get_table_schema(table['id'])
                
                # Conversion du schéma Dremio vers format OpenMetadata
                columns = self._convert_dremio_columns_to_openmetadata(table_schema)
                
                # Définition de la table pour OpenMetadata
                table_definition = {
                    "name": table['name'],
                    "displayName": table.get('displayName', table['name']),
                    "description": f"Table Dremio: {table.get('description', '')}",
                    "tableType": "Regular",
                    "columns": columns,
                    "databaseSchema": source['name']
                }
                
                self.openmetadata_client.create_table(table_definition)
                
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur ingestion tables source {source['name']}: {e}")
    
    def _ingest_vds(self) -> bool:
        """
        Ingère les VDS (Virtual Data Sets) Dremio comme vues dans OpenMetadata
        Les VDS sont organisés par espaces (Analytics, DataLake, CustomDB_Analytics, etc.)
        """
        self.logger.info("[VDS] Ingestion des VDS Dremio...")
        
        try:
            # Création du schéma général pour les VDS
            vds_schema_definition = {
                "name": "VDS_Analytics",
                "description": "Schéma pour les Virtual Data Sets (VDS) Dremio"
            }
            self.openmetadata_client.create_database_schema(vds_schema_definition)
            
            # Récupération des VDS depuis Dremio
            vds_list = self.dremio_client.get_vds()
            
            for vds in vds_list:
                # Extraction du chemin VDS pour déterminer l'organisation
                vds_path = vds.get('path', 'Unknown')
                self.logger.info(f"[VDS] Traitement VDS: {vds_path}")
                
                # Skip les VDS avec données incomplètes
                if not vds.get('id') or vds.get('name') == 'Unknown':
                    self.logger.warning(f"[VDS] VDS incomplet ignoré: {vds}")
                    continue
                
                # Détermination du schéma basé sur l'espace VDS
                schema_name = self._determine_vds_schema(vds_path)
                
                # Création du schéma si nécessaire
                if schema_name != "VDS_Analytics":
                    schema_definition = {
                        "name": schema_name,
                        "description": f"Schéma Dremio pour l'espace {schema_name}"
                    }
                    self.openmetadata_client.create_database_schema(schema_definition)
                
                # Récupération du schéma du VDS
                vds_schema = self.dremio_client.get_vds_schema(vds['id'])
                columns = self._convert_dremio_columns_to_openmetadata(vds_schema)
                
                # Définition de la vue pour OpenMetadata
                view_definition = {
                    "name": vds['name'],
                    "displayName": vds.get('displayName', vds['name']),
                    "description": f"VDS Dremio: {vds.get('description', '')}",
                    "tableType": "View",
                    "columns": columns,
                    "databaseSchema": schema_name
                }
                
                self.openmetadata_client.create_table(view_definition)
            
            self.logger.info("[OK] VDS Dremio ingérés avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur ingestion VDS: {e}")
            return False
    
    def _determine_vds_schema(self, vds_path: str) -> str:
        """
        Détermine le schéma OpenMetadata pour un VDS basé sur son chemin
        
        Args:
            vds_path: Chemin complet du VDS (ex: "Analytics.Vue_Clients_Complets")
            
        Returns:
            str: Nom du schéma à utiliser dans OpenMetadata
        """
        if '.' in vds_path:
            # Utilise le premier niveau comme schéma (Analytics, DataLake, CustomDB_Analytics, etc.)
            return vds_path.split('.')[0]
        else:
            # Schéma par défaut pour les VDS sans organisation claire
            return "VDS_Analytics"
    
    def _convert_dremio_columns_to_openmetadata(self, dremio_schema: List[Dict]) -> List[Dict]:
        """
        Convertit le schéma de colonnes Dremio vers le format OpenMetadata
        
        Args:
            dremio_schema: Liste des colonnes au format Dremio
            
        Returns:
            List[Dict]: Liste des colonnes au format OpenMetadata
        """
        om_columns = []
        
        for col in dremio_schema:
            om_column = {
                "name": col['name'],
                "displayName": col.get('displayName', col['name']),
                "dataType": self._map_dremio_type_to_openmetadata(col['type']),
                "description": col.get('description', ''),
                "dataLength": col.get('precision', 1)  # Longueur par défaut
            }
            om_columns.append(om_column)
        
        return om_columns
    
    def _map_dremio_type_to_openmetadata(self, dremio_type: str) -> str:
        """
        Mappe les types de données Dremio vers les types OpenMetadata compatibles
        
        Args:
            dremio_type: Type de données Dremio (VARCHAR, INTEGER, etc.)
            
        Returns:
            str: Type de données OpenMetadata correspondant
        """
        type_mapping = {
            'VARCHAR': 'VARCHAR',
            'INTEGER': 'INT',
            'BIGINT': 'BIGINT',
            'DOUBLE': 'DOUBLE',
            'BOOLEAN': 'BOOLEAN',
            'DATE': 'DATE',
            'TIMESTAMP': 'TIMESTAMP',
            'DECIMAL': 'DECIMAL',
            'FLOAT': 'FLOAT',
            'TEXT': 'TEXT'
        }
        
        # Nettoyage du type Dremio et mapping
        clean_type = dremio_type.upper().split('(')[0]  # Supprime les paramètres comme VARCHAR(255)
        return type_mapping.get(clean_type, 'STRING')
    
    def _create_metadata_pipeline(self) -> bool:
        """Crée le pipeline d'ingestion des métadonnées dans OpenMetadata"""
        self.logger.info("[PIPELINE] Création des pipelines d'ingestion...")
        
        try:
            pipeline_definition = {
                "name": "dremio-metadata-pipeline",
                "displayName": "Dremio Metadata Ingestion Pipeline",
                "description": "Pipeline d'ingestion automatique des métadonnées Dremio vers OpenMetadata",
                "pipelineType": "metadata",
                "sourceConfig": {
                    "config": {
                        "type": "DatabaseMetadata",
                        "schemaFilterPattern": {"includes": [".*"]},
                        "tableFilterPattern": {"includes": [".*"]}
                    }
                },
                "airflowConfig": {
                    "scheduleInterval": "@daily"
                },
                "service": self.service_name
            }
            
            success = self.openmetadata_client.create_ingestion_pipeline(pipeline_definition)
            
            if success:
                self.logger.info("[OK] Pipeline d'ingestion créé avec succès")
                return True
            else:
                self.logger.error("[ERROR] Échec création pipeline")
                return False
                
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur création pipeline: {e}")
            return False
    
    def run_test_mode(self) -> bool:
        """
        Mode test - vérifie les connexions et affiche un aperçu des métadonnées disponibles
        
        Returns:
            bool: True si le test s'est déroulé avec succès
        """
        self.logger.info("[TEST] Mode test - Vérification des connexions et métadonnées")
        
        try:
            # Validation des connexions
            if not self._validate_connections():
                return False
            
            # Aperçu des sources Dremio
            sources = self.dremio_client.get_sources()
            self.logger.info(f"[INFO] {len(sources)} sources trouvées dans Dremio:")
            for source in sources[:5]:  # Affiche les 5 premières
                self.logger.info(f"  - {source['name']} ({source.get('type', 'Unknown')})")
            
            # Aperçu des VDS
            vds_list = self.dremio_client.get_vds()
            self.logger.info(f"[INFO] {len(vds_list)} VDS trouvés dans Dremio:")
            for vds in vds_list[:5]:  # Affiche les 5 premiers
                vds_path = vds.get('path', 'Unknown')
                self.logger.info(f"  - {vds_path}")
            
            self.logger.info("[OK] Mode test terminé avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur en mode test: {e}")
            return False


def main():
    """
    Point d'entrée principal du système d'ingestion
    
    Arguments de ligne de commande:
    --mode ingestion: Lance l'ingestion complète
    --mode test: Teste les connexions et affiche les métadonnées disponibles  
    --mode dry-run: Teste uniquement les connexions
    """
    parser = argparse.ArgumentParser(
        description='Ingestion Dremio vers OpenMetadata - Version Nettoyée',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python dremio_ingestion_clean.py --mode ingestion
  python dremio_ingestion_clean.py --mode test
  python dremio_ingestion_clean.py --mode dry-run

Variables d'environnement requises:
  DREMIO_HOST, DREMIO_PORT, DREMIO_USERNAME, DREMIO_PASSWORD
  OPENMETADATA_HOST, OPENMETADATA_PORT, OPENMETADATA_JWT_TOKEN
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['ingestion', 'test', 'dry-run'], 
        default='test', 
        help='Mode d\'exécution (défaut: test)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialisation du système d'ingestion
        ingestion_system = DremioIngestion()
        
        # Exécution selon le mode choisi
        if args.mode == 'ingestion':
            success = ingestion_system.run_ingestion()
        elif args.mode == 'test':
            success = ingestion_system.run_test_mode()
        else:  # dry-run
            success = ingestion_system._validate_connections()
        
        # Code de retour
        return 0 if success else 1
        
    except Exception as e:
        logging.error(f"[FATAL] Erreur fatale: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())