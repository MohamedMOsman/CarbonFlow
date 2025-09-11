"""
Rate function registry for system dynamics models.

This module provides a registry system for rate calculation functions
that can be used in YAML model configurations.
"""

import numpy as np
from typing import Dict, Callable, Any, Optional
from ..core.units import Quantity


class RateFunctionRegistry:
    """Registry for rate calculation functions used in system dynamics models."""
    
    def __init__(self):
        """Initialize the registry with built-in functions."""
        self._functions: Dict[str, Callable] = {}
        self._descriptions: Dict[str, str] = {}
        
        # Register built-in functions
        self._register_builtin_functions()
    
    def register(self, name: str, function: Callable, description: str = ""):
        """
        Register a new rate function.
        
        Parameters:
        -----------
        name : str
            Name of the function
        function : callable
            The rate calculation function
        description : str
            Description of the function
        """
        self._functions[name] = function
        self._descriptions[name] = description
    
    def get(self, name: str) -> Callable:
        """Get a registered function by name."""
        if name not in self._functions:
            raise ValueError(f"Function '{name}' not found in registry")
        return self._functions[name]
    
    def list_functions(self) -> Dict[str, str]:
        """List all registered functions with descriptions."""
        return self._descriptions.copy()
    
    def _register_builtin_functions(self):
        """Register built-in rate functions."""
        
        # Basic growth functions
        self.register(
            "exponential_growth",
            self._exponential_growth,
            "Exponential growth rate: rate * stock"
        )
        
        self.register(
            "logistic_growth", 
            self._logistic_growth,
            "Logistic growth with carrying capacity"
        )
        
        # Climate-related functions (generic)
        self.register(
            "temperature_dependent_rate",
            self._temperature_dependent_rate,
            "Temperature-dependent rate calculation"
        )
    
    def _exponential_growth(self, time: float, dt: float, flow, **kwargs) -> float:
        """Basic exponential growth rate."""
        growth_rate = kwargs.get('growth_rate', 0.02)
        stock_value = kwargs.get('stock_value', 0)
        return growth_rate * stock_value
    
    def _logistic_growth(self, time: float, dt: float, flow, **kwargs) -> float:
        """Logistic growth with carrying capacity."""
        growth_rate = kwargs.get('growth_rate', 0.02)
        carrying_capacity = kwargs.get('carrying_capacity', 10000)
        stock_value = kwargs.get('stock_value', 0)
        
        if carrying_capacity <= 0:
            return 0
        
        return growth_rate * stock_value * (1 - stock_value / carrying_capacity)
    

    
    def _temperature_dependent_rate(self, time: float, dt: float, flow, **kwargs) -> float:
        """Temperature-dependent rate calculation."""
        base_rate = kwargs.get('base_rate', 0.01)
        temperature = kwargs.get('temperature', 15.0)
        baseline_temp = kwargs.get('baseline_temperature', 15.0)
        sensitivity = kwargs.get('temperature_sensitivity', 0.001)
        stock_value = kwargs.get('stock_value', 0)
        
        temp_effect = sensitivity * (temperature - baseline_temp)
        adjusted_rate = base_rate + temp_effect
        
        return max(0, adjusted_rate * stock_value)
    

# Create global registry instance
rate_registry = RateFunctionRegistry()
