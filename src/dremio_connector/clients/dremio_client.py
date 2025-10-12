
"""
Dremio client pour l'ingestion vers OpenMetadata.
Gère toutes les interactions avec l'API Dremio.
"""

import logging
import requests
import json
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DremioClient:
	"""Client Dremio pour récupérer sources et VDS"""
    
	def __init__(self, config: Dict[str, Any]):
		"""
		Initialise le client Dremio.
		
		Args:
			config: Configuration Dremio
				- url: URL Dremio (ex: http://localhost:9047)
				- username: Nom utilisateur
				- password: Mot de passe
				- port: Port (optionnel, extrait de l'URL)
		"""
		if isinstance(config, str):
			# Compatibilité ancienne signature (host)
			raise ValueError("Utiliser config dict au lieu de paramètres individuels")
		
		self.url = config.get('url', 'http://localhost:9047')
		self.username = config.get('username')
		self.password = config.get('password')
		
		# Extraire host et port de l'URL
		from urllib.parse import urlparse
		parsed = urlparse(self.url)
		self.host = parsed.hostname or 'localhost'
		self.port = parsed.port or 9047
		self.base_url = self.url
		self.session = requests.Session()
		self.token = None
        
	def test_connection(self) -> bool:
		"""Test la connexion à Dremio"""
		try:
			if not self._login():
				return False
            
			# Test simple API call avec l'API v3
			response = self.session.get(f"{self.base_url}/api/v3/catalog")
			return response.status_code == 200
            
		except Exception as e:
			logger.error(f"Erreur test connexion Dremio: {e}")
			return False
    
	def _login(self) -> bool:
		"""Authentification sur Dremio"""
		try:
			login_data = {
				"userName": self.username,
				"password": self.password
			}
            
			response = self.session.post(
				f"{self.base_url}/apiv2/login",
				json=login_data,
				headers={'Content-Type': 'application/json'}
			)
            
			if response.status_code == 200:
				self.token = response.json().get('token')
				self.session.headers.update({'Authorization': f'_dremio{self.token}'})
				logger.info("[OK] Connexion Dremio réussie")
				return True
			else:
				logger.error(f"Échec authentification Dremio: {response.status_code}")
				return False
                
		except Exception as e:
			logger.error(f"Erreur authentification Dremio: {e}")
			return False
    
	def get_sources(self) -> List[Dict[str, Any]]:
		"""Récupère toutes les sources Dremio"""
		try:
			if not self.token:
				self._login()
            
			response = self.session.get(f"{self.base_url}/api/v3/catalog")
            
			if response.status_code == 200:
				data = response.json()
				sources = []
                
				for item in data.get('data', []):
					if item.get('containerType') == 'SOURCE':
						sources.append({
							'id': item['id'],
							'name': item['path'][0],  # Premier élément du path
							'displayName': item.get('displayName', item['path'][0]),
							'type': item.get('type', 'Unknown'),
							'description': item.get('description', ''),
							'path': item.get('path', [])
						})
                
				logger.info(f"[OK] {len(sources)} sources récupérées")
				return sources
			else:
				logger.error(f"Erreur récupération sources: {response.status_code}")
				return []
                
		except Exception as e:
			logger.error(f"Erreur get_sources: {e}")
			return []
    
	def get_source_datasets(self, source_id: str) -> List[Dict[str, Any]]:
		"""Récupère les datasets d'une source spécifique"""
		try:
			if not self.token:
				self._login()
            
			response = self.session.get(f"{self.base_url}/api/v3/catalog/{source_id}")
            
			if response.status_code == 200:
				data = response.json()
				datasets = []
                
				logger.info(f"Source catalog keys: {list(data.keys())}")
				children = data.get('children', [])
				logger.info(f"Nombre d'enfants directs: {len(children)}")
                
				# Log des premiers enfants pour debug
				for i, child in enumerate(children[:3]):
					logger.info(f"  Enfant {i+1}: {child.get('path', [])} (Type: {child.get('type', 'N/A')}, ContainerType: {child.get('containerType', 'N/A')})")
                
				# Parcours récursif des enfants avec plus de profondeur
				logger.info(f"Début exploration récursive pour source {source_id}")
				self._extract_datasets_recursive(children, datasets, depth=0, max_depth=5)
                
				logger.info(f"[OK] {len(datasets)} datasets trouvés pour source {source_id}")
                
				# Log des datasets trouvés
				for i, dataset in enumerate(datasets[:3]):
					logger.info(f"  Dataset {i+1}: {dataset.get('name', 'N/A')} (Type: {dataset.get('type', 'N/A')})")
                
				return datasets
			else:
				logger.error(f"Erreur récupération datasets source {source_id}: {response.status_code}")
				return []
                
		except Exception as e:
			logger.error(f"Erreur get_source_datasets: {e}")
			return []
    
	def _extract_datasets_recursive(self, children: List[Dict], datasets: List[Dict], depth: int = 0, max_depth: int = 5):
		"""Extraction récursive des datasets avec contrôle de profondeur"""
		if depth > max_depth:
			logger.warning(f"Profondeur maximale atteinte: {depth}")
			return
            
		indent = "  " * depth
		logger.info(f"{indent}Exploration niveau {depth}, {len(children)} enfants")
        
		for i, child in enumerate(children):
			child_path = child.get('path', ['Unknown'])
			child_type = child.get('type', 'N/A')
			container_type = child.get('containerType', 'N/A')
            
			logger.info(f"{indent}  [{i+1}] {child_path} (Type: {child_type}, Container: {container_type})")
            
			# Rechercher les datasets (tables physiques et vues)
			if child_type in ['PHYSICAL_DATASET', 'VIRTUAL_DATASET', 'TABLE', 'VIEW', 'DATASET']:
				dataset = {
					'id': child['id'],
					'name': child_path[-1] if child_path else child.get('name', 'Unknown'),
					'displayName': child.get('displayName', child.get('name', 'Unknown')),
					'type': child_type,
					'path': child_path,
					'description': child.get('description', ''),
					'containerType': container_type
				}
				datasets.append(dataset)
				logger.info(f"{indent}    -> Dataset ajouté: {dataset['name']}")
            
			# Si c'est un conteneur, explorer ses enfants
			elif container_type in ['FOLDER', 'SCHEMA', 'DATABASE'] or child_type == 'CONTAINER':
				try:
					logger.info(f"{indent}    -> Exploration conteneur: {child_path}")
					# Récupérer les enfants de ce conteneur
					child_response = self.session.get(f"{self.base_url}/api/v3/catalog/{child['id']}")
					if child_response.status_code == 200:
						child_data = child_response.json()
						if 'children' in child_data and len(child_data['children']) > 0:
							logger.info(f"{indent}      {len(child_data['children'])} sous-enfants trouvés")
							self._extract_datasets_recursive(child_data['children'], datasets, depth + 1, max_depth)
						else:
							logger.info(f"{indent}      Aucun sous-enfant")
					else:
						logger.warning(f"{indent}      Erreur API {child_response.status_code} pour {child_path}")
				except Exception as e:
					logger.warning(f"{indent}    Erreur exploration {child_path}: {e}")
            
			# Parcours récursif des enfants directs aussi (au cas où)
			if 'children' in child and len(child['children']) > 0:
				logger.info(f"{indent}    -> Enfants directs trouvés dans l'objet")
				self._extract_datasets_recursive(child['children'], datasets, depth + 1, max_depth)
    
	def get_vds(self) -> List[Dict[str, Any]]:
		"""Récupère tous les VDS (Virtual Data Sets)"""
		try:
			if not self.token:
				self._login()
            
			vds_list = []
            
			# Méthode 1: Recherche via l'API spaces qui est plus fiable pour les VDS
			logger.info("Recherche VDS via API spaces...")
			spaces_response = self.session.get(f"{self.base_url}/api/v3/catalog")
            
			if spaces_response.status_code == 200:
				catalog_data = spaces_response.json()
                
				# Vérifier si c'est une liste ou un dict avec 'data'
				if isinstance(catalog_data, list):
					catalog_items = catalog_data
				else:
					catalog_items = catalog_data.get('data', [])
                
				# Recherche des espaces (SPACE) pour explorer les VDS
				for item in catalog_items:
					if item.get('containerType') == 'SPACE':
						logger.info(f"Exploration espace: {item.get('path', ['Unknown'])}")
						self._explore_space_for_vds(item.get('id'), vds_list)
                
				# Si aucun VDS trouvé, essayer la méthode récursive classique
				if len(vds_list) == 0:
					logger.info("Recherche VDS par méthode récursive...")
					self._find_vds_recursive(catalog_items, vds_list, depth=0, max_depth=3)
                
				# Méthode 3: Essayer l'API search si toujours rien
				if len(vds_list) == 0:
					logger.info("Tentative de recherche VDS via API search alternative...")
					search_response = self.session.get(f"{self.base_url}/apiv2/datasets/search?filter=*")
                    
					if search_response.status_code == 200:
						search_data = search_response.json()
                        
						# Handle both list and dict responses
						if isinstance(search_data, list):
							search_items = search_data
						else:
							search_items = search_data.get('results', [])
                        
						for item in search_items:
							if item.get('datasetType') == 'VIRTUAL_DATASET':
								# Debug logging
								logger.info(f"VDS trouvé via search: {item}")
                                
								# Extract name and path properly
								item_path = item.get('fullPath', item.get('path', []))
								item_name = item_path[-1] if item_path else item.get('name', 'Unknown')
                                
								vds_list.append({
									'id': item.get('id'),
									'name': item_name,
									'displayName': item.get('displayName', item_name),
									'path': '.'.join(item_path),
									'type': item.get('datasetType'),
									'description': item.get('description', '')
								})
                
				logger.info(f"[OK] {len(vds_list)} VDS récupérés")
				return vds_list
			else:
				logger.error(f"Erreur récupération catalogue pour VDS: {spaces_response.status_code}")
				return []
                
		except Exception as e:
			logger.error(f"Erreur get_vds: {e}")
			return []
    
	def _find_vds_recursive(self, catalog_items: List[Dict], vds_list: List[Dict], depth: int = 0, max_depth: int = 3):
		"""Recherche récursive des VDS dans le catalogue"""
		if depth > max_depth:
			return
            
		for item in catalog_items:
			# Si c'est un VDS, l'ajouter à la liste
			if item.get('type') == 'VIRTUAL_DATASET':
				vds_list.append({
					'id': item['id'],
					'name': item['path'][-1] if item.get('path') else item.get('name', 'Unknown'),
					'displayName': item.get('displayName', item.get('name', 'Unknown')),
					'path': '.'.join(item.get('path', [])),
					'type': item.get('type'),
					'description': item.get('description', '')
				})
				logger.info(f"VDS trouvé: {item.get('path', ['Unknown'])}")
            
			# Si c'est un conteneur, explorer ses enfants
			elif item.get('containerType') in ['SPACE', 'FOLDER', 'HOME']:
				try:
					child_response = self.session.get(f"{self.base_url}/api/v3/catalog/{item['id']}")
					if child_response.status_code == 200:
						child_data = child_response.json()
						if 'children' in child_data:
							self._find_vds_recursive(child_data['children'], vds_list, depth + 1, max_depth)
				except Exception as e:
					logger.warning(f"Erreur exploration enfants VDS de {item.get('path', ['Unknown'])}: {e}")
    
	def _explore_space_for_vds(self, space_id: str, vds_list: List[Dict]):
		"""Explore un espace spécifique à la recherche de VDS"""
		try:
			space_response = self.session.get(f"{self.base_url}/api/v3/catalog/{space_id}")
			if space_response.status_code == 200:
				space_data = space_response.json()
				children = space_data.get('children', [])
                
				for child in children:
					if child.get('type') == 'VIRTUAL_DATASET':
						vds_list.append({
							'id': child.get('id'),
							'name': child.get('path', ['Unknown'])[-1] if child.get('path') else child.get('name', 'Unknown'),
							'displayName': child.get('displayName', child.get('name', 'Unknown')),
							'path': '.'.join(child.get('path', [])),
							'type': child.get('type'),
							'description': child.get('description', '')
						})
						logger.info(f"VDS trouvé dans espace: {child.get('path', ['Unknown'])}")
                    
					# Explorer récursivement les folders dans l'espace
					elif child.get('containerType') == 'FOLDER':
						self._explore_space_for_vds(child.get('id'), vds_list)
                        
		except Exception as e:
			logger.warning(f"Erreur exploration espace {space_id}: {e}")
    
	def get_vds_details(self, vds_id: str) -> Dict[str, Any]:
		"""Récupère les détails d'un VDS spécifique"""
		try:
			if not self.token:
				self._login()
            
			response = self.session.get(f"{self.base_url}/api/v3/catalog/{vds_id}")
            
			if response.status_code == 200:
				data = response.json()
				return {
					'id': data['id'],
					'name': data['path'][-1],
					'sql': data.get('sql', ''),
					'description': data.get('description', ''),
					'createdAt': data.get('createdAt'),
					'modifiedAt': data.get('modifiedAt')
				}
			else:
				logger.error(f"Erreur récupération détails VDS {vds_id}: {response.status_code}")
				return {}
                
		except Exception as e:
			logger.error(f"Erreur get_vds_details: {e}")
			return {}
    
	def get_table_schema(self, table_id: str) -> List[Dict[str, Any]]:
		"""Récupère le schéma d'une table"""
		try:
			if not self.token:
				self._login()
            
			response = self.session.get(f"{self.base_url}/api/v3/catalog/{table_id}")
            
			if response.status_code == 200:
				data = response.json()
				fields = data.get('fields', [])
                
				schema = []
				for field in fields:
					schema.append({
						'name': field.get('name', ''),
						'type': field.get('type', {}).get('name', 'VARCHAR'),
						'description': field.get('description', '')
					})
                
				return schema
			else:
				logger.error(f"Erreur récupération schéma table {table_id}: {response.status_code}")
				return []
                
		except Exception as e:
			logger.error(f"Erreur get_table_schema: {e}")
			return []
    
	def get_vds_schema(self, vds_id: str) -> List[Dict[str, Any]]:
		"""Récupère le schéma d'un VDS"""
		return self.get_table_schema(vds_id)  # Même API pour VDS et tables
    
	def get_catalog_tree(self) -> Dict[str, Any]:
		"""Récupère l'arbre complet du catalogue Dremio"""
		try:
			if not self.token:
				self._login()
            
			response = self.session.get(f"{self.base_url}/api/v3/catalog")
            
			if response.status_code == 200:
				return response.json()
			else:
				logger.error(f"Erreur récupération catalogue: {response.status_code}")
				return {}
                
		except Exception as e:
			logger.error(f"Erreur get_catalog_tree: {e}")
			return {}
