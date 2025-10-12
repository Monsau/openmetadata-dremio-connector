"""
Gestionnaire d'agents pour OpenMetadata.

Ce module gère l'enregistrement, la découverte et l'exécution des agents
du connecteur Dremio dans OpenMetadata.
"""

import logging
from typing import Dict, List, Optional, Any, Type
from datetime import datetime

from .dbt_agent import DbtAgent
from .metadata_agent import MetadataAgent
from .lineage_agent import LineageAgent
from .profiler_agent import ProfilerAgent
from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Registre des agents disponibles pour OpenMetadata.
    
    Gère l'enregistrement, la création et la découverte des agents.
    """
    
    # Registre des agents disponibles
    _agents: Dict[str, Type[BaseAgent]] = {
        'dbt': DbtAgent,
        'metadata': MetadataAgent,
        'lineage': LineageAgent,
        'profiler': ProfilerAgent
    }
    
    @classmethod
    def get_available_agents(cls) -> List[Dict[str, Any]]:
        """
        Retourne la liste des agents disponibles.
        
        Returns:
            Liste des agents avec métadonnées
        """
        agents = []
        
        for agent_type, agent_class in cls._agents.items():
            # Crée instance temporaire pour récupérer schéma
            temp_config = {
                'openmetadata': {
                    'api_url': 'http://localhost:8585/api',
                    'token': 'temp',
                    'service_name': 'temp'
                }
            }
            
            try:
                temp_agent = agent_class(temp_config)
                schema = temp_agent.get_schema()
                
                agents.append({
                    'type': agent_type,
                    'name': agent_class.__name__,
                    'description': agent_class.__doc__.split('\n')[1].strip() if agent_class.__doc__ else '',
                    'schema': schema,
                    'class': agent_class.__name__
                })
                
            except Exception as e:
                logger.warning(f"Erreur récupération schéma {agent_type}: {str(e)}")
                
        return agents
    
    @classmethod
    def create_agent(cls, agent_type: str, config: Dict[str, Any]) -> BaseAgent:
        """
        Crée une instance d'agent.
        
        Args:
            agent_type: Type d'agent ('dbt', 'metadata', etc.)
            config: Configuration de l'agent
            
        Returns:
            Instance d'agent configurée
            
        Raises:
            ValueError: Si le type d'agent n'est pas reconnu
        """
        if agent_type not in cls._agents:
            available = list(cls._agents.keys())
            raise ValueError(f"Agent type '{agent_type}' non reconnu. Disponibles: {available}")
        
        agent_class = cls._agents[agent_type]
        return agent_class(config)
    
    @classmethod
    def register_agent(cls, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """
        Enregistre un nouvel agent.
        
        Args:
            agent_type: Nom du type d'agent
            agent_class: Classe de l'agent
        """
        if not issubclass(agent_class, BaseAgent):
            raise ValueError("L'agent doit hériter de BaseAgent")
        
        cls._agents[agent_type] = agent_class
        logger.info(f"Agent '{agent_type}' enregistré: {agent_class.__name__}")
    
    @classmethod
    def get_agent_schema(cls, agent_type: str) -> Dict[str, Any]:
        """
        Retourne le schéma de configuration d'un agent.
        
        Args:
            agent_type: Type d'agent
            
        Returns:
            Schéma JSON pour configuration UI
        """
        if agent_type not in cls._agents:
            raise ValueError(f"Agent type '{agent_type}' non trouvé")
        
        agent_class = cls._agents[agent_type]
        
        # Configuration temporaire pour récupérer schéma
        temp_config = {
            'openmetadata': {
                'api_url': 'http://localhost:8585/api',
                'token': 'temp',
                'service_name': 'temp'
            }
        }
        
        temp_agent = agent_class(temp_config)
        return temp_agent.get_schema()


class AgentExecutor:
    """
    Exécuteur d'agents pour OpenMetadata.
    
    Gère l'exécution, la surveillance et le reporting des agents.
    """
    
    def __init__(self):
        """Initialise l'exécuteur."""
        self.running_agents: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    def execute_agent(self, agent_type: str, config: Dict[str, Any], 
                     agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Exécute un agent avec la configuration donnée.
        
        Args:
            agent_type: Type d'agent à exécuter
            config: Configuration de l'agent
            agent_id: ID unique de l'agent (optionnel)
            
        Returns:
            Résultat d'exécution avec statistiques
        """
        if not agent_id:
            agent_id = f"{agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"🚀 Démarrage agent {agent_type} (ID: {agent_id})")
            
            # Créer agent
            agent = AgentRegistry.create_agent(agent_type, config)
            
            # Marquer comme en cours
            self.running_agents[agent_id] = {
                'type': agent_type,
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'config': config
            }
            
            # Exécuter
            result = agent.run()
            
            # Finaliser
            self.running_agents[agent_id]['status'] = result['status']
            self.running_agents[agent_id]['finished_at'] = datetime.now().isoformat()
            self.running_agents[agent_id]['result'] = result
            
            # Historique
            execution_record = {
                'agent_id': agent_id,
                'agent_type': agent_type,
                'status': result['status'],
                'started_at': self.running_agents[agent_id]['started_at'],
                'finished_at': self.running_agents[agent_id]['finished_at'],
                'result': result
            }
            self.execution_history.append(execution_record)
            
            logger.info(f"✅ Agent {agent_type} terminé: {result['status']}")
            return result
            
        except Exception as e:
            error_result = {
                'status': 'failed',
                'agent_type': agent_type,
                'agent_id': agent_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            if agent_id in self.running_agents:
                self.running_agents[agent_id]['status'] = 'failed'
                self.running_agents[agent_id]['error'] = str(e)
                self.running_agents[agent_id]['finished_at'] = datetime.now().isoformat()
            
            logger.error(f"❌ Erreur agent {agent_type}: {str(e)}")
            return error_result
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Retourne le statut d'un agent.
        
        Args:
            agent_id: ID de l'agent
            
        Returns:
            Statut de l'agent ou None si non trouvé
        """
        return self.running_agents.get(agent_id)
    
    def get_running_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Retourne tous les agents en cours d'exécution.
        
        Returns:
            Dict des agents avec leur statut
        """
        return {
            agent_id: info for agent_id, info in self.running_agents.items()
            if info['status'] == 'running'
        }
    
    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retourne l'historique d'exécution.
        
        Args:
            limit: Nombre max d'enregistrements
            
        Returns:
            Liste des exécutions récentes
        """
        return self.execution_history[-limit:]
    
    def stop_agent(self, agent_id: str) -> bool:
        """
        Arrête un agent en cours d'exécution.
        
        Args:
            agent_id: ID de l'agent à arrêter
            
        Returns:
            True si arrêté avec succès
        """
        if agent_id not in self.running_agents:
            return False
        
        agent_info = self.running_agents[agent_id]
        if agent_info['status'] != 'running':
            return False
        
        # Marquer comme arrêté
        agent_info['status'] = 'stopped'
        agent_info['finished_at'] = datetime.now().isoformat()
        
        logger.info(f"🛑 Agent {agent_id} arrêté")
        return True


# Instances globales
agent_registry = AgentRegistry()
agent_executor = AgentExecutor()


def get_openmetadata_agents() -> Dict[str, Any]:
    """
    Point d'entrée principal pour OpenMetadata.
    
    Retourne la configuration des agents disponibles au format attendu
    par OpenMetadata pour l'intégration dans l'UI.
    
    Returns:
        Configuration agents pour OpenMetadata
    """
    agents = agent_registry.get_available_agents()
    
    return {
        'connector': 'dremio_connector',
        'version': '1.0.0',
        'agents': agents,
        'capabilities': [
            'metadata_ingestion',
            'dbt_integration', 
            'lineage_tracking',
            'data_profiling',
            'incremental_sync'
        ],
        'supported_services': [
            'dremio',
            'dbt',
            'openmetadata'
        ]
    }