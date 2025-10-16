"""
Configuration loading utilities
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Union


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file.
    
    Args:
        config_path: Path to configuration file (.yaml, .yml, or .json)
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If file format is not supported
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        if config_path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif config_path.suffix == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries, with override taking precedence.
    
    Args:
        base_config: Base configuration dictionary
        override_config: Override configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_config(config: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate that all required keys are present in configuration.
    
    Args:
        config: Configuration dictionary to validate
        required_keys: List of required configuration keys
        
    Returns:
        True if valid, False otherwise
    """
    for key in required_keys:
        if '.' in key:
            # Handle nested keys like 'source.serviceConnection'
            parts = key.split('.')
            current = config
            for part in parts:
                if not isinstance(current, dict) or part not in current:
                    return False
                current = current[part]
        else:
            if key not in config:
                return False
    
    return True
