"""
Configuration file loader
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Parameters:
    -----------
    config_path : str
        Path to config file
        
    Returns:
    --------
    Dict : Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def get_data_config() -> Dict[str, Any]:
    """Get data configuration section"""
    config = load_config()
    return config.get('data', {})


def get_strategy_config() -> Dict[str, Any]:
    """Get strategy configuration section"""
    config = load_config()
    return config.get('strategy', {})


def get_model_config() -> Dict[str, Any]:
    """Get model configuration section"""
    config = load_config()
    return config.get('model', {})
