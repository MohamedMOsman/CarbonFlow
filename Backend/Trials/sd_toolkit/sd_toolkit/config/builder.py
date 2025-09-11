"""
YAML-based system dynamics model builder.

This module provides functionality to create system dynamics models
from YAML configuration files.
"""

import yaml
import numpy as np
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

from ..engine.system import SystemModel
from ..engine.elements import Stock, Flow, Auxiliary, Calculator
from .registry import rate_registry


class YAMLSystemBuilder:
    """Builder for creating system dynamics models from YAML configuration."""
    
    def __init__(self):
        """Initialize the YAML system builder."""
        self._constants = {}
        self._dimensions = {}
        self._functions = {}
    
    def build_from_file(self, filepath: Union[str, Path]) -> SystemModel:
        """
        Build a system model from a YAML file.
        
        Parameters:
        -----------
        filepath : str or Path
            Path to the YAML configuration file
            
        Returns:
        --------
        SystemModel : The constructed model
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"YAML file not found: {filepath}")
        
        with open(filepath, 'r') as file:
            config = yaml.safe_load(file)
        
        return self.build_from_dict(config)
    
    def build_from_dict(self, config: Dict[str, Any]) -> SystemModel:
        """
        Build a system model from a configuration dictionary.
        
        Parameters:
        -----------
        config : dict
            Configuration dictionary
            
        Returns:
        --------
        SystemModel : The constructed model
        """
        # Extract model metadata
        model_config = config.get('model', {})
        model_name = model_config.get('name', 'Untitled Model')
        description = model_config.get('description', '')
        time_horizon = model_config.get('time_horizon', 50)
        dt = model_config.get('dt', 0.25)
        time_units = model_config.get('time_units', 'year')
        
        # Create model
        model = SystemModel(model_name, time_units=time_units)
        model.description = description
        model.time_horizon = time_horizon
        model.dt = dt
        
        # Process constants
        self._constants = config.get('constants', {})
        
        # Process dimensions
        self._dimensions = config.get('dimensions', {})
        model.dimensions = self._dimensions.copy()  # Store in model for access
        
        # Process functions
        self._functions = config.get('functions', {})
        
        # Process elements
        elements_config = config.get('elements', {})
        elements = {}
        
        # Create stocks
        stocks_config = elements_config.get('stocks', [])
        for stock_config in stocks_config:
            stock = self._create_stock(stock_config)
            elements[stock.name] = stock
            model.add_element(stock)
        
        # Create flows
        flows_config = elements_config.get('flows', [])
        for flow_config in flows_config:
            flow = self._create_flow(flow_config, elements)
            elements[flow.name] = flow
            model.add_element(flow)
        
        # Create auxiliaries
        auxiliaries_config = elements_config.get('auxiliaries', [])
        for aux_config in auxiliaries_config:
            auxiliary = self._create_auxiliary(aux_config, elements)
            elements[auxiliary.name] = auxiliary
            model.add_element(auxiliary)

        # Create calculators
        calculators_config = elements_config.get('calculators', [])
        for calc_config in calculators_config:
            calculator = self._create_calculator(calc_config, elements, model)
            elements[calculator.name] = calculator
            model.add_element(calculator)
        
        # Process connections
        connections_config = config.get('connections', [])
        self._create_connections(connections_config, elements)
        
        return model
    
    def _resolve_value(self, value: Any) -> Any:
        """Resolve a value that might be a constant reference."""
        if isinstance(value, str) and value.startswith('$'):
            constant_name = value[1:]  # Remove $ prefix
            if constant_name in self._constants:
                resolved = self._constants[constant_name]
                # If the resolved value is a nested list, convert to numpy array
                if isinstance(resolved, list):
                    return np.array(resolved)
                return resolved
            else:
                raise ValueError(f"Constant '{constant_name}' not found")
        elif isinstance(value, dict) and 'array' in value:
            # Handle multidimensional arrays
            return self._create_multidimensional_array(value)
        elif isinstance(value, list):
            # Handle lists (might contain references or be multidimensional)
            resolved_list = [self._resolve_value(item) for item in value]
            # Convert to numpy array if it's a nested structure
            try:
                return np.array(resolved_list)
            except:
                return resolved_list
        else:
            return value
    
    def _create_multidimensional_array(self, array_config: Dict[str, Any]) -> np.ndarray:
        """Create a multidimensional array from configuration."""
        if 'shape' in array_config:
            shape = array_config['shape']
            if 'values' in array_config:
                values = array_config['values']
                if isinstance(values, str) and values.startswith('$'):
                    values = self._resolve_value(values)
                try:
                    return np.array(values).reshape(shape)
                except ValueError as e:
                    print(f"Warning: Could not reshape array to {shape}: {e}")
                    return np.array(values)
            elif 'fill_value' in array_config:
                fill_value = self._resolve_value(array_config['fill_value'])
                return np.full(shape, fill_value)
            else:
                return np.zeros(shape)
        elif 'values' in array_config:
            values = self._resolve_value(array_config['values'])
            return np.array(values)
        else:
            # If neither shape nor values specified, try to extract from array_config itself
            if isinstance(array_config.get('array'), dict):
                return self._create_multidimensional_array(array_config['array'])
            else:
                raise ValueError("Array configuration must specify 'shape' or 'values'")
    
    def _create_stock(self, config: Dict[str, Any]) -> Stock:
        """Create a stock element from configuration."""
        name = config['name']
        initial_value = self._resolve_value(config.get('initial_value', 0))
        units = config.get('units', None)
        spatial_dims = config.get('spatial_dims', None)
        min_value = config.get('min_value', None)
        max_value = config.get('max_value', None)
        description = config.get('description', '')
        
        return Stock(
            name=name,
            initial_value=initial_value,
            units=units,
            spatial_dims=spatial_dims,
            min_value=min_value,
            max_value=max_value,
            description=description
        )
    
    def _create_flow(self, config: Dict[str, Any], elements: Dict[str, Any]) -> Flow:
        """Create a flow element from configuration."""
        name = config['name']
        units = config.get('units', None)
        spatial_dims = config.get('spatial_dims', None)
        description = config.get('description', '')

        # Handle rate specification
        if 'rate' in config:
            rate_spec = config['rate']
            if isinstance(rate_spec, str):
                # Check if it's a constant reference (starts with $)
                if rate_spec.startswith('$'):
                    # Resolve the constant reference to get the actual value
                    try:
                        resolved_rate = self._resolve_value(rate_spec)
                        if isinstance(resolved_rate, (int, float)):
                            rate_function = resolved_rate
                        else:
                            raise ValueError(f"Resolved rate '{rate_spec}' is not a numeric value: {resolved_rate}")
                    except Exception as e:
                        print(f"Warning: Error resolving rate constant '{rate_spec}' for flow '{name}': {e}")
                        # Fallback to simple constant rate
                        rate_function = 0.01
                else:
                    # Function name from registry or custom function
                    try:
                        rate_function = self._create_rate_function(rate_spec, config.get('parameters', {}))
                    except Exception as e:
                        print(f"Warning: Error creating rate function '{rate_spec}' for flow '{name}': {e}")
                        # Fallback to simple constant rate
                        rate_function = 0.01
            elif isinstance(rate_spec, (int, float)):
                # Constant rate
                rate_function = rate_spec
            else:
                raise ValueError(f"Invalid rate specification for flow '{name}'")
        else:
            rate_function = 0.0

        flow = Flow(
            name=name,
            rate=rate_function,
            units=units,
            spatial_dims=spatial_dims,
            description=description
        )

        # Add resolved parameters to the flow
        if 'parameters' in config:
            for param_name, param_value in config['parameters'].items():
                try:
                    resolved_value = self._resolve_value(param_value)
                    flow.add_parameter(param_name, resolved_value)
                except Exception as e:
                    print(f"Warning: Could not resolve flow parameter '{param_name}' = '{param_value}': {e}")
                    flow.add_parameter(param_name, param_value)

        return flow
    
    def _create_auxiliary(self, config: Dict[str, Any], elements: Dict[str, Any]) -> Auxiliary:
        """Create an auxiliary element from configuration."""
        name = config['name']
        units = config.get('units', None)
        spatial_dims = config.get('spatial_dims', None)
        description = config.get('description', '')

        # Create calculation function
        if 'calculation' in config:
            calc_spec = config['calculation']
            if isinstance(calc_spec, str):
                # Function name from registry or custom function
                calc_function = self._create_calculation_function(calc_spec, config.get('parameters', {}))
            else:
                raise ValueError(f"Invalid calculation specification for auxiliary '{name}'")
        else:
            calc_function = lambda time, dt, deps, **kwargs: 0.0

        auxiliary = Auxiliary(
            name=name,
            calculation_function=calc_function,
            units=units,
            spatial_dims=spatial_dims,
            description=description
        )

        # Add resolved parameters to the auxiliary
        if 'parameters' in config:
            for param_name, param_value in config['parameters'].items():
                try:
                    resolved_value = self._resolve_value(param_value)
                    auxiliary.add_parameter(param_name, resolved_value)
                except Exception as e:
                    print(f"Warning: Could not resolve auxiliary parameter '{param_name}' = '{param_value}': {e}")
                    auxiliary.add_parameter(param_name, param_value)

        return auxiliary

    def _create_calculator(self, config: Dict[str, Any], elements: Dict[str, Any], model) -> Calculator:
        """Create a calculator element from configuration."""
        name = config['name']
        expression = config.get('expression', '0')
        units = config.get('units', None)
        spatial_dims = config.get('spatial_dims', None)
        description = config.get('description', '')

        calculator = Calculator(
            name=name,
            expression=expression,
            units=units,
            spatial_dims=spatial_dims,
            description=description
        )

        # Add resolved parameters to the calculator
        if 'parameters' in config:
            for param_name, param_value in config['parameters'].items():
                try:
                    resolved_value = self._resolve_value(param_value)
                    calculator.add_parameter(param_name, resolved_value)
                except Exception as e:
                    print(f"Warning: Could not resolve calculator parameter '{param_name}' = '{param_value}': {e}")
                    calculator.add_parameter(param_name, param_value)

        # Handle dependencies specified in config
        if 'dependencies' in config:
            for dep_name in config['dependencies']:
                if dep_name in elements:
                    dep_element = elements[dep_name]
                    calculator.add_dependency(dep_element)
                    # Also register in model dependencies for execution order
                    model.dependencies[calculator.id].append(dep_element.id)
                else:
                    print(f"Warning: Dependency '{dep_name}' not found for calculator '{name}'")

        # Auto-resolve dependencies from expression if not explicitly specified
        if 'dependencies' not in config:
            self._auto_resolve_calculator_dependencies(calculator, elements, model)

        return calculator

    def _auto_resolve_calculator_dependencies(self, calculator: Calculator, elements: Dict[str, Any], model):
        """Automatically resolve calculator dependencies from expression variables."""
        for var_name in calculator.dependency_names:
            # Try exact name match first
            if var_name in elements:
                dep_element = elements[var_name]
                calculator.add_dependency(dep_element)
                # Also register in model dependencies for execution order
                model.dependencies[calculator.id].append(dep_element.id)
                continue

            # Try name variations (spaces, underscores, hyphens)
            variations = [
                var_name.replace('_', ' '),
                var_name.replace('_', '-'),
                var_name.replace(' ', '_'),
                var_name.replace('-', '_'),
                var_name.replace(' ', '-'),
                var_name.replace('-', ' ')
            ]

            found = False
            for variation in variations:
                if variation in elements:
                    dep_element = elements[variation]
                    calculator.add_dependency(dep_element)
                    # Also register in model dependencies for execution order
                    model.dependencies[calculator.id].append(dep_element.id)
                    found = True
                    break

            if not found:
                print(f"Warning: Could not resolve dependency '{var_name}' for calculator '{calculator.name}'")
                print(f"Available elements: {list(elements.keys())}")

    def _create_rate_function(self, function_name: str, parameters: Dict[str, Any]):
        """Create a rate function from registry."""
        if function_name in self._functions:
            # Custom function defined in YAML
            return self._create_custom_function(self._functions[function_name], parameters)
        else:
            # Function from registry
            base_function = rate_registry.get(function_name)
            resolved_params = {k: self._resolve_value(v) for k, v in parameters.items()}
            
            def rate_function(time: float, dt: float, flow, **kwargs):
                # Merge resolved parameters with runtime kwargs
                all_kwargs = {**resolved_params, **kwargs}
                return base_function(time, dt, flow, **all_kwargs)
            
            return rate_function
    
    def _create_calculation_function(self, function_name: str, parameters: Dict[str, Any]):
        """Create a calculation function for auxiliaries."""
        if function_name in self._functions:
            # Custom function defined in YAML
            return self._create_custom_function(self._functions[function_name], parameters)
        else:
            # Simple calculation (could be extended)
            resolved_params = {k: self._resolve_value(v) for k, v in parameters.items()}
            
            def calc_function(time: float, dt: float, dependencies: Dict, **kwargs):
                # Basic calculation - could be extended for more complex expressions
                return resolved_params.get('value', 0.0)
            
            return calc_function
    
    def _create_custom_function(self, function_config: Dict[str, Any], parameters: Dict[str, Any]):
        """Create a custom function from YAML configuration."""
        expression = function_config.get('expression', '')
        dependencies = function_config.get('dependencies', [])

        # Merge function-level parameters with flow-level parameters
        all_parameters = {**function_config.get('parameters', {}), **parameters}

        # Resolve parameters at function creation time (not call time)
        resolved_parameters = {}
        for key, value in all_parameters.items():
            try:
                resolved_value = self._resolve_value(value)
                resolved_parameters[key] = resolved_value

            except Exception as e:
                print(f"Warning: Could not resolve parameter '{key}' = '{value}': {e}")
                print(f"Available constants: {list(self._constants.keys())}")
                # For debugging, check if it's a string with $ prefix
                if isinstance(value, str) and value.startswith('$'):
                    constant_name = value[1:]
                    if constant_name in self._constants:
                        print(f"  Constant '{constant_name}' found with value: {self._constants[constant_name]}")
                        resolved_parameters[key] = self._constants[constant_name]
                    else:
                        print(f"  Constant '{constant_name}' not found in constants")
                        resolved_parameters[key] = value  # Keep original if resolution fails
                else:
                    resolved_parameters[key] = value  # Keep original if resolution fails

        # This is a simplified implementation
        # In practice, you might want to use a more sophisticated expression parser
        def custom_function(time: float, dt: float, context, **kwargs):
            # Use pre-resolved parameters (don't let kwargs override them)
            local_vars = {'time': time, 'dt': dt}
            local_vars.update(kwargs)  # Add kwargs first
            local_vars.update(resolved_parameters)  # Then override with resolved parameters

            # Add numpy for mathematical operations
            local_vars['np'] = np

            # Handle different context types and add dependencies
            for dep_name in dependencies:
                dep_value = None

                # Method 1: Check if context is a dictionary-like object
                if hasattr(context, 'items') and dep_name in context:
                    dep_value = context[dep_name]

                # Method 2: Check if context has the attribute directly
                elif hasattr(context, dep_name):
                    dep_value = getattr(context, dep_name)

                # Method 3: For flows, check connected stocks (population dependency)
                elif hasattr(context, 'from_stock') and context.from_stock is not None and dep_name == 'population':
                    dep_value = context.from_stock.current_value

                # Method 4: Check if it's passed in kwargs
                elif dep_name in kwargs:
                    dep_value = kwargs[dep_name]

                # Method 5: Check if it's in the parameters
                elif dep_name in parameters:
                    dep_value = parameters[dep_name]

                # If we found a value, use it
                if dep_value is not None:
                    local_vars[dep_name] = dep_value
                else:
                    # Provide reasonable defaults for missing dependencies
                    if dep_name == 'population':
                        # For multidimensional models, create a small default array
                        local_vars[dep_name] = np.ones((3, 3, 2)) * 1000.0  # Default multidimensional population
                    elif dep_name == 'climate_stress':
                        local_vars[dep_name] = 0.1  # Default climate stress
                    elif 'multiplier' in dep_name.lower():
                        local_vars[dep_name] = 1.0  # Default multiplier
                    else:
                        local_vars[dep_name] = 0.0  # Generic default

            # Simple expression evaluation (could be enhanced)
            try:
                result = eval(expression, {"__builtins__": {}, "np": np}, local_vars)
                return result if result is not None else 0.0
            except Exception as e:
                print(f"Error evaluating expression '{expression}': {e}")
                print(f"Available variables: {list(local_vars.keys())}")
                # Print types and shapes for debugging
                for var_name, var_value in local_vars.items():
                    if isinstance(var_value, np.ndarray):
                        print(f"  {var_name}: numpy array, shape={var_value.shape}, dtype={var_value.dtype}")
                    else:
                        print(f"  {var_name}: {type(var_value).__name__}, value={var_value}")
                return 0.0

        return custom_function
    
    def _create_connections(self, connections_config: List[Dict[str, Any]], elements: Dict[str, Any]):
        """Create connections between elements."""
        for connection in connections_config:
            from_element_name = connection['from']
            to_element_name = connection['to']
            connection_type = connection['type']
            
            if from_element_name not in elements:
                raise ValueError(f"Element '{from_element_name}' not found")
            if to_element_name not in elements:
                raise ValueError(f"Element '{to_element_name}' not found")
            
            from_element = elements[from_element_name]
            to_element = elements[to_element_name]
            
            if connection_type == 'inflow':
                if hasattr(to_element, 'add_inflow'):
                    to_element.add_inflow(from_element)
                    # Set the from_stock reference for the flow to access stock data
                    if hasattr(from_element, 'from_stock'):
                        from_element.from_stock = to_element
                else:
                    raise ValueError(f"Element '{to_element_name}' cannot have inflows")
            elif connection_type == 'outflow':
                if hasattr(to_element, 'add_outflow'):
                    to_element.add_outflow(from_element)
                    # Set the from_stock reference for the flow to access stock data
                    if hasattr(from_element, 'from_stock'):
                        from_element.from_stock = to_element
                else:
                    raise ValueError(f"Element '{to_element_name}' cannot have outflows")
            elif connection_type == 'dependency':
                if hasattr(to_element, 'add_dependency'):
                    to_element.add_dependency(from_element)
                else:
                    raise ValueError(f"Element '{to_element_name}' cannot have dependencies")
            elif connection_type == 'internal_flow':
                # Internal flows represent transitions within the same stock
                # For now, we'll treat them as dependencies
                print(f"Note: Internal flow connection from '{from_element_name}' to '{to_element_name}' treated as dependency")
                if hasattr(to_element, 'add_dependency'):
                    to_element.add_dependency(from_element)
                else:
                    print(f"Warning: Element '{to_element_name}' cannot have internal flow dependencies")
            else:
                raise ValueError(f"Unknown connection type: {connection_type}")
