#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dremio to OpenMetadata Ingestion System
=======================================

Système d'ingestion des sources Dremio et VDS vers OpenMetadata en tant que CustomDB.
Basé sur l'architecture du projet ingestion-generic.

Utilisation:
    python dremio_to_openmetadata_ingestion.py [--mode ingestion|test|dry-run]

Fonctionnalités:
- Récupération des sources Dremio (MinIO, PostgreSQL, etc.)
- Récupération des VDS (Virtual Data Sets)
- Ingestion vers OpenMetadata comme service de base de données personnalisé
- Support des métadonnées et de la lignée des données
"""

import logging
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import des composants
from src.client.dremio_client import DremioClient
from src.client.openmetadata_client import OpenMetadataClient
from src.utils.config_manager import ConfigManager


class DremioOpenMetadataIngestion:
    """Système d'ingestion Dremio vers OpenMetadata"""
    
    def __init__(self, config_file: str = "config/dremio_ingestion.yaml"):
        """Initialise le système d'ingestion"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_manager = ConfigManager(config_file)
        self.dremio_client = None
        self.openmetadata_client = None
        
        self._setup_logging()
        self._setup_clients()
        
    def _setup_logging(self):
        """Configure le logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('dremio_ingestion.log')
            ]
        )
        
    def _setup_clients(self):
        """Initialise les clients Dremio et OpenMetadata"""
        try:
            # Configuration Dremio
            dremio_config = self.config_manager.get_dremio_config()
            self.dremio_client = DremioClient(
                host=dremio_config['host'],
                port=dremio_config['port'],
                username=dremio_config['username'],
                password=dremio_config['password']
            )
            
            # Configuration OpenMetadata
            om_config = self.config_manager.get_openmetadata_config()
            self.openmetadata_client = OpenMetadataClient(
                base_url=f"{om_config['protocol']}://{om_config['host']}:{om_config['port']}",
                jwt_token=om_config['jwt_token']
            )
            
            self.logger.info("[OK] Clients Dremio et OpenMetadata initialisés")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur initialisation clients: {e}")
            raise
    
    def run_ingestion(self) -> bool:
        """Lance l'ingestion complète"""
        try:
            self.logger.info("[START] Début de l'ingestion Dremio vers OpenMetadata")
            
            # 1. Test de connexion
            if not self._test_connections():
                return False
            
            # 2. Création du service CustomDB dans OpenMetadata
            if not self._create_custom_database_service():
                return False
            
            # 3. Ingestion des sources Dremio
            if not self._ingest_dremio_sources():
                return False
            
            # 4. Ingestion des VDS
            if not self._ingest_dremio_vds():
                return False
            
            # 5. Création des pipelines d'ingestion
            if not self._create_ingestion_pipelines():
                return False
            
            self.logger.info("[SUCCESS] Ingestion Dremio vers OpenMetadata terminée avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur lors de l'ingestion: {e}")
            return False
    
    def _test_connections(self) -> bool:
        """Test les connexions aux systèmes"""
        self.logger.info("[TEST] Test des connexions...")
        
        # Test Dremio
        if not self.dremio_client.test_connection():
            self.logger.error("[ERROR] Connexion Dremio échouée")
            return False
        
        # Test OpenMetadata
        if not self.openmetadata_client.health_check():
            self.logger.error("[ERROR] Connexion OpenMetadata échouée")
            return False
        
        self.logger.info("[OK] Toutes les connexions sont opérationnelles")
        return True
    
    def _create_custom_database_service(self) -> bool:
        """Crée le service de base de données personnalisé pour Dremio"""
        self.logger.info("[CREATE] Création du service CustomDB pour Dremio...")
        
        try:
            service_definition = {
                "name": "dremio-custom-service",
                "displayName": "Dremio Data Lake Platform",
                "description": "Service personnalisé pour exposer les sources et VDS Dremio dans OpenMetadata",
                "serviceType": "CustomDatabase",
                "connection": {
                    "config": {
                        "type": "CustomDatabase",
                        "sourcePythonClass": "metadata.ingestion.source.database.customdatabase.source.CustomDatabaseSource",
                        "connectionOptions": {
                            "dremio_host": self.config_manager.get_dremio_config()['host'],
                            "dremio_port": str(self.config_manager.get_dremio_config()['port'])
                        }
                    }
                }
            }
            
            result = self.openmetadata_client.create_database_service(service_definition)
            
            if result:
                self.logger.info("[OK] Service CustomDB Dremio créé avec succès")
                return True
            else:
                self.logger.error("[ERROR] Échec création service CustomDB")
                return False
                
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur création service CustomDB: {e}")
            return False
    
    def _ingest_dremio_sources(self) -> bool:
        """Ingère les sources Dremio comme schémas dans OpenMetadata"""
        self.logger.info("[INGEST] Ingestion des sources Dremio...")
        
        try:
            # Récupération des sources depuis Dremio
            sources = self.dremio_client.get_sources()
            
            for source in sources:
                self.logger.info(f"[SOURCE] Traitement source: {source['name']}")
                
                # Création du schéma dans OpenMetadata
                schema_definition = {
                    "name": source['name'],
                    "displayName": source.get('displayName', source['name']),
                    "description": f"Source Dremio: {source.get('description', '')}",
                    "service": "dremio-custom-service",
                    "sourceType": source.get('type', 'Unknown')
                }
                
                self.openmetadata_client.create_database_schema(schema_definition)
                
                # Ingestion des tables/datasets de cette source
                self._ingest_source_tables(source)
            
            self.logger.info("[OK] Sources Dremio ingérées avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur ingestion sources: {e}")
            return False
    
    def _ingest_source_tables(self, source: Dict[str, Any]):
        """Ingère les tables d'une source spécifique"""
        try:
            # Récupération des datasets/tables de la source
            tables = self.dremio_client.get_source_datasets(source['id'])
            
            for table in tables:
                self.logger.info(f"[TABLE] Traitement table: {table['path']}")
                
                # Récupération du schéma de la table
                table_schema = self.dremio_client.get_table_schema(table['id'])
                
                # Définition de la table pour OpenMetadata
                table_definition = {
                    "name": table['name'],
                    "displayName": table.get('displayName', table['name']),
                    "description": table.get('description', ''),
                    "tableType": "Regular",
                    "columns": self._convert_dremio_columns_to_om(table_schema),
                    "databaseSchema": source['name'],
                    "service": "dremio-custom-service"
                }
                
                self.openmetadata_client.create_table(table_definition)
                
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur ingestion tables source {source['name']}: {e}")
    
    def _ingest_dremio_vds(self) -> bool:
        """Ingère les VDS Dremio comme vues dans OpenMetadata"""
        self.logger.info("[VDS] Ingestion des VDS Dremio...")
        
        try:
            # Créer le schéma pour les VDS
            vds_schema_name = "VDS_Analytics"
            vds_schema_definition = {
                "name": vds_schema_name,
                "description": "Schéma pour les Virtual Data Sets (VDS) Dremio"
            }
            self.openmetadata_client.create_database_schema(vds_schema_definition)
            
            # Récupération des VDS depuis Dremio
            vds_list = self.dremio_client.get_vds()
            
            for vds in vds_list:
                self.logger.info(f"[VDS] Traitement VDS: {vds.get('path', 'Unknown')}")
                
                # Skip if VDS data is incomplete
                if not vds.get('id') or vds.get('name') == 'Unknown':
                    self.logger.warning(f"[VDS] VDS incomplet ignoré: {vds}")
                    continue
                
                # Récupération des détails et du schéma du VDS
                vds_details = self.dremio_client.get_vds_details(vds['id'])
                vds_schema = self.dremio_client.get_vds_schema(vds['id'])
                
                # Déterminer le schéma basé sur le path du VDS
                vds_path = vds.get('path', '')
                if '.' in vds_path:
                    vds_path_parts = vds_path.split('.')
                    # Utiliser le premier niveau comme schéma (ex: Analytics, Reports, etc.)
                    schema_name = vds_path_parts[0]
                    # Créer le schéma s'il n'existe pas
                    schema_definition = {
                        "name": schema_name,
                        "description": f"Schéma Dremio pour l'espace {schema_name}"
                    }
                    self.openmetadata_client.create_database_schema(schema_definition)
                else:
                    schema_name = vds_schema_name
                
                # Définition de la vue pour OpenMetadata
                view_definition = {
                    "name": vds['name'],
                    "displayName": vds.get('displayName', vds['name']),
                    "description": vds_details.get('description', ''),
                    "tableType": "View",
                    "columns": self._convert_dremio_columns_to_om(vds_schema),
                    "databaseSchema": schema_name,
                    "service": "dremio-custom-service"
                }
                
                self.openmetadata_client.create_table(view_definition)
            
            self.logger.info("[OK] VDS Dremio ingérés avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur ingestion VDS: {e}")
            return False
    
    def _convert_dremio_columns_to_om(self, dremio_schema: List[Dict]) -> List[Dict]:
        """Convertit le schéma Dremio vers le format OpenMetadata"""
        om_columns = []
        
        for col in dremio_schema:
            om_column = {
                "name": col['name'],
                "displayName": col.get('displayName', col['name']),
                "dataType": self._map_dremio_type_to_om(col['type']),
                "description": col.get('description', '')
            }
            om_columns.append(om_column)
        
        return om_columns
    
    def _map_dremio_type_to_om(self, dremio_type: str) -> str:
        """Mappe les types Dremio vers les types OpenMetadata"""
        type_mapping = {
            'VARCHAR': 'VARCHAR',
            'INTEGER': 'INT',
            'BIGINT': 'BIGINT',
            'DOUBLE': 'DOUBLE',
            'BOOLEAN': 'BOOLEAN',
            'DATE': 'DATE',
            'TIMESTAMP': 'TIMESTAMP',
            'DECIMAL': 'DECIMAL'
        }
        return type_mapping.get(dremio_type.upper(), 'STRING')
    
    def _create_ingestion_pipelines(self) -> bool:
        """Crée les pipelines d'ingestion dans OpenMetadata"""
        self.logger.info("[PIPELINE] Création des pipelines d'ingestion...")
        
        try:
            pipeline_definition = {
                "name": "dremio-metadata-pipeline",
                "displayName": "Dremio Metadata Ingestion Pipeline",
                "description": "Pipeline d'ingestion automatique des métadonnées Dremio",
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
                "service": "dremio-custom-service"
            }
            
            result = self.openmetadata_client.create_ingestion_pipeline(pipeline_definition)
            
            if result:
                self.logger.info("[OK] Pipeline d'ingestion créé avec succès")
                return True
            else:
                self.logger.error("[ERROR] Échec création pipeline")
                return False
                
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur création pipeline: {e}")
            return False
    
    def run_test_mode(self) -> bool:
        """Mode test - vérifie les connexions et affiche les métadonnées"""
        self.logger.info("[TEST] Mode test - Vérification des connexions et métadonnées")
        
        try:
            # Test connexions
            if not self._test_connections():
                return False
            
            # Affichage des sources Dremio
            sources = self.dremio_client.get_sources()
            self.logger.info(f"[INFO] {len(sources)} sources trouvées dans Dremio:")
            for source in sources[:5]:  # Affiche les 5 premières
                self.logger.info(f"  - {source['name']} ({source.get('type', 'Unknown')})")
            
            # Affichage des VDS
            vds_list = self.dremio_client.get_vds()
            self.logger.info(f"[INFO] {len(vds_list)} VDS trouvés dans Dremio:")
            for vds in vds_list[:5]:  # Affiche les 5 premiers
                self.logger.info(f"  - {vds['path']}")
            
            self.logger.info("[OK] Mode test terminé avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erreur en mode test: {e}")
            return False


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Ingestion Dremio vers OpenMetadata')
    parser.add_argument('--mode', choices=['ingestion', 'test', 'dry-run'], 
                       default='test', help='Mode d\'exécution')
    parser.add_argument('--config', default='config/dremio_ingestion.yaml',
                       help='Fichier de configuration')
    
    args = parser.parse_args()
    
    try:
        ingestion_system = DremioOpenMetadataIngestion(args.config)
        
        if args.mode == 'ingestion':
            success = ingestion_system.run_ingestion()
        elif args.mode == 'test':
            success = ingestion_system.run_test_mode()
        else:  # dry-run
            success = ingestion_system._test_connections()
        
        return 0 if success else 1
        
    except Exception as e:
        logging.error(f"[FATAL] Erreur fatale: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())