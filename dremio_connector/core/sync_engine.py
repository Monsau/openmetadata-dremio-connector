"""
Auto-Sync Engine: Découverte automatique et synchronisation Dremio → OpenMetadata

Ce module fournit un moteur de synchronisation intelligent qui:
- Découvre automatiquement toutes les ressources Dremio (spaces, sources, folders, datasets)
- Synchronise ces ressources dans OpenMetadata avec métadonnées complètes
- Gère la hiérarchie Database → Schema → Table
- Extrait les colonnes avec types et descriptions
- Fournit des statistiques détaillées de synchronisation

Architecture:
    DremioAutoDiscovery: Découverte et exploration récursive des ressources
    OpenMetadataSyncEngine: Synchronisation vers OpenMetadata
    DremioOpenMetadataSync: Orchestrateur principal

Usage:
    from dremio_connector.core.sync_engine import DremioOpenMetadataSync
    
    sync = DremioOpenMetadataSync(
        dremio_url="http://localhost:9047",
        dremio_user="admin",
        dremio_password="admin123",
        openmetadata_url="http://localhost:8585/api",
        jwt_token="your-token",
        service_name="dremio_service"
    )
    
    stats = sync.sync()
    print(f"Synchronisation terminée: {stats}")
"""

import logging
import requests
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DremioAutoDiscovery:
    """
    Moteur de découverte automatique des ressources Dremio
    
    Utilise l'API REST v3 de Dremio pour explorer récursivement:
    - Spaces (@admin, Analytics, etc.)
    - Sources (PostgreSQL, MinIO, etc.)
    - Folders (organisation hiérarchique)
    - Datasets (tables physiques et vues virtuelles)
    
    Gère la normalisation des types d'API inconsistants:
    - /api/v3/catalog → type + containerType
    - /api/v3/catalog/by-path/{path} → entityType
    """
    
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.token = None
        self.headers = {}
        self._visited: Set[str] = set()
    
    def authenticate(self) -> bool:
        """Authentifie auprès de Dremio et récupère le token"""
        try:
            response = requests.post(
                f"{self.url}/apiv2/login",
                json={"userName": self.username, "password": self.password},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json()["token"]
                self.headers = {"Authorization": f"_dremio{self.token}"}
                logger.info("✅ Authentification Dremio réussie")
                return True
            else:
                logger.error(f"❌ Échec authentification: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur authentification: {e}")
            return False
    
    def get_catalog_item(self, path: str = None) -> Optional[Dict]:
        """Récupère un élément du catalogue par path ou le catalogue racine"""
        try:
            if path:
                url = f"{self.url}/api/v3/catalog/by-path/{path}"
            else:
                url = f"{self.url}/api/v3/catalog"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.debug(f"Ressource introuvable: {path}")
                return None
            else:
                logger.warning(f"Erreur {response.status_code} pour {path or 'catalogue racine'}")
                return None
        except requests.Timeout:
            logger.warning(f"Timeout pour {path or 'catalogue racine'}")
            return None
        except Exception as e:
            logger.error(f"Erreur récupération {path}: {e}")
            return None
    
    def get_dataset_schema(self, dataset_id: str) -> Optional[Dict]:
        """Récupère le schéma détaillé d'un dataset (colonnes, types, etc.)"""
        try:
            url = f"{self.url}/api/v3/catalog/{dataset_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.debug(f"Erreur récupération schéma {dataset_id}: {e}")
            return None
    
    def discover_all_resources(self) -> List[Dict]:
        """
        Point d'entrée principal: découvre toutes les ressources Dremio
        
        Returns:
            List[Dict]: Liste des ressources avec structure:
                {
                    "id": str,
                    "path": List[str],
                    "full_path": str (joined path),
                    "type": str (space|source|folder|dataset),
                    "schema": Dict (optionnel, pour datasets),
                    "columns": List[Dict] (optionnel, pour datasets)
                }
        """
        logger.info("🔍 Démarrage auto-discovery Dremio...")
        resources = []
        self._visited.clear()
        
        # Récupérer catalogue racine
        catalog = self.get_catalog_item()
        if not catalog:
            logger.error("❌ Impossible de récupérer le catalogue racine")
            return resources
        
        # Explorer récursivement tous les items racine
        items = catalog.get("data", [])
        logger.info(f"📦 {len(items)} items racine trouvés")
        
        for item in items:
            self._explore_item_deep(item, resources)
        
        logger.info(f"✅ Découverte terminée: {len(resources)} ressources")
        
        # Statistiques par type
        type_counts = {}
        for res in resources:
            res_type = res.get("type", "unknown")
            type_counts[res_type] = type_counts.get(res_type, 0) + 1
        
        logger.info(f"📊 Répartition: {dict(type_counts)}")
        return resources
    
    def _explore_item_deep(self, item: Dict, resources: List[Dict]):
        """
        Explore récursivement un item avec requêtes API pour conteneurs
        
        Gère la normalisation:
        - CONTAINER + SPACE → space
        - CONTAINER + SOURCE → source
        - CONTAINER + FOLDER → folder
        - DATASET → dataset
        """
        path = item.get("path", [])
        path_str = ".".join(path) if path else ""
        
        # Éviter cycles
        if path_str in self._visited:
            return
        self._visited.add(path_str)
        
        # Normaliser le type (API inconsistante)
        item_type = item.get("type", item.get("entityType", "UNKNOWN"))
        container_type = item.get("containerType", "")
        item_id = item.get("id", "")
        
        if item_type == "CONTAINER":
            if container_type == "SPACE":
                entity_type = "space"
            elif container_type == "HOME":
                entity_type = "home"
            elif container_type == "SOURCE":
                entity_type = "source"
            elif container_type == "FOLDER":
                entity_type = "folder"
            else:
                entity_type = "folder"
        elif item_type == "DATASET":
            entity_type = "dataset"
        else:
            entity_type = item_type.lower() if item_type else "unknown"
        
        resource = {
            "id": item_id,
            "path": path,
            "full_path": path_str,
            "type": entity_type
        }
        
        # Pour datasets: récupérer schéma et colonnes
        if entity_type == "dataset" and item_id:
            logger.debug(f"  📄 Schéma pour: {path_str}")
            schema = self.get_dataset_schema(item_id)
            if schema:
                resource["schema"] = schema
                resource["columns"] = self._extract_columns(schema)
        
        resources.append(resource)
        logger.info(f"✓ [{entity_type.upper():7}] {path_str}")
        
        # Explorer conteneurs
        if entity_type in ["space", "source", "folder", "home"] and path:
            container_path = "/".join(path)
            container_data = self.get_catalog_item(container_path)
            if container_data:
                children = container_data.get("children", [])
                if children:
                    logger.debug(f"    → {len(children)} enfants")
                    for child in children:
                        self._explore_item_deep(child, resources)
    
    def _extract_columns(self, schema: Dict) -> List[Dict]:
        """Extrait colonnes avec mapping de types Dremio → OpenMetadata"""
        columns = []
        fields = schema.get("fields", [])
        
        for idx, field in enumerate(fields, start=1):
            column = {
                "name": field.get("name", f"column_{idx}"),
                "dataType": self._map_dremio_type(field.get("type", {})),
                "dataLength": 1,
                "ordinalPosition": idx,
                "description": field.get("description", "")
            }
            columns.append(column)
        
        return columns
    
    def _map_dremio_type(self, dremio_type: Dict) -> str:
        """Mapping types Dremio → OpenMetadata"""
        type_name = dremio_type.get("name", "VARCHAR")
        
        type_mapping = {
            "INTEGER": "INT",
            "BIGINT": "BIGINT",
            "FLOAT": "FLOAT",
            "DOUBLE": "DOUBLE",
            "VARCHAR": "VARCHAR",
            "CHAR": "CHAR",
            "TEXT": "TEXT",
            "BOOLEAN": "BOOLEAN",
            "DATE": "DATE",
            "TIME": "TIME",
            "TIMESTAMP": "TIMESTAMP",
            "DECIMAL": "DECIMAL",
            "NUMERIC": "NUMERIC"
        }
        
        return type_mapping.get(type_name.upper(), "VARCHAR")


class OpenMetadataSyncEngine:
    """
    Moteur de synchronisation vers OpenMetadata
    
    Crée/met à jour les entités OpenMetadata:
    - Databases (par space/source Dremio)
    - Schemas (par folder Dremio)
    - Tables (par dataset Dremio) avec colonnes
    
    Utilise PUT pour idempotence (safe re-run).
    """
    
    def __init__(self, url: str, jwt_token: str, service_name: str):
        self.url = url
        self.service_name = service_name
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        self.stats = {
            "databases": 0,
            "schemas": 0,
            "tables": 0,
            "errors": 0
        }
    
    def create_or_update_database(self, name: str, description: str = "") -> Optional[str]:
        """Crée ou met à jour une database"""
        payload = {
            "name": name,
            "displayName": name,
            "description": description,
            "service": self.service_name
        }
        
        try:
            response = requests.put(
                f"{self.url}/v1/databases",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                fqn = response.json().get("fullyQualifiedName")
                logger.info(f"✅ Database: {fqn}")
                self.stats["databases"] += 1
                return fqn
            else:
                logger.warning(f"⚠️ Échec database {name}: {response.status_code}")
                self.stats["errors"] += 1
                return None
        except Exception as e:
            logger.error(f"❌ Erreur database {name}: {e}")
            self.stats["errors"] += 1
            return None
    
    def create_or_update_schema(self, database_fqn: str, name: str, description: str = "") -> Optional[str]:
        """Crée ou met à jour un schema"""
        payload = {
            "name": name,
            "displayName": name,
            "description": description,
            "database": database_fqn
        }
        
        try:
            response = requests.put(
                f"{self.url}/v1/databaseSchemas",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                fqn = response.json().get("fullyQualifiedName")
                logger.info(f"✅ Schema: {fqn}")
                self.stats["schemas"] += 1
                return fqn
            else:
                logger.warning(f"⚠️ Échec schema {name}: {response.status_code}")
                self.stats["errors"] += 1
                return None
        except Exception as e:
            logger.error(f"❌ Erreur schema {name}: {e}")
            self.stats["errors"] += 1
            return None
    
    def create_or_update_table(self, schema_fqn: str, name: str, columns: List[Dict], description: str = "") -> Optional[str]:
        """Crée ou met à jour une table avec colonnes"""
        payload = {
            "name": name,
            "displayName": name,
            "description": description,
            "tableType": "Regular",
            "columns": columns,
            "databaseSchema": schema_fqn
        }
        
        try:
            response = requests.put(
                f"{self.url}/v1/tables",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                fqn = response.json().get("fullyQualifiedName")
                logger.info(f"✅ Table: {fqn} ({len(columns)} colonnes)")
                self.stats["tables"] += 1
                return fqn
            else:
                logger.warning(f"⚠️ Échec table {name}: {response.status_code}")
                self.stats["errors"] += 1
                return None
        except Exception as e:
            logger.error(f"❌ Erreur table {name}: {e}")
            self.stats["errors"] += 1
            return None


class DremioOpenMetadataSync:
    """
    Orchestrateur principal de synchronisation
    
    Workflow:
    1. Découverte automatique des ressources Dremio
    2. Organisation en hiérarchie Database → Schema → Table
    3. Synchronisation vers OpenMetadata
    4. Statistiques détaillées
    
    Usage:
        sync = DremioOpenMetadataSync(...)
        stats = sync.sync()
    """
    
    def __init__(
        self,
        dremio_url: str,
        dremio_user: str,
        dremio_password: str,
        openmetadata_url: str,
        jwt_token: str,
        service_name: str
    ):
        self.dremio = DremioAutoDiscovery(dremio_url, dremio_user, dremio_password)
        self.om = OpenMetadataSyncEngine(openmetadata_url, jwt_token, service_name)
        self.service_name = service_name
    
    def sync(self) -> Dict:
        """
        Synchronisation complète Dremio → OpenMetadata
        
        Returns:
            Dict: Statistiques de synchronisation
                {
                    "resources_discovered": int,
                    "databases_created": int,
                    "schemas_created": int,
                    "tables_created": int,
                    "errors": int,
                    "duration_seconds": float
                }
        """
        start_time = datetime.now()
        logger.info("="*80)
        logger.info("🚀 SYNCHRONISATION DREMIO → OPENMETADATA")
        logger.info("="*80)
        
        # 1. Authentification
        if not self.dremio.authenticate():
            logger.error("❌ Échec authentification Dremio")
            return {"error": "authentication_failed"}
        
        # 2. Découverte
        resources = self.dremio.discover_all_resources()
        if not resources:
            logger.warning("⚠️ Aucune ressource découverte")
            return {"resources_discovered": 0}
        
        # 3. Organisation hiérarchique
        hierarchy = self._organize_hierarchy(resources)
        
        # 4. Synchronisation vers OpenMetadata
        self._sync_to_openmetadata(hierarchy)
        
        # 5. Statistiques finales
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("="*80)
        logger.info("📊 STATISTIQUES DE SYNCHRONISATION")
        logger.info("="*80)
        logger.info(f"Ressources découvertes:     {len(resources)}")
        logger.info(f"Databases créées/màj:       {self.om.stats['databases']}")
        logger.info(f"Schemas créés/màj:          {self.om.stats['schemas']}")
        logger.info(f"Tables créées/màj:          {self.om.stats['tables']}")
        logger.info(f"Erreurs:                    {self.om.stats['errors']}")
        logger.info(f"Durée:                      {duration:.2f}s")
        logger.info("="*80)
        
        return {
            "resources_discovered": len(resources),
            "databases_created": self.om.stats["databases"],
            "schemas_created": self.om.stats["schemas"],
            "tables_created": self.om.stats["tables"],
            "errors": self.om.stats["errors"],
            "duration_seconds": duration
        }
    
    def _organize_hierarchy(self, resources: List[Dict]) -> Dict:
        """Organise les ressources en hiérarchie Database → Schema → Table"""
        hierarchy = {}
        
        for resource in resources:
            path = resource.get("path", [])
            res_type = resource.get("type")
            
            if not path:
                continue
            
            # Database level: spaces & sources
            if res_type in ["space", "source"]:
                db_name = path[0]
                if db_name not in hierarchy:
                    hierarchy[db_name] = {"schemas": {}}
            
            # Schema level: folders (depth 2+)
            elif res_type == "folder" and len(path) >= 2:
                db_name = path[0]
                schema_name = ".".join(path[1:])
                
                if db_name not in hierarchy:
                    hierarchy[db_name] = {"schemas": {}}
                
                if schema_name not in hierarchy[db_name]["schemas"]:
                    hierarchy[db_name]["schemas"][schema_name] = {"tables": []}
            
            # Table level: datasets
            elif res_type == "dataset":
                if len(path) == 1:
                    # Dataset direct dans space/source
                    db_name = path[0]
                    schema_name = "default"
                else:
                    db_name = path[0]
                    schema_name = ".".join(path[1:-1]) if len(path) > 2 else path[1]
                
                if db_name not in hierarchy:
                    hierarchy[db_name] = {"schemas": {}}
                
                if schema_name not in hierarchy[db_name]["schemas"]:
                    hierarchy[db_name]["schemas"][schema_name] = {"tables": []}
                
                hierarchy[db_name]["schemas"][schema_name]["tables"].append(resource)
        
        return hierarchy
    
    def _sync_to_openmetadata(self, hierarchy: Dict):
        """Synchronise la hiérarchie vers OpenMetadata"""
        for db_name, db_data in hierarchy.items():
            # Créer database
            db_fqn = self.om.create_or_update_database(
                name=db_name,
                description=f"Dremio {db_name} space/source"
            )
            
            if not db_fqn:
                continue
            
            # Créer schemas
            for schema_name, schema_data in db_data.get("schemas", {}).items():
                schema_fqn = self.om.create_or_update_schema(
                    database_fqn=db_fqn,
                    name=schema_name,
                    description=f"Schema {schema_name}"
                )
                
                if not schema_fqn:
                    continue
                
                # Créer tables
                for table in schema_data.get("tables", []):
                    table_name = table["path"][-1]
                    columns = table.get("columns", [])
                    
                    self.om.create_or_update_table(
                        schema_fqn=schema_fqn,
                        name=table_name,
                        columns=columns,
                        description=f"Table {table_name} from Dremio"
                    )


# Fonction utilitaire pour usage direct
def sync_dremio_to_openmetadata(
    dremio_url: str,
    dremio_user: str,
    dremio_password: str,
    openmetadata_url: str,
    jwt_token: str,
    service_name: str
) -> Dict:
    """
    Fonction helper pour synchronisation rapide
    
    Example:
        from dremio_connector.core.sync_engine import sync_dremio_to_openmetadata
        
        stats = sync_dremio_to_openmetadata(
            dremio_url="http://localhost:9047",
            dremio_user="admin",
            dremio_password="admin123",
            openmetadata_url="http://localhost:8585/api",
            jwt_token="your-jwt-token",
            service_name="dremio_service"
        )
        
        print(f"Sync terminée: {stats}")
    """
    sync = DremioOpenMetadataSync(
        dremio_url=dremio_url,
        dremio_user=dremio_user,
        dremio_password=dremio_password,
        openmetadata_url=openmetadata_url,
        jwt_token=jwt_token,
        service_name=service_name
    )
    
    return sync.sync()
