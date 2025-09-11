"""
Core system dynamics modeling elements.

This module defines the fundamental building blocks of system dynamics models:
stocks, flows, connectors, and auxiliary variables with unit awareness and
spatiotemporal capabilities.
"""

import numpy as np
import re
import warnings
from typing import Union, Dict, List, Optional, Callable, Any
from abc import ABC, abstractmethod
import uuid

from ..core.units import Quantity, unit_registry, DimensionalAnalysis
from ..data.loader import SpatioTemporalData


class ExpressionUnitValidator:
    """
    Validates unit consistency in calculator expressions.

    Parses arithmetic expressions and checks that operations are dimensionally consistent.
    """

    def __init__(self):
        """Initialize the validator with dimensional analysis tools."""
        self.dim_analysis = DimensionalAnalysis()
        self.ureg = unit_registry.ureg

    def validate_expression(self, expression: str, dependencies: Dict[str, str],
                          expected_units: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate the dimensional consistency of an expression.

        Parameters:
        -----------
        expression : str
            The arithmetic expression to validate
        dependencies : Dict[str, str]
            Mapping of variable names to their units
        expected_units : str, optional
            Expected units of the result

        Returns:
        --------
        Dict[str, Any]
            Validation result with 'valid', 'inferred_units', 'errors', 'warnings'
        """
        result = {
            'valid': True,
            'inferred_units': None,
            'errors': [],
            'warnings': []
        }

        try:
            # Parse the expression to identify operations
            tokens = self._tokenize_expression(expression)

            # Validate each operation in the expression
            inferred_units = self._validate_tokens(tokens, dependencies, result)

            result['inferred_units'] = str(inferred_units) if inferred_units else None

            # Check against expected units if provided
            if expected_units and inferred_units:
                try:
                    expected_quantity = self.ureg.Quantity(1, expected_units)
                    inferred_quantity = self.ureg.Quantity(1, inferred_units)

                    if not self.dim_analysis.check_equation_consistency(expected_quantity, inferred_quantity):
                        result['errors'].append(
                            f"Unit mismatch: expression yields '{inferred_units}' but expected '{expected_units}'"
                        )
                        result['valid'] = False
                except Exception as e:
                    result['warnings'].append(f"Could not compare units: {e}")

        except Exception as e:
            result['errors'].append(f"Expression validation failed: {e}")
            result['valid'] = False

        return result

    def _tokenize_expression(self, expression: str) -> List[Dict[str, Any]]:
        """
        Tokenize an arithmetic expression into operators and operands.

        Returns list of tokens with 'type' and 'value' keys.
        """
        # Simple tokenizer for basic arithmetic expressions
        # This handles +, -, *, /, parentheses, numbers, and variables

        token_pattern = r'(\d+\.?\d*|\w+|[+\-*/()]|\s+)'
        tokens = []

        for match in re.finditer(token_pattern, expression):
            token = match.group(1).strip()
            if not token:
                continue

            if re.match(r'\d+\.?\d*', token):
                tokens.append({'type': 'number', 'value': float(token)})
            elif token in ['+', '-', '*', '/', '(', ')']:
                tokens.append({'type': 'operator', 'value': token})
            elif re.match(r'\w+', token):
                # Check if it's a numpy function
                if token.startswith('np.'):
                    tokens.append({'type': 'function', 'value': token})
                else:
                    tokens.append({'type': 'variable', 'value': token})

        return tokens

    def _validate_tokens(self, tokens: List[Dict[str, Any]], dependencies: Dict[str, str],
                        result: Dict[str, Any]) -> Optional[str]:
        """
        Validate the dimensional consistency of tokenized expression.

        This is a simplified validator that handles basic arithmetic operations.
        """
        try:
            # For now, implement basic validation for simple expressions
            # This can be extended to handle more complex expressions with proper parsing

            variables_in_expr = [t['value'] for t in tokens if t['type'] == 'variable']

            # Check that all variables have known units
            for var in variables_in_expr:
                if var not in dependencies:
                    result['warnings'].append(f"Unknown variable '{var}' in expression")

            # For simple cases, try to infer units
            if len(variables_in_expr) == 1:
                # Single variable expression
                var = variables_in_expr[0]
                if var in dependencies:
                    return dependencies[var]

            elif len(variables_in_expr) == 2:
                # Two variable expression - check for common patterns
                var1, var2 = variables_in_expr[0], variables_in_expr[1]
                if var1 in dependencies and var2 in dependencies:
                    units1, units2 = dependencies[var1], dependencies[var2]

                    # Look for operators between variables
                    operators = [t['value'] for t in tokens if t['type'] == 'operator' and t['value'] in ['+', '-', '*', '/']]

                    if '+' in operators or '-' in operators:
                        # Addition/subtraction requires same units
                        try:
                            q1 = self.ureg.Quantity(1, units1)
                            q2 = self.ureg.Quantity(1, units2)
                            if not self.dim_analysis.check_equation_consistency(q1, q2):
                                result['errors'].append(
                                    f"Cannot add/subtract '{units1}' and '{units2}' - incompatible units"
                                )
                                result['valid'] = False
                            else:
                                return units1  # Result has same units as operands
                        except Exception as e:
                            result['warnings'].append(f"Could not validate addition/subtraction: {e}")

                    elif '*' in operators:
                        # Multiplication
                        try:
                            q1 = self.ureg.Quantity(1, units1)
                            q2 = self.ureg.Quantity(1, units2)
                            result_q = q1 * q2
                            return str(result_q.units)
                        except Exception as e:
                            result['warnings'].append(f"Could not validate multiplication: {e}")

                    elif '/' in operators:
                        # Division
                        try:
                            q1 = self.ureg.Quantity(1, units1)
                            q2 = self.ureg.Quantity(1, units2)
                            result_q = q1 / q2
                            return str(result_q.units)
                        except Exception as e:
                            result['warnings'].append(f"Could not validate division: {e}")

            # If we can't infer, return None but don't mark as invalid
            result['warnings'].append("Could not infer units from complex expression")
            return None

        except Exception as e:
            result['errors'].append(f"Token validation failed: {e}")
            result['valid'] = False
            return None


class ModelElement(ABC):
    """
    Abstract base class for all system dynamics model elements.
    
    Provides common functionality for naming, identification, units,
    and spatial/temporal properties.
    """
    
    def __init__(self, name: str, units: Optional[str] = None, 
                 spatial_dims: Optional[tuple] = None, description: str = ""):
        """
        Initialize model element.
        
        Parameters:
        -----------
        name : str
            Name of the element
        units : str, optional
            Units of the element
        spatial_dims : tuple, optional
            Spatial dimensions (e.g., ('x', 'y'))
        description : str
            Description of the element
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.units = units
        self.spatial_dims = spatial_dims or ()
        self.connections = []  # Elements connected to this one
        self.metadata = {}
    
    def connect_to(self, other_element):
        """Connect this element to another element."""
        if other_element not in self.connections:
            self.connections.append(other_element)
    
    def disconnect_from(self, other_element):
        """Disconnect this element from another element."""
        if other_element in self.connections:
            self.connections.remove(other_element)
    
    @abstractmethod
    def calculate(self, time: float, dt: float, **kwargs) -> Union[float, np.ndarray]:
        """Calculate the value of this element at a given time."""
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', units='{self.units}')"


class Stock(ModelElement):
    """
    Stock (level) element in system dynamics.
    
    Represents accumulations in the system - things that can be measured
    at a point in time (e.g., population, inventory, carbon in atmosphere).
    """
    
    def __init__(self, name: str, initial_value: Union[float, np.ndarray] = 0.0,
                 units: Optional[str] = None, spatial_dims: Optional[tuple] = None,
                 min_value: Optional[float] = None, max_value: Optional[float] = None,
                 description: str = ""):
        """
        Initialize stock element.
        
        Parameters:
        -----------
        name : str
            Name of the stock
        initial_value : float or array
            Initial value of the stock
        units : str, optional
            Units of the stock
        spatial_dims : tuple, optional
            Spatial dimensions
        min_value : float, optional
            Minimum allowed value
        max_value : float, optional
            Maximum allowed value
        description : str
            Description of the stock
        """
        super().__init__(name, units, spatial_dims, description)
        
        self.initial_value = initial_value
        self.current_value = initial_value
        self.min_value = min_value
        self.max_value = max_value
        
        # Track inflows and outflows
        self.inflows = []
        self.outflows = []
        
        # History for tracking changes over time
        self.history = {'time': [], 'value': []}
    
    def add_inflow(self, flow):
        """Add an inflow to this stock."""
        if flow not in self.inflows:
            self.inflows.append(flow)
            flow.connect_to(self)
    
    def add_outflow(self, flow):
        """Add an outflow from this stock."""
        if flow not in self.outflows:
            self.outflows.append(flow)
            flow.connect_to(self)
    
    def calculate(self, time: float, dt: float, **kwargs) -> Union[float, np.ndarray]:
        """Calculate stock value using Euler integration."""
        # Calculate net flow
        net_inflow = sum(flow.calculate(time, dt, **kwargs) for flow in self.inflows)
        net_outflow = sum(flow.calculate(time, dt, **kwargs) for flow in self.outflows)
        net_flow = net_inflow - net_outflow
        
        # Update stock using Euler integration
        new_value = self.current_value + net_flow * dt
        
        # Apply constraints
        if self.min_value is not None:
            new_value = np.maximum(new_value, self.min_value)
        if self.max_value is not None:
            new_value = np.minimum(new_value, self.max_value)
        
        self.current_value = new_value
        
        # Record history
        self.history['time'].append(time)
        self.history['value'].append(new_value)
        
        return new_value
    
    def reset(self):
        """Reset stock to initial conditions."""
        self.current_value = self.initial_value
        self.history = {'time': [], 'value': []}


class Flow(ModelElement):
    """
    Flow (rate) element in system dynamics.
    
    Represents activities or processes that change stocks over time
    (e.g., birth rate, production rate, decay rate).
    """
    
    def __init__(self, name: str, rate: Union[float, Callable] = 0.0,
                 units: Optional[str] = None, spatial_dims: Optional[tuple] = None,
                 description: str = ""):
        """
        Initialize flow element.
        
        Parameters:
        -----------
        name : str
            Name of the flow
        rate : float or callable
            Flow rate (constant) or function to calculate rate
        units : str, optional
            Units of the flow (typically per time unit)
        spatial_dims : tuple, optional
            Spatial dimensions
        description : str
            Description of the flow
        """
        super().__init__(name, units, spatial_dims, description)
        
        self.rate = rate
        self.from_stock = None
        self.to_stock = None

        # Dependencies (other elements this flow depends on)
        self.dependencies = []

        # Parameters for rate calculation
        self.parameters = {}

        # Current calculated value
        self.current_value = 0.0

        # History
        self.history = {'time': [], 'value': []}
    
    def set_rate_function(self, rate_function: Callable):
        """Set a function to calculate the flow rate dynamically."""
        self.rate = rate_function
    
    def add_parameter(self, name: str, value: Any):
        """Add a parameter for rate calculation."""
        self.parameters[name] = value

    def add_dependency(self, element: 'ModelElement'):
        """Add a dependency on another model element."""
        if element not in self.dependencies:
            self.dependencies.append(element)
            element.connect_to(self)

    def calculate(self, time: float, dt: float, **kwargs) -> Union[float, np.ndarray]:
        """Calculate flow value at given time."""
        # Gather values from dependencies
        dependency_values = {
            dep.name: dep.current_value for dep in self.dependencies
        }

        # Merge dependency values with kwargs
        all_kwargs = {**kwargs, **dependency_values, **self.parameters}

        if callable(self.rate):
            # Dynamic rate calculation
            flow_value = self.rate(time, dt, self, **all_kwargs)
        else:
            # Constant rate
            flow_value = self.rate

        # If connected to a stock, rate might depend on stock level
        if self.from_stock is not None:
            if isinstance(flow_value, (int, float)):
                flow_value = flow_value * self.from_stock.current_value

        # Update current_value so calculators can access it
        self.current_value = flow_value

        # Record history
        self.history['time'].append(time)
        self.history['value'].append(flow_value)

        return flow_value

    def reset(self):
        """Reset flow to initial conditions."""
        # Don't reset current_value to 0.0 - flows should maintain their calculated values
        # Only reset history
        self.history = {'time': [], 'value': []}


class Connector(ModelElement):
    """
    Connector element for information links in system dynamics.
    
    Represents information flows that don't directly change stocks
    but influence rates and decisions.
    """
    
    def __init__(self, name: str, source_element: ModelElement,
                 target_element: ModelElement, 
                 transform_function: Optional[Callable] = None,
                 units: Optional[str] = None, description: str = ""):
        """
        Initialize connector element.
        
        Parameters:
        -----------
        name : str
            Name of the connector
        source_element : ModelElement
            Element providing the information
        target_element : ModelElement
            Element receiving the information
        transform_function : callable, optional
            Function to transform the information
        units : str, optional
            Units of the information
        description : str
            Description of the connector
        """
        super().__init__(name, units, description=description)
        
        self.source_element = source_element
        self.target_element = target_element
        self.transform_function = transform_function or (lambda x: x)
        
        # Connect elements
        source_element.connect_to(self)
        self.connect_to(target_element)
    
    def calculate(self, time: float, dt: float, **kwargs) -> Union[float, np.ndarray]:
        """Calculate connector value by transforming source information."""
        source_value = self.source_element.current_value
        return self.transform_function(source_value)


class Auxiliary(ModelElement):
    """
    Auxiliary variable in system dynamics.
    
    Represents intermediate calculations or constants that help
    clarify model structure and calculations.
    """
    
    def __init__(self, name: str, calculation_function: Callable,
                 units: Optional[str] = None, spatial_dims: Optional[tuple] = None,
                 description: str = ""):
        """
        Initialize auxiliary variable.

        Parameters:
        -----------
        name : str
            Name of the auxiliary
        calculation_function : callable
            Function to calculate auxiliary value
        units : str, optional
            Units of the auxiliary
        spatial_dims : tuple, optional
            Spatial dimensions
        description : str
            Description of the auxiliary
        """
        super().__init__(name, units, spatial_dims, description)

        self.calculation_function = calculation_function
        self.current_value = 0.0

        # Dependencies (other elements this auxiliary depends on)
        self.dependencies = []

        # Parameters for calculation
        self.parameters = {}

        # History
        self.history = {'time': [], 'value': []}
    
    def add_parameter(self, name: str, value: Any):
        """Add a parameter for calculation."""
        self.parameters[name] = value

    def add_dependency(self, element: ModelElement):
        """Add a dependency on another model element."""
        if element not in self.dependencies:
            self.dependencies.append(element)
            element.connect_to(self)
    
    def calculate(self, time: float, dt: float, **kwargs) -> Union[float, np.ndarray]:
        """Calculate auxiliary value using its calculation function."""
        # Gather values from dependencies
        dependency_values = {
            dep.name: dep.current_value for dep in self.dependencies
        }

        # Merge dependency values with parameters and kwargs
        all_kwargs = {**kwargs, **dependency_values, **self.parameters}

        # Calculate value
        self.current_value = self.calculation_function(
            time, dt, dependency_values, **all_kwargs
        )

        # Record history
        self.history['time'].append(time)
        self.history['value'].append(self.current_value)

        return self.current_value


class Calculator(ModelElement):
    """
    Calculator element in system dynamics.

    Represents arithmetic calculations that combine other model elements
    (stocks, flows, constants, other calculators) using basic operations.
    Supports expressions like: net_flow = inflow - outflow
    """

    def __init__(self, name: str, expression: str,
                 units: Optional[str] = None, spatial_dims: Optional[tuple] = None,
                 description: str = ""):
        """
        Initialize calculator element.

        Parameters:
        -----------
        name : str
            Name of the calculator
        expression : str
            Arithmetic expression (e.g., "stock_a + flow_b - constant_c")
        units : str, optional
            Units of the calculated result
        spatial_dims : tuple, optional
            Spatial dimensions
        description : str
            Description of the calculator
        """
        super().__init__(name, units, spatial_dims, description)

        self.expression = expression
        self.current_value = 0.0

        # Dependencies (other elements this calculator depends on)
        self.dependencies = []

        # Parameters for calculation
        self.parameters = {}

        # History for tracking changes over time
        self.history = {'time': [], 'value': []}

        # Unit validation
        self.unit_validator = ExpressionUnitValidator()
        self.unit_validation_enabled = True
        self.strict_unit_validation = False  # Default to warnings, not exceptions
        self.last_validation_result = None

        # Parse expression to identify dependencies
        self._parse_dependencies()

    def _parse_dependencies(self):
        """Parse the expression to identify variable names (dependencies)."""
        import re

        # Find all variable names in the expression (alphanumeric + underscore)
        # Exclude Python keywords and numpy functions
        excluded_names = {
            'np', 'time', 'dt', 'and', 'or', 'not', 'if', 'else', 'elif',
            'for', 'while', 'def', 'class', 'import', 'from', 'as', 'in',
            'is', 'True', 'False', 'None', 'abs', 'min', 'max', 'sum',
            'len', 'range', 'int', 'float', 'str', 'list', 'dict', 'set'
        }

        # Find all potential variable names
        variable_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        potential_vars = re.findall(variable_pattern, self.expression)

        # Filter out excluded names and duplicates
        self.dependency_names = list(set(var for var in potential_vars
                                       if var not in excluded_names))

    def add_dependency(self, element):
        """Add a dependency to this calculator."""
        if element not in self.dependencies:
            self.dependencies.append(element)
            element.connect_to(self)

    def add_parameter(self, name: str, value: Any):
        """Add a parameter for the calculation."""
        self.parameters[name] = value

    def validate_units(self) -> Dict[str, Any]:
        """
        Validate the dimensional consistency of this calculator's expression.

        Returns:
        --------
        Dict[str, Any]
            Validation result with 'valid', 'inferred_units', 'errors', 'warnings'
        """
        if not self.unit_validation_enabled:
            return {'valid': True, 'inferred_units': None, 'errors': [], 'warnings': ['Unit validation disabled']}

        # Build dependency units mapping
        dependency_units = {}
        for dep in self.dependencies:
            if hasattr(dep, 'units') and dep.units:
                dependency_units[dep.name] = dep.units
                # Also add cleaned name for Python variables
                clean_name = dep.name.replace(' ', '_').replace('-', '_')
                dependency_units[clean_name] = dep.units

        # Validate the expression
        validation_result = self.unit_validator.validate_expression(
            self.expression,
            dependency_units,
            self.units
        )

        self.last_validation_result = validation_result
        return validation_result

    def enable_unit_validation(self, enabled: bool = True):
        """Enable or disable unit validation for this calculator."""
        self.unit_validation_enabled = enabled

    def get_validation_summary(self) -> str:
        """Get a human-readable summary of the last unit validation."""
        if not self.last_validation_result:
            return "No validation performed yet"

        result = self.last_validation_result
        summary = []

        if result['valid']:
            summary.append("✅ Unit validation passed")
            if result['inferred_units']:
                summary.append(f"   Inferred units: {result['inferred_units']}")
        else:
            summary.append("❌ Unit validation failed")

        if result['errors']:
            summary.append("   Errors:")
            for error in result['errors']:
                summary.append(f"     - {error}")

        if result['warnings']:
            summary.append("   Warnings:")
            for warning in result['warnings']:
                summary.append(f"     - {warning}")

        return "\n".join(summary)

    def calculate(self, time: float, dt: float, **kwargs) -> Union[float, np.ndarray]:
        """Calculate the result using the arithmetic expression with unit validation."""

        # Perform unit validation if enabled
        if self.unit_validation_enabled and self.dependencies:
            validation_result = self.validate_units()

            if not validation_result['valid']:
                error_msg = f"Unit validation failed for calculator '{self.name}':\n"
                for error in validation_result['errors']:
                    error_msg += f"  - {error}\n"

                if self.strict_unit_validation:
                    # Raise exception for strict validation
                    raise ValueError(error_msg.strip())
                else:
                    # Issue warning and continue for lenient validation
                    warnings.warn(error_msg.strip())

            # Show warnings if any
            if validation_result['warnings']:
                warning_msg = f"Unit validation warnings for calculator '{self.name}':\n"
                for warning in validation_result['warnings']:
                    warning_msg += f"  - {warning}\n"
                warnings.warn(warning_msg)

        # Gather values from dependencies
        dependency_values = {}
        for dep in self.dependencies:
            # Use element name as variable name in expression
            var_name = dep.name.replace(' ', '_').replace('-', '_')  # Clean name for Python variables
            dependency_values[var_name] = dep.current_value
            # Also add with original name for backward compatibility
            dependency_values[dep.name] = dep.current_value

        # Create local variables for expression evaluation
        local_vars = {
            'time': time,
            'dt': dt,
            'np': np
        }

        # Add dependency values
        local_vars.update(dependency_values)

        # Add parameters (constants from YAML)
        local_vars.update(self.parameters)

        # Add any additional kwargs
        local_vars.update(kwargs)

        # For missing variables in expression, try to provide reasonable defaults
        for var_name in self.dependency_names:
            if var_name not in local_vars:
                # Try to find by cleaned name
                cleaned_name = var_name.replace('_', ' ').replace('_', '-')
                found = False
                for dep in self.dependencies:
                    if dep.name == cleaned_name or dep.name.replace(' ', '_').replace('-', '_') == var_name:
                        local_vars[var_name] = dep.current_value
                        found = True
                        break

                if not found:
                    # Provide default values for common variable patterns
                    if 'flow' in var_name.lower():
                        local_vars[var_name] = 0.0
                    elif 'stock' in var_name.lower() or 'population' in var_name.lower():
                        local_vars[var_name] = 1000.0  # Default population
                    elif 'rate' in var_name.lower() or 'multiplier' in var_name.lower():
                        local_vars[var_name] = 1.0
                    else:
                        local_vars[var_name] = 0.0

        # Evaluate the expression
        try:
            result = eval(self.expression, {"__builtins__": {}, "np": np}, local_vars)

            # Ensure result is a valid numeric type
            if result is None:
                result = 0.0
            elif isinstance(result, (list, tuple)):
                result = np.array(result)

            self.current_value = result

        except Exception as e:
            print(f"Error evaluating calculator '{self.name}' expression '{self.expression}': {e}")
            print(f"Available variables: {list(local_vars.keys())}")
            print(f"Expected variables from expression: {self.dependency_names}")
            # Print variable details for debugging
            for var_name, var_value in local_vars.items():
                if isinstance(var_value, np.ndarray):
                    print(f"  {var_name}: numpy array, shape={var_value.shape}")
                elif var_name not in ['np', '__builtins__']:
                    print(f"  {var_name}: {type(var_value).__name__} = {var_value}")

            # Return zero on error
            self.current_value = 0.0

        # Record history
        self.history['time'].append(time)
        self.history['value'].append(self.current_value)

        return self.current_value

    def set_strict_unit_validation(self, strict: bool = True):
        """
        Configure whether unit validation failures should raise exceptions.

        Parameters:
        -----------
        strict : bool
            If True, unit validation failures raise ValueError exceptions.
            If False, unit validation failures issue warnings but continue.
        """
        self.strict_unit_validation = strict

        # Modify the calculate method behavior by updating the validation logic
        # This is handled in the calculate method itself

    def reset(self):
        """Reset calculator to initial conditions."""
        self.current_value = 0.0
        self.history = {'time': [], 'value': []}
        self.last_validation_result = None


class Delay(ModelElement):
    """
    Delay element for modeling time delays in system dynamics.
    
    Represents material or information delays where inputs take time
    to become outputs (e.g., aging chains, pipeline delays).
    """
    
    def __init__(self, name: str, delay_time: float, order: int = 1,
                 units: Optional[str] = None, description: str = ""):
        """
        Initialize delay element.
        
        Parameters:
        -----------
        name : str
            Name of the delay
        delay_time : float
            Average delay time
        order : int
            Order of the delay (1 = exponential, higher = more pipeline-like)
        units : str, optional
            Units of the delayed quantity
        description : str
            Description of the delay
        """
        super().__init__(name, units, description=description)
        
        self.delay_time = delay_time
        self.order = order
        
        # Create internal structure for higher-order delays
        self.levels = [0.0] * order
        self.input_value = 0.0
        self.output_value = 0.0
        
        # History
        self.history = {'time': [], 'input': [], 'output': []}
    
    def set_input(self, value: Union[float, np.ndarray]):
        """Set the input to the delay."""
        self.input_value = value
    
    def calculate(self, time: float, dt: float, **kwargs) -> Union[float, np.ndarray]:
        """Calculate delay output using aging chain structure."""
        if self.order == 1:
            # Simple exponential delay
            rate = self.input_value / self.delay_time
            self.levels[0] += (self.input_value - rate) * dt
            self.output_value = rate
        else:
            # Higher-order delay (aging chain)
            stage_time = self.delay_time / self.order
            
            # First stage
            rate_in = self.input_value
            rate_out = self.levels[0] / stage_time
            self.levels[0] += (rate_in - rate_out) * dt
            
            # Intermediate stages
            for i in range(1, self.order - 1):
                rate_in = self.levels[i-1] / stage_time
                rate_out = self.levels[i] / stage_time
                self.levels[i] += (rate_in - rate_out) * dt
            
            # Final stage
            if self.order > 1:
                rate_in = self.levels[-2] / stage_time
                rate_out = self.levels[-1] / stage_time
                self.levels[-1] += (rate_in - rate_out) * dt
                self.output_value = rate_out
        
        # Record history
        self.history['time'].append(time)
        self.history['input'].append(self.input_value)
        self.history['output'].append(self.output_value)
        
        return self.output_value


# Convenience functions for creating common model patterns
def create_exponential_growth(name: str, initial_value: float, growth_rate: float,
                            units: str = None) -> tuple[Stock, Flow]:
    """
    Create a simple exponential growth pattern.

    Returns:
    --------
    tuple : (stock, growth_flow)
    """
    stock = Stock(name, initial_value, units)
    growth_flow = Flow(f"{name}_growth", growth_rate, f"{units}/time" if units else None)
    stock.add_inflow(growth_flow)
    return stock, growth_flow


def create_decay_process(name: str, initial_value: float, decay_rate: float,
                        units: str = None) -> tuple[Stock, Flow]:
    """
    Create a simple decay/depreciation process.

    Returns:
    --------
    tuple : (stock, decay_flow)
    """
    stock = Stock(name, initial_value, units)
    decay_flow = Flow(f"{name}_decay", decay_rate, f"{units}/time" if units else None)
    stock.add_outflow(decay_flow)
    return stock, decay_flow
