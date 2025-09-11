"""
Unit management and dimensional analysis for the System Dynamics Toolkit.

This module provides comprehensive unit handling capabilities using the Pint library,
with extensions for system dynamics modeling and climate science applications.
"""

import pint
import numpy as np
from typing import Union, Optional, Dict, Any
import warnings


class UnitRegistry:
    """
    Enhanced unit registry for system dynamics modeling.
    
    Extends Pint's UnitRegistry with custom units and contexts
    relevant to climate science and system dynamics.
    """
    
    def __init__(self):
        self._ureg = pint.UnitRegistry()
        self._setup_custom_units()
        self._setup_contexts()
    
    def _setup_custom_units(self):
        """Define custom units for climate and system dynamics modeling."""
        # Population units
        self._ureg.define('person = [population]')
        self._ureg.define('people = person')
        self._ureg.define('capita = person')
        
        # Carbon and emissions units
        self._ureg.define('tCO2 = metric_ton * CO2 = [carbon_mass]')
        self._ureg.define('tCO2e = tCO2')  # CO2 equivalent
        
        # Energy units commonly used in climate modeling
        self._ureg.define('TWh = terawatt * hour')
        self._ureg.define('Mtoe = million * tonne_oil_equivalent')
        
        # Economic units
        self._ureg.define('USD = [currency]')
        self._ureg.define('dollar = USD')
        
    def _setup_contexts(self):
        """Setup unit conversion contexts for different modeling domains."""
        # Climate context for emissions and energy
        climate_context = pint.Context('climate')
        climate_context.add_transformation('[carbon_mass]', '[mass]', 
                                         lambda ureg, x: x)
        climate_context.add_transformation('[mass]', '[carbon_mass]', 
                                         lambda ureg, x: x)
        self._ureg.add_context(climate_context)
    
    @property
    def ureg(self):
        """Access to the underlying Pint unit registry."""
        return self._ureg
    
    def Quantity(self, magnitude, units=None):
        """Create a quantity with units."""
        return self._ureg.Quantity(magnitude, units)
    
    def parse_expression(self, expression: str):
        """Parse a unit expression string."""
        return self._ureg.parse_expression(expression)


