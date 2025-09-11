"""
Template management for system dynamics models.

This module provides template functionality for creating common
system dynamics model patterns.
"""

from typing import Dict, Any, Optional
from ..engine.system import SystemModel
from .builder import YAMLSystemBuilder


class TemplateManager:
    """Manager for system dynamics model templates."""
    
    def __init__(self):
        """Initialize the template manager with built-in templates."""
        self._templates = {}
        self._register_builtin_templates()
    
    def register_template(self, name: str, template_config: Dict[str, Any], description: str = ""):
        """
        Register a new template.
        
        Parameters:
        -----------
        name : str
            Name of the template
        template_config : dict
            Template configuration dictionary
        description : str
            Description of the template
        """
        self._templates[name] = {
            'config': template_config,
            'description': description
        }
    
    def list_templates(self) -> Dict[str, str]:
        """List all available templates with descriptions."""
        return {name: template['description'] for name, template in self._templates.items()}
    
    def instantiate_template(self, template_name: str, parameters: Dict[str, Any]) -> SystemModel:
        """
        Instantiate a model from a template.
        
        Parameters:
        -----------
        template_name : str
            Name of the template to instantiate
        parameters : dict
            Parameters to customize the template
            
        Returns:
        --------
        SystemModel : The instantiated model
        """
        if template_name not in self._templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self._templates[template_name]
        config = template['config'].copy()
        
        # Apply parameter substitutions
        config = self._apply_parameters(config, parameters)
        
        # Build model using YAML builder
        builder = YAMLSystemBuilder()
        return builder.build_from_dict(config)
    
    def _apply_parameters(self, config: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply parameter substitutions to template configuration."""
        # Update constants with provided parameters
        if 'constants' not in config:
            config['constants'] = {}
        
        config['constants'].update(parameters)
        
        # Update model name if provided
        if 'model_name' in parameters:
            if 'model' not in config:
                config['model'] = {}
            config['model']['name'] = parameters['model_name']
        
        return config
    
    def _register_builtin_templates(self):
        """Register built-in templates."""
        
        # Simple growth template
        self.register_template(
            'exponential_growth',
            {
                'model': {
                    'name': 'Exponential Growth Model',
                    'description': 'Simple exponential growth system',
                    'time_horizon': 50,
                    'dt': 0.25
                },
                'constants': {
                    'initial_value': 1000,
                    'growth_rate': 0.02
                },
                'elements': {
                    'stocks': [
                        {
                            'name': 'Stock',
                            'initial_value': '$initial_value',
                            'units': 'units',
                            'description': 'Main stock variable',
                            'min_value': 0
                        }
                    ],
                    'flows': [
                        {
                            'name': 'Growth',
                            'rate': 'exponential_growth',
                            'units': 'units/year',
                            'description': 'Growth flow',
                            'parameters': {
                                'growth_rate': '$growth_rate'
                            }
                        }
                    ]
                },
                'connections': [
                    {
                        'from': 'Growth',
                        'to': 'Stock',
                        'type': 'inflow'
                    }
                ]
            },
            'Simple exponential growth model'
        )
        
        # Logistic growth template
        self.register_template(
            'logistic_growth',
            {
                'model': {
                    'name': 'Logistic Growth Model',
                    'description': 'Growth with carrying capacity',
                    'time_horizon': 100,
                    'dt': 0.25
                },
                'constants': {
                    'initial_value': 1000,
                    'growth_rate': 0.03,
                    'carrying_capacity': 10000
                },
                'elements': {
                    'stocks': [
                        {
                            'name': 'Stock',
                            'initial_value': '$initial_value',
                            'units': 'units',
                            'description': 'Main stock variable',
                            'min_value': 0
                        }
                    ],
                    'flows': [
                        {
                            'name': 'Growth',
                            'rate': 'logistic_growth',
                            'units': 'units/year',
                            'description': 'Logistic growth',
                            'parameters': {
                                'growth_rate': '$growth_rate',
                                'carrying_capacity': '$carrying_capacity'
                            }
                        }
                    ]
                },
                'connections': [
                    {
                        'from': 'Growth',
                        'to': 'Stock',
                        'type': 'inflow'
                    }
                ]
            },
            'Logistic growth model with carrying capacity'
        )

