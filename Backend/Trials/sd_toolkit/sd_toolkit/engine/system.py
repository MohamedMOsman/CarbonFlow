"""
System dynamics model and simulation engine.

This module provides the main SystemModel class and SimulationEngine
for building, configuring, and running system dynamics simulations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any, Tuple
from collections import defaultdict
import warnings
from datetime import datetime, timedelta

from .elements import ModelElement, Stock, Flow, Connector, Auxiliary, Calculator, Delay
from ..core.units import Quantity, unit_registry
from ..data.loader import SpatioTemporalData


class SystemModel:
    """
    Main system dynamics model container.
    
    Manages model elements, their relationships, and provides methods
    for model configuration, validation, and simulation.
    """
    
    def __init__(self, name: str, description: str = "", time_units: str = "year"):
        """
        Initialize system model.
        
        Parameters:
        -----------
        name : str
            Name of the model
        description : str
            Description of the model
        time_units : str
            Units for time dimension
        """
        self.name = name
        self.description = description
        self.time_units = time_units
        self.created_at = datetime.now()
        
        # Model elements
        self.elements = {}  # id -> element mapping
        self.stocks = {}
        self.flows = {}
        self.connectors = {}
        self.auxiliaries = {}
        self.calculators = {}
        self.delays = {}
        
        # Model structure
        self.element_order = []  # Calculation order
        self.dependencies = defaultdict(list)  # element -> [dependencies]
        
        # Simulation settings
        self.time_horizon = 100
        self.dt = 0.25  # Default time step
        self.start_time = 0
        
        # Results storage
        self.results = None
        self.simulation_metadata = {}
    
    def add_element(self, element: ModelElement):
        """Add an element to the model."""
        if element.id in self.elements:
            warnings.warn(f"Element {element.name} already exists in model")
            return
        
        self.elements[element.id] = element
        
        # Add to specific collections
        if isinstance(element, Stock):
            self.stocks[element.id] = element
        elif isinstance(element, Flow):
            self.flows[element.id] = element
        elif isinstance(element, Connector):
            self.connectors[element.id] = element
        elif isinstance(element, Auxiliary):
            self.auxiliaries[element.id] = element
        elif isinstance(element, Calculator):
            self.calculators[element.id] = element
        elif isinstance(element, Delay):
            self.delays[element.id] = element
    
    def remove_element(self, element_id: str):
        """Remove an element from the model."""
        if element_id not in self.elements:
            warnings.warn(f"Element {element_id} not found in model")
            return
        
        element = self.elements[element_id]
        
        # Remove from specific collections
        if element_id in self.stocks:
            del self.stocks[element_id]
        elif element_id in self.flows:
            del self.flows[element_id]
        elif element_id in self.connectors:
            del self.connectors[element_id]
        elif element_id in self.auxiliaries:
            del self.auxiliaries[element_id]
        elif element_id in self.calculators:
            del self.calculators[element_id]
        elif element_id in self.delays:
            del self.delays[element_id]
        
        # Remove from main collection
        del self.elements[element_id]
        
        # Clean up dependencies
        if element_id in self.dependencies:
            del self.dependencies[element_id]
        
        # Remove from other elements' dependencies
        for deps in self.dependencies.values():
            if element_id in deps:
                deps.remove(element_id)
    
    def connect(self, from_element: Union[str, ModelElement], 
                to_element: Union[str, ModelElement]):
        """Connect two elements."""
        # Resolve element references
        if isinstance(from_element, str):
            from_element = self.elements.get(from_element)
        if isinstance(to_element, str):
            to_element = self.elements.get(to_element)
        
        if not from_element or not to_element:
            raise ValueError("Invalid element reference in connection")
        
        # Create connection
        from_element.connect_to(to_element)
        
        # Update dependencies
        self.dependencies[to_element.id].append(from_element.id)
    
    def validate_model(self) -> Dict[str, Any]:
        """
        Validate model structure and consistency.
        
        Returns:
        --------
        dict : Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check for isolated elements
        isolated_elements = []
        for element in self.elements.values():
            if not element.connections and element.id not in self.dependencies:
                isolated_elements.append(element.name)
        
        if isolated_elements:
            results['warnings'].append(
                f"Isolated elements found: {isolated_elements}"
            )
        
        # Check for circular dependencies
        try:
            self._calculate_execution_order()
        except ValueError as e:
            results['errors'].append(f"Circular dependency detected: {e}")
            results['valid'] = False
        
        # Check unit consistency
        unit_issues = self._check_unit_consistency()
        if unit_issues:
            results['warnings'].extend(unit_issues)
        
        # Model statistics
        results['statistics'] = {
            'total_elements': len(self.elements),
            'stocks': len(self.stocks),
            'flows': len(self.flows),
            'connectors': len(self.connectors),
            'auxiliaries': len(self.auxiliaries),
            'delays': len(self.delays)
        }
        
        return results
    
    def _calculate_execution_order(self) -> List[str]:
        """Calculate the order in which elements should be calculated."""
        # Topological sort to handle dependencies
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(element_id):
            if element_id in temp_visited:
                raise ValueError(f"Circular dependency involving {element_id}")
            if element_id in visited:
                return
            
            temp_visited.add(element_id)
            
            # Visit dependencies first
            for dep_id in self.dependencies.get(element_id, []):
                visit(dep_id)
            
            temp_visited.remove(element_id)
            visited.add(element_id)
            order.append(element_id)
        
        # Visit all elements
        for element_id in self.elements:
            if element_id not in visited:
                visit(element_id)
        
        self.element_order = order
        return order
    
    def _check_unit_consistency(self) -> List[str]:
        """Check for unit consistency issues."""
        issues = []
        
        # Check stock-flow unit consistency
        for stock in self.stocks.values():
            for flow in stock.inflows + stock.outflows:
                if stock.units and flow.units:
                    # Flow units should be stock_units/time_units
                    expected_flow_units = f"{stock.units}/{self.time_units}"
                    if flow.units != expected_flow_units:
                        issues.append(
                            f"Unit mismatch: {stock.name} ({stock.units}) "
                            f"and {flow.name} ({flow.units})"
                        )
        
        return issues
    
    def simulate(self, time_horizon: Optional[float] = None, 
                dt: Optional[float] = None, 
                start_time: Optional[float] = None,
                method: str = 'euler') -> pd.DataFrame:
        """
        Run model simulation.
        
        Parameters:
        -----------
        time_horizon : float, optional
            Total simulation time
        dt : float, optional
            Time step size
        start_time : float, optional
            Starting time
        method : str
            Integration method ('euler', 'rk4')
            
        Returns:
        --------
        pd.DataFrame : Simulation results
        """
        # Use provided values or defaults
        time_horizon = time_horizon or self.time_horizon
        dt = dt or self.dt
        start_time = start_time or self.start_time
        
        # Validate model before simulation
        validation = self.validate_model()
        if not validation['valid']:
            raise ValueError(f"Model validation failed: {validation['errors']}")
        
        # Calculate execution order
        self._calculate_execution_order()
        
        # Initialize simulation
        time_points = np.arange(start_time, start_time + time_horizon + dt, dt)
        n_steps = len(time_points)
        
        # Reset all elements
        for element in self.elements.values():
            if hasattr(element, 'reset'):
                element.reset()
        
        # Storage for results
        results_data = {
            'time': time_points,
        }

        # Add columns for each element - handle multidimensional elements
        multidimensional_elements = {}

        for element in self.elements.values():
            # Get initial value to determine shape
            if hasattr(element, 'current_value') and element.current_value is not None:
                initial_value = element.current_value
            elif hasattr(element, 'initial_value') and element.initial_value is not None:
                initial_value = element.initial_value
            else:
                # Default to scalar
                initial_value = 0.0

            # Create storage array with appropriate shape
            if isinstance(initial_value, np.ndarray):
                # Multidimensional element - store separately
                multidimensional_elements[element.name] = {
                    'shape': initial_value.shape,
                    'data': []
                }
                # Store total as scalar for DataFrame compatibility
                results_data[element.name] = np.zeros(n_steps)
            else:
                # Scalar element - use regular numpy array
                results_data[element.name] = np.zeros(n_steps)
        
        # Run simulation
        for i, t in enumerate(time_points):
            # Calculate elements in dependency order
            for element_id in self.element_order:
                element = self.elements[element_id]
                value = element.calculate(t, dt)

                # Store value appropriately based on type
                if isinstance(value, np.ndarray):
                    # Multidimensional value - store full array and total
                    if element.name in multidimensional_elements:
                        multidimensional_elements[element.name]['data'].append(value.copy())
                        results_data[element.name][i] = value.sum()  # Store total for DataFrame
                    else:
                        # This shouldn't happen, but handle gracefully
                        results_data[element.name][i] = value.sum()
                else:
                    # Scalar value
                    results_data[element.name][i] = value
        
        # Create results DataFrame with scalar data (including totals for multidimensional elements)
        self.results = pd.DataFrame(results_data)

        # Store multidimensional data separately
        self.multidimensional_results = {}
        for name, element_data in multidimensional_elements.items():
            self.multidimensional_results[name] = element_data['data']
        
        # Store simulation metadata
        self.simulation_metadata = {
            'time_horizon': time_horizon,
            'dt': dt,
            'start_time': start_time,
            'method': method,
            'n_steps': n_steps,
            'simulation_time': datetime.now()
        }
        
        return self.results

    def get_element_results(self, element_name: str) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Get results for a specific element, handling both scalar and multidimensional data.

        Parameters:
        -----------
        element_name : str
            Name of the element to get results for

        Returns:
        --------
        Union[np.ndarray, List[np.ndarray]]
            For scalar elements: 1D numpy array of values over time
            For multidimensional elements: List of numpy arrays, one for each time step
        """
        if element_name in self.results.columns:
            return self.results[element_name].values
        elif hasattr(self, 'multidimensional_results') and element_name in self.multidimensional_results:
            return self.multidimensional_results[element_name]
        else:
            raise KeyError(f"Element '{element_name}' not found in results")

    def get_multidimensional_summary(self, element_name: str) -> Dict[str, Any]:
        """
        Get summary statistics for a multidimensional element.

        Parameters:
        -----------
        element_name : str
            Name of the multidimensional element

        Returns:
        --------
        Dict[str, Any]
            Summary including total values over time, shape info, etc.
        """
        if not hasattr(self, 'multidimensional_results') or element_name not in self.multidimensional_results:
            raise KeyError(f"Multidimensional element '{element_name}' not found in results")

        data = self.multidimensional_results[element_name]

        # Calculate summary statistics
        totals = [arr.sum() if arr is not None else 0 for arr in data]
        shapes = [arr.shape if arr is not None else None for arr in data]

        return {
            'element_name': element_name,
            'time_points': len(data),
            'total_over_time': np.array(totals),
            'shapes': shapes,
            'initial_total': totals[0] if totals else 0,
            'final_total': totals[-1] if totals else 0,
            'data': data
        }
    
    def get_element_by_name(self, name: str) -> Optional[ModelElement]:
        """Get element by name."""
        for element in self.elements.values():
            if element.name == name:
                return element
        return None
    
    def get_results(self, element_names: Optional[List[str]] = None) -> pd.DataFrame:
        """Get simulation results for specific elements."""
        if self.results is None:
            raise ValueError("No simulation results available. Run simulate() first.")
        
        if element_names is None:
            return self.results
        
        # Include time column plus requested elements
        columns = ['time'] + [name for name in element_names if name in self.results.columns]
        return self.results[columns]
    
    def export_model(self, filepath: str):
        """Export model structure to file (simplified implementation)."""
        import json
        
        model_data = {
            'name': self.name,
            'description': self.description,
            'time_units': self.time_units,
            'created_at': self.created_at.isoformat(),
            'elements': {},
            'connections': []
        }
        
        # Export elements (simplified)
        for element in self.elements.values():
            model_data['elements'][element.id] = {
                'type': element.__class__.__name__,
                'name': element.name,
                'description': element.description,
                'units': element.units
            }
        
        # Export connections
        for element_id, deps in self.dependencies.items():
            for dep_id in deps:
                model_data['connections'].append([dep_id, element_id])
        
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)


class SimulationEngine:
    """
    Advanced simulation engine with multiple integration methods.
    
    Provides more sophisticated numerical integration methods and
    sensitivity analysis capabilities.
    """
    
    def __init__(self, model: SystemModel):
        """Initialize simulation engine with a model."""
        self.model = model
        self.integration_methods = {
            'euler': self._euler_step,
            'rk4': self._rk4_step,
            'adaptive': self._adaptive_step
        }
    
    def _euler_step(self, t: float, dt: float) -> Dict[str, float]:
        """Single Euler integration step."""
        values = {}
        for element_id in self.model.element_order:
            element = self.model.elements[element_id]
            values[element_id] = element.calculate(t, dt)
        return values
    
    def _rk4_step(self, t: float, dt: float) -> Dict[str, float]:
        """Single Runge-Kutta 4th order step (simplified implementation)."""
        # This is a simplified RK4 - full implementation would be more complex
        return self._euler_step(t, dt)
    
    def _adaptive_step(self, t: float, dt: float) -> Dict[str, float]:
        """Adaptive step size integration (simplified implementation)."""
        # This would implement adaptive step size control
        return self._euler_step(t, dt)
    
    def run_sensitivity_analysis(self, parameter_ranges: Dict[str, Tuple[float, float]], 
                               n_samples: int = 100) -> Dict[str, Any]:
        """
        Run Monte Carlo sensitivity analysis.
        
        Parameters:
        -----------
        parameter_ranges : dict
            Parameter names and their (min, max) ranges
        n_samples : int
            Number of Monte Carlo samples
            
        Returns:
        --------
        dict : Sensitivity analysis results
        """
        # This would implement Monte Carlo sensitivity analysis
        # Simplified placeholder implementation
        results = {
            'parameter_ranges': parameter_ranges,
            'n_samples': n_samples,
            'sensitivity_indices': {},
            'correlation_matrix': None
        }
        
        return results