class Quantity:
    """
    Enhanced quantity class for system dynamics modeling.
    
    Wraps Pint quantities with additional functionality for
    spatiotemporal data and system dynamics operations.
    """
    
    def __init__(self, magnitude, units=None, spatial_dims=None, temporal_dim=None):
        """
        Initialize a quantity with optional spatial and temporal dimensions.
        
        Parameters:
        -----------
        magnitude : array-like or scalar
            The numerical value(s)
        units : str or pint.Unit
            The units of the quantity
        spatial_dims : tuple, optional
            Names of spatial dimensions (e.g., ('x', 'y') or ('lat', 'lon'))
        temporal_dim : str, optional
            Name of temporal dimension (e.g., 'time')
        """
        self._ureg = UnitRegistry().ureg
        
        if isinstance(magnitude, pint.Quantity):
            self._quantity = magnitude
        else:
            self._quantity = self._ureg.Quantity(magnitude, units)
        
        self.spatial_dims = spatial_dims or ()
        self.temporal_dim = temporal_dim
        self._metadata = {}
    
    @property
    def magnitude(self):
        """Get the magnitude (numerical value)."""
        return self._quantity.magnitude
    
    @property
    def units(self):
        """Get the units."""
        return self._quantity.units
    
    @property
    def dimensionality(self):
        """Get the dimensionality."""
        return self._quantity.dimensionality
    
    def to(self, units):
        """Convert to different units."""
        converted = self._quantity.to(units)
        return Quantity(converted, spatial_dims=self.spatial_dims, 
                       temporal_dim=self.temporal_dim)
    
    def check_dimensionality(self, other):
        """Check if two quantities have compatible dimensions."""
        if isinstance(other, Quantity):
            return self.dimensionality == other.dimensionality
        elif isinstance(other, pint.Quantity):
            return self.dimensionality == other.dimensionality
        return False
    
    def __add__(self, other):
        """Add two quantities with dimension checking."""
        if isinstance(other, (Quantity, pint.Quantity)):
            if not self.check_dimensionality(other):
                raise pint.DimensionalityError(
                    f"Cannot add {self.dimensionality} and {other.dimensionality}"
                )
        
        if isinstance(other, Quantity):
            result = self._quantity + other._quantity
        else:
            result = self._quantity + other
        
        return Quantity(result, spatial_dims=self.spatial_dims,
                       temporal_dim=self.temporal_dim)
    
    def __sub__(self, other):
        """Subtract two quantities with dimension checking."""
        if isinstance(other, (Quantity, pint.Quantity)):
            if not self.check_dimensionality(other):
                raise pint.DimensionalityError(
                    f"Cannot subtract {other.dimensionality} from {self.dimensionality}"
                )
        
        if isinstance(other, Quantity):
            result = self._quantity - other._quantity
        else:
            result = self._quantity - other
        
        return Quantity(result, spatial_dims=self.spatial_dims,
                       temporal_dim=self.temporal_dim)
    
    def __mul__(self, other):
        """Multiply quantities."""
        if isinstance(other, Quantity):
            result = self._quantity * other._quantity
        else:
            result = self._quantity * other
        
        return Quantity(result, spatial_dims=self.spatial_dims,
                       temporal_dim=self.temporal_dim)
    
    def __truediv__(self, other):
        """Divide quantities."""
        if isinstance(other, Quantity):
            result = self._quantity / other._quantity
        else:
            result = self._quantity / other
        
        return Quantity(result, spatial_dims=self.spatial_dims,
                       temporal_dim=self.temporal_dim)
    
    def __repr__(self):
        """String representation."""
        return f"Quantity({self._quantity})"


class DimensionalAnalysis:
    """
    Dimensional analysis utilities for system dynamics models.
    
    Provides tools for checking dimensional consistency in model equations
    and automatically inferring units for derived quantities.
    """
    
    def __init__(self):
        self.ureg = UnitRegistry().ureg
    
    def check_equation_consistency(self, left_side, right_side):
        """
        Check if both sides of an equation have consistent dimensions.
        
        Parameters:
        -----------
        left_side : Quantity or pint.Quantity
            Left side of equation
        right_side : Quantity or pint.Quantity  
            Right side of equation
            
        Returns:
        --------
        bool : True if dimensions are consistent
        """
        try:
            if isinstance(left_side, Quantity):
                left_dim = left_side.dimensionality
            else:
                left_dim = left_side.dimensionality
                
            if isinstance(right_side, Quantity):
                right_dim = right_side.dimensionality
            else:
                right_dim = right_side.dimensionality
                
            return left_dim == right_dim
        except Exception as e:
            warnings.warn(f"Could not check dimensional consistency: {e}")
            return False
    
    def infer_units(self, expression_parts):
        """
        Infer the units of a complex expression from its parts.
        
        Parameters:
        -----------
        expression_parts : list of Quantity or pint.Quantity
            Components of the expression
            
        Returns:
        --------
        pint.Unit : Inferred units
        """
        if not expression_parts:
            return self.ureg.dimensionless
        
        # Start with first quantity
        result_units = expression_parts[0].units
        
        # Apply operations (this is a simplified version)
        for part in expression_parts[1:]:
            # This would need to be expanded based on actual operations
            result_units = result_units * part.units
        
        return result_units


# Global unit registry instance
unit_registry = UnitRegistry()

# Convenience functions
def Q_(magnitude, units=None):
    """Create a Quantity (shorthand)."""
    return Quantity(magnitude, units)

def parse_units(unit_string):
    """Parse a unit string."""
    return unit_registry.parse_expression(unit_string)
