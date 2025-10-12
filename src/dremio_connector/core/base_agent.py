"""
Classe de base pour tous les agents OpenMetadata du connecteur Dremio.

Cette classe définit l'interface commune et les fonctionnalités partagées.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class BaseAgent(ABC):
    """
    Classe de base abstraite pour tous les agents.
    
    Définit l'interface standard et fonctionnalités communes:
    - Configuration et validation
    - Logging standardisé
    - Méthodes abstraites à implémenter
    - Utilitaires partagés
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise l'agent de base.
        
        Args:
            config: Configuration complète de l'agent
                - openmetadata: Configuration OpenMetadata requise
                - schedule: Planification optionnelle
                - logging: Configuration logging optionnelle
        """
        self.config = config
        self.openmetadata_config = config.get('openmetadata', {})
        self.schedule = config.get('schedule')
        
        # Configuration logging
        log_config = config.get('logging', {})
        self.logger = self._setup_logger(log_config)
        
        # Validation config de base
        if not self.openmetadata_config:
            raise ValueError("Configuration openmetadata requise")
            
        # Propriétés à définir par les classes filles
        self.agent_type = "base"
    
    def _setup_logger(self, log_config: Dict[str, Any]) -> logging.Logger:
        """
        Configure le logger pour l'agent.
        
        Args:
            log_config: Configuration logging
                - level: Niveau de log (DEBUG, INFO, WARNING, ERROR)
                - format: Format des messages
                
        Returns:
            Logger configuré
        """
        logger_name = f"dremio_connector.agents.{self.__class__.__name__}"
        logger = logging.getLogger(logger_name)
        
        # Éviter duplication si déjà configuré
        if logger.handlers:
            return logger
            
        # Configuration niveau
        level = log_config.get('level', 'INFO').upper()
        logger.setLevel(getattr(logging, level, logging.INFO))
        
        # Configuration format
        log_format = log_config.get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        formatter = logging.Formatter(log_format)
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _validate_openmetadata_config(self) -> List[str]:
        """
        Valide la configuration OpenMetadata de base.
        
        Returns:
            Liste des erreurs de validation
        """
        errors = []
        
        required_fields = ['api_url', 'token']
        for field in required_fields:
            if not self.openmetadata_config.get(field):
                errors.append(f"Champ OpenMetadata requis manquant: {field}")
        
        # Validation URL
        api_url = self.openmetadata_config.get('api_url', '')
        if api_url and not (api_url.startswith('http://') or api_url.startswith('https://')):
            errors.append("api_url doit commencer par http:// ou https://")
        
        return errors
    
    def _get_timestamp(self) -> str:
        """
        Retourne timestamp ISO actuel.
        
        Returns:
            Timestamp au format ISO
        """
        return datetime.now().isoformat()
    
    def get_config(self) -> Dict[str, Any]:
        """
        Retourne la configuration complète de l'agent.
        
        Returns:
            Configuration avec métadonnées
        """
        return {
            'agent_type': self.agent_type,
            'config': self.config,
            'schedule': self.schedule,
            'created_at': self._get_timestamp()
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test les connexions configurées.
        
        Returns:
            Résultat des tests de connexion
        """
        try:
            validation = self.validate_config()
            
            # Test basique OpenMetadata (sera surchargé par les classes filles)
            om_test = self._test_openmetadata_connection()
            
            return {
                'status': 'success' if validation['valid'] and om_test['success'] else 'failed',
                'agent_type': self.agent_type,
                'validation': validation,
                'openmetadata_connection': om_test,
                'timestamp': self._get_timestamp()
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': self._get_timestamp()
            }
    
    def _test_openmetadata_connection(self) -> Dict[str, Any]:
        """
        Test basique de connexion OpenMetadata.
        
        Returns:
            Résultat du test
        """
        try:
            # Import dynamique pour éviter dépendance circulaire
            from ..clients.openmetadata_client import OpenMetadataClient
            
            client = OpenMetadataClient(self.openmetadata_config)
            health = client.health_check()
            
            return {
                'success': True,
                'health': health,
                'message': 'Connexion OpenMetadata OK'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erreur connexion OpenMetadata'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retourne le statut actuel de l'agent.
        
        Returns:
            Statut avec informations système
        """
        return {
            'agent_type': self.agent_type,
            'status': 'ready',
            'config_valid': self.validate_config()['valid'],
            'schedule': self.schedule,
            'last_check': self._get_timestamp()
        }
    
    def to_json(self) -> str:
        """
        Sérialise l'agent en JSON.
        
        Returns:
            Représentation JSON de l'agent
        """
        agent_data = {
            'agent_type': self.agent_type,
            'config': self.config,
            'status': self.get_status(),
            'schema': self.get_schema()
        }
        
        return json.dumps(agent_data, indent=2, ensure_ascii=False)
    
    @abstractmethod
    def validate_config(self) -> Dict[str, Any]:
        """
        Valide la configuration spécifique de l'agent.
        
        À implémenter par chaque agent.
        
        Returns:
            Résultat validation avec erreurs éventuelles
        """
        pass
    
    @abstractmethod 
    def run(self) -> Dict[str, Any]:
        """
        Exécute la logique principale de l'agent.
        
        À implémenter par chaque agent.
        
        Returns:
            Résultat d'exécution avec statistiques
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Retourne le schéma JSON de configuration pour l'UI.
        
        À implémenter par chaque agent.
        
        Returns:
            Schéma JSON Schema pour formulaire de configuration
        """
        pass