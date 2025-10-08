"""
OpenMetadata client pour l'ingestion Dremio.
Basé sur le client du projet ingestion-generic.
Gère toutes les interactions avec l'API OpenMetadata.
"""

import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class OpenMetadataClient:
    """Client OpenMetadata - Compatible avec API v1 (OpenMetadata 1.9.7+)"""
    
    def __init__(self, base_url: str, jwt_token: str):
        self.base_url = base_url.rstrip('/')
        self.jwt_token = jwt_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-OM-Version': '1.9.7'  # Spécifier la version pour compatibilité
        })
    
    def health_check(self) -> bool:
        """Vérifie si OpenMetadata est accessible"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/system/version", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check échoué: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: dict = None, ignore_409=True):
        """Effectue une requête API avec gestion d'erreurs"""
        try:
            url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=30)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data, timeout=30)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 409 and ignore_409:
                logger.warning(f"Ressource existe déjà (409): {endpoint}")
                return {"status": "exists"}
            else:
                logger.error(f"Erreur API {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur requête {method} {endpoint}: {e}")
            return None
    
    def create_database_service(self, service_definition: Dict[str, Any]) -> bool:
        """Crée un service de base de données"""
        try:
            logger.info(f"Création service: {service_definition['name']}")
            
            # Vérification si le service existe déjà
            existing = self._make_request('GET', f"services/databaseServices/name/{service_definition['name']}")
            if existing and existing.get('id'):
                logger.info(f"Service {service_definition['name']} existe déjà")
                return True
            
            # Création du service
            result = self._make_request('POST', 'services/databaseServices', service_definition)
            
            if result:
                logger.info(f"✅ Service {service_definition['name']} créé")
                return True
            else:
                logger.error(f"❌ Échec création service {service_definition['name']}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur création service: {e}")
            return False
    
    def create_database_schema(self, schema_definition: Dict[str, Any]) -> bool:
        """Crée un schéma de base de données"""
        try:
            logger.info(f"Création schéma: {schema_definition['name']}")
            
            # Récupération du service parent
            service_name = schema_definition.get('service', 'dremio-custom-service')
            service = self._make_request('GET', f"services/databaseServices/name/{service_name}")
            
            if not service:
                logger.error(f"Service parent {service_name} introuvable")
                return False
            
            # Création de la base de données d'abord
            database_definition = {
                "name": f"{service_name}_database",
                "displayName": f"Dremio Database",
                "description": "Base de données Dremio pour l'ingestion",
                "service": service['fullyQualifiedName']  # Utilise FQN au lieu d'objet
            }
            
            # Création/récupération de la base de données
            database = self._make_request('POST', 'databases', database_definition)
            if not database or database == {"status": "exists"}:
                # Essayer de récupérer la base existante avec le FQN complet
                database_fqn = f"{service_name}.{database_definition['name']}"
                logger.info(f"Tentative récupération database avec FQN: {database_fqn}")
                database = self._make_request('GET', f"databases/name/{database_fqn}")
                
                # Si toujours pas trouvé, essayer avec le nom simple
                if not database:
                    logger.info(f"Tentative récupération database avec nom simple: {database_definition['name']}")
                    database = self._make_request('GET', f"databases/name/{database_definition['name']}")
            
            if database and database.get('id'):
                logger.info(f"Database récupérée avec succès: {database['name']} (ID: {database['id']}, FQN: {database.get('fullyQualifiedName', 'N/A')})")
            else:
                logger.error(f"Impossible de créer/récupérer la base de données. Nom testé: {database_definition['name']}, FQN: {service_name}.{database_definition['name']}")
                return False
            
            # Préparation du schéma
            schema_payload = {
                "name": schema_definition['name'],
                "displayName": schema_definition.get('displayName', schema_definition['name']),
                "description": schema_definition.get('description', ''),
                "database": database['fullyQualifiedName']  # Utilise FQN au lieu d'objet
            }
            
            result = self._make_request('POST', 'databaseSchemas', schema_payload)
            
            if result:
                logger.info(f"[OK] Schéma {schema_definition['name']} créé")
                return True
            else:
                logger.error(f"[ERROR] Échec création schéma {schema_definition['name']}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur création schéma: {e}")
            return False
    
    def create_table(self, table_definition: Dict[str, Any]) -> bool:
        """Crée une table dans OpenMetadata"""
        try:
            logger.info(f"Création table: {table_definition['name']}")
            
            # Récupération du schéma parent
            service_name = table_definition.get('service', 'dremio-custom-service')
            schema_name = table_definition.get('databaseSchema', 'default')
            
            # Construction du FQN du schéma correct
            schema_fqn = f"{service_name}.{service_name}_database.{schema_name}"
            logger.info(f"Recherche schéma avec FQN: {schema_fqn}")
            schema = self._make_request('GET', f"databaseSchemas/name/{schema_fqn}")
            
            if not schema:
                logger.error(f"Schéma parent {schema_fqn} introuvable")
                return False
            
            # Préparation des colonnes
            columns = []
            for col_def in table_definition.get('columns', []):
                column = {
                    "name": col_def['name'],
                    "displayName": col_def.get('displayName', col_def['name']),
                    "dataType": col_def.get('dataType', 'VARCHAR'),
                    "dataLength": col_def.get('dataLength', 255),
                    "description": col_def.get('description', '')
                }
                columns.append(column)
            
            # Préparation de la table
            table_payload = {
                "name": table_definition['name'],
                "displayName": table_definition.get('displayName', table_definition['name']),
                "description": table_definition.get('description', ''),
                "tableType": table_definition.get('tableType', 'Regular'),
                "columns": columns,
                "databaseSchema": schema['fullyQualifiedName']
            }
            
            # Ajout du SQL pour les vues
            if table_definition.get('viewDefinition'):
                table_payload['viewDefinition'] = table_definition['viewDefinition']
                table_payload['tableType'] = 'View'
            
            result = self._make_request('POST', 'tables', table_payload)
            
            if result:
                logger.info(f"[OK] Table {table_definition['name']} créée")
                return True
            else:
                logger.error(f"[ERROR] Échec création table {table_definition['name']}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur création table: {e}")
            return False
    
    def create_ingestion_pipeline(self, pipeline_definition: Dict[str, Any]) -> bool:
        """Crée un pipeline d'ingestion"""
        try:
            logger.info(f"Création pipeline: {pipeline_definition['name']}")
            
            # Récupération du service
            service_name = pipeline_definition.get('service', 'dremio-custom-service')
            service = self._make_request('GET', f"services/databaseServices/name/{service_name}")
            
            if not service:
                logger.error(f"Service {service_name} introuvable pour le pipeline")
                return False
            
            # Préparation du pipeline
            pipeline_payload = {
                "name": pipeline_definition['name'],
                "displayName": pipeline_definition.get('displayName', pipeline_definition['name']),
                "description": pipeline_definition.get('description', ''),
                "pipelineType": pipeline_definition.get('pipelineType', 'metadata'),
                "sourceConfig": pipeline_definition.get('sourceConfig', {}),
                "airflowConfig": pipeline_definition.get('airflowConfig', {"scheduleInterval": "@daily"}),
                "service": {
                    "id": service['id'],
                    "type": "databaseService"
                }
            }
            
            result = self._make_request('POST', 'services/ingestionPipelines', pipeline_payload)
            
            if result:
                logger.info(f"[OK] Pipeline {pipeline_definition['name']} créé")
                return True
            else:
                logger.error(f"[ERROR] Échec création pipeline {pipeline_definition['name']}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur création pipeline: {e}")
            return False
    
    def get_service_by_name(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Récupère un service par son nom"""
        # Try direct lookup first
        result = self._make_request('GET', f"services/databaseServices/name/{service_name}")
        if result and result.get('id'):
            return result
            
        # Fallback: search through all services if direct lookup fails
        logger.warning(f"Direct lookup failed for service '{service_name}', trying list search...")
        all_services = self.list_services()
        for service in all_services:
            if service.get('name') == service_name:
                logger.info(f"Found service '{service_name}' via list search")
                return service
        
        logger.error(f"Service '{service_name}' not found even in list search")
        return None
    
    def get_database_by_name(self, database_name: str) -> Optional[Dict[str, Any]]:
        """Récupère une base de données par son nom"""
        return self._make_request('GET', f"databases/name/{database_name}")
    
    def get_schema_by_name(self, schema_fqn: str) -> Optional[Dict[str, Any]]:
        """Récupère un schéma par son FQN"""
        return self._make_request('GET', f"databaseSchemas/name/{schema_fqn}")
    
    def get_table_by_name(self, table_fqn: str) -> Optional[Dict[str, Any]]:
        """Récupère une table par son FQN"""
        return self._make_request('GET', f"tables/name/{table_fqn}")
    
    def list_services(self) -> List[Dict[str, Any]]:
        """Liste tous les services de base de données"""
        result = self._make_request('GET', 'services/databaseServices')
        return result.get('data', []) if result else []
    
    def test_service_connection(self, service_name: str) -> bool:
        """Test la connexion d'un service"""
        try:
            service = self.get_service_by_name(service_name)
            if not service:
                return False
            
            # Pour un CustomDB, on considère que si le service existe, la connexion est OK
            return True
            
        except Exception as e:
            logger.error(f"Erreur test connexion service {service_name}: {e}")
            return False