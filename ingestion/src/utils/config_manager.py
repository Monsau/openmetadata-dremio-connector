"""
Gestionnaire de configuration pour l'ingestion Dremio vers OpenMetadata.
Basé sur le ConfigurationManager du projet ingestion-generic.
"""

import logging
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """Gestionnaire de configuration pour l'ingestion Dremio"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = {}
        self._load_config()
        self._load_environment_variables()
    
    def _load_config(self):
        """Charge le fichier de configuration YAML"""
        try:
            config_path = Path(self.config_file)
            
            if not config_path.exists():
                logger.error(f"Fichier de configuration introuvable: {self.config_file}")
                raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
            
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            
            logger.info(f"✅ Configuration chargée depuis {self.config_file}")
            
        except Exception as e:
            logger.error(f"Erreur chargement configuration: {e}")
            raise
    
    def _load_environment_variables(self):
        """Charge les variables d'environnement"""
        # Chargement du fichier .env si présent
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip().strip('"\'')
                
                logger.info("✅ Variables d'environnement chargées depuis .env")
            except Exception as e:
                logger.warning(f"Erreur chargement .env: {e}")
    
    def get_dremio_config(self) -> Dict[str, Any]:
        """Récupère la configuration Dremio"""
        dremio_config = self.config.get('dremio', {})
        
        # Résolution des variables d'environnement
        return {
            'host': os.getenv('DREMIO_HOST', dremio_config.get('host', 'localhost')),
            'port': int(os.getenv('DREMIO_PORT', dremio_config.get('port', 9047))),
            'username': os.getenv('DREMIO_USERNAME', dremio_config.get('username', 'admin')),
            'password': os.getenv('DREMIO_PASSWORD', dremio_config.get('password', 'admin123'))
        }
    
    def get_openmetadata_config(self) -> Dict[str, Any]:
        """Récupère la configuration OpenMetadata"""
        om_config = self.config.get('openmetadata', {})
        
        # Récupération du token JWT
        jwt_token = os.getenv('OPENMETADATA_JWT_TOKEN', om_config.get('jwt_token'))
        if not jwt_token:
            logger.error("Token JWT OpenMetadata manquant dans la configuration ou les variables d'environnement")
            raise ValueError("OpenMetadata JWT token is required")
        
        return {
            'host': os.getenv('OPENMETADATA_HOST', om_config.get('host', 'localhost')),
            'port': int(os.getenv('OPENMETADATA_PORT', om_config.get('port', 8585))),
            'protocol': os.getenv('OPENMETADATA_PROTOCOL', om_config.get('protocol', 'http')),
            'api_version': om_config.get('api_version', 'v1'),
            'jwt_token': jwt_token
        }
    
    def get_ingestion_config(self) -> Dict[str, Any]:
        """Récupère la configuration d'ingestion"""
        return self.config.get('ingestion', {
            'batch_size': 100,
            'timeout': 30,
            'retry_count': 3,
            'include_schemas': ['.*'],
            'exclude_schemas': [],
            'include_tables': ['.*'],
            'exclude_tables': [],
            'create_lineage': True,
            'create_profiling': False
        })
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Récupère la configuration de logging"""
        return self.config.get('logging', {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'dremio_ingestion.log'
        })
    
    def get_service_config(self) -> Dict[str, Any]:
        """Récupère la configuration du service CustomDB"""
        return self.config.get('service', {
            'name': 'dremio-custom-db',
            'display_name': 'Dremio Data Lake Platform',
            'description': 'Service personnalisé pour exposer les sources et VDS Dremio dans OpenMetadata',
            'service_type': 'CustomDatabase'
        })
    
    def get_pipeline_config(self) -> Dict[str, Any]:
        """Récupère la configuration des pipelines"""
        return self.config.get('pipeline', {
            'name': 'dremio-metadata-pipeline',
            'display_name': 'Dremio Metadata Ingestion Pipeline',
            'description': 'Pipeline d\'ingestion automatique des métadonnées Dremio',
            'schedule_interval': '@daily',
            'include_views': True,
            'include_tables': True,
            'mark_deleted_tables': False
        })
    
    def validate_configuration(self) -> bool:
        """Valide la configuration"""
        try:
            # Vérification des sections obligatoires
            required_sections = ['dremio', 'openmetadata']
            
            for section in required_sections:
                if section not in self.config:
                    logger.error(f"Section obligatoire manquante: {section}")
                    return False
            
            # Vérification des paramètres Dremio
            dremio_config = self.get_dremio_config()
            required_dremio = ['host', 'port', 'username', 'password']
            
            for param in required_dremio:
                if not dremio_config.get(param):
                    logger.error(f"Paramètre Dremio manquant: {param}")
                    return False
            
            # Vérification des paramètres OpenMetadata
            om_config = self.get_openmetadata_config()
            required_om = ['host', 'port', 'jwt_token']
            
            for param in required_om:
                if not om_config.get(param):
                    logger.error(f"Paramètre OpenMetadata manquant: {param}")
                    return False
            
            logger.info("✅ Configuration validée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation configuration: {e}")
            return False
    
    def get_full_config(self) -> Dict[str, Any]:
        """Récupère la configuration complète"""
        return self.config.copy()
    
    def update_config(self, section: str, key: str, value: Any):
        """Met à jour un paramètre de configuration"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        logger.info(f"Configuration mise à jour: {section}.{key} = {value}")
    
    def save_config(self, output_file: Optional[str] = None):
        """Sauvegarde la configuration dans un fichier"""
        try:
            output_path = Path(output_file or self.config_file)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"✅ Configuration sauvegardée dans {output_path}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde configuration: {e}")
            raise