"""
System Dynamics Component Type Definitions

This module defines the types of system dynamics components available
in the GUI, their properties, and default values.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass
class ComponentType:
    """Definition of a system dynamics component type."""
    
    name: str  # Internal name (e.g., 'stock', 'flow')
    display_name: str  # Display name (e.g., 'Stock', 'Flow')
    description: str  # Description of the component
    category: str  # Category for grouping (e.g., 'core', 'calculation')
    default_properties: Dict[str, Any]  # Default property values
    required_properties: List[str]  # Properties that must be set
    optional_properties: List[str]  # Properties that can be set
    supports_dimensions: bool  # Whether component supports multidimensional data
    connection_types: List[str]  # Types of connections this component can have


# Define component types
STOCK_TYPE = ComponentType(
    name='stock',
    display_name='Stock',
    description='Accumulation element that represents quantities that can be measured at a point in time',
    category='core',
    default_properties={
        'initial_value': 0,
        'units': 'units',
        'spatial_dims': [],
        'min_value': None,
        'max_value': None,
    },
    required_properties=['name', 'initial_value'],
    optional_properties=['units', 'spatial_dims', 'min_value', 'max_value', 'description'],
    supports_dimensions=True,
    connection_types=['inflow', 'outflow']
)

FLOW_TYPE = ComponentType(
    name='flow',
    display_name='Flow',
    description='Rate element that represents activities or processes that change stocks over time',
    category='core',
    default_properties={
        'rate': 0,
        'units': 'units/time',
        'spatial_dims': [],
        'parameters': {},
    },
    required_properties=['name', 'rate'],
    optional_properties=['units', 'spatial_dims', 'parameters', 'description'],
    supports_dimensions=True,
    connection_types=['from_stock', 'to_stock', 'dependency']
)

CALCULATOR_TYPE = ComponentType(
    name='calculator',
    display_name='Calculator',
    description='Calculation element that performs arithmetic operations on other model elements',
    category='calculation',
    default_properties={
        'expression': '',
        'units': 'units',
        'spatial_dims': [],
        'dependencies': [],
    },
    required_properties=['name', 'expression'],
    optional_properties=['units', 'spatial_dims', 'dependencies', 'description'],
    supports_dimensions=True,
    connection_types=['dependency', 'output']
)

AUXILIARY_TYPE = ComponentType(
    name='auxiliary',
    display_name='Auxiliary',
    description='Helper element for intermediate calculations and constants',
    category='calculation',
    default_properties={
        'value': 0,
        'units': 'units',
    },
    required_properties=['name', 'value'],
    optional_properties=['units', 'description'],
    supports_dimensions=False,
    connection_types=['dependency']
)

CONSTANT_TYPE = ComponentType(
    name='constant',
    display_name='Constant',
    description='Fixed value element that provides parameters to the model',
    category='parameter',
    default_properties={
        'value': 0,
        'units': 'units',
    },
    required_properties=['name', 'value'],
    optional_properties=['units', 'description'],
    supports_dimensions=False,
    connection_types=['dependency']
)

# Component definitions registry
COMPONENT_DEFINITIONS: Dict[str, ComponentType] = {
    'stock': STOCK_TYPE,
    'flow': FLOW_TYPE,
    'calculator': CALCULATOR_TYPE,
    'auxiliary': AUXILIARY_TYPE,
    'constant': CONSTANT_TYPE,
}


def get_component_type(type_name: str) -> Optional[ComponentType]:
    """Get component type definition by name."""
    return COMPONENT_DEFINITIONS.get(type_name)


def get_all_component_types() -> List[ComponentType]:
    """Get all available component types."""
    return list(COMPONENT_DEFINITIONS.values())


def get_component_types_by_category(category: str) -> List[ComponentType]:
    """Get component types in a specific category."""
    return [comp_type for comp_type in COMPONENT_DEFINITIONS.values() 
            if comp_type.category == category]


def validate_component_properties(component_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate component properties against type definition.
    
    Returns:
    --------
    Dict with 'valid' (bool), 'errors' (list), 'warnings' (list)
    """
    
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    comp_type = get_component_type(component_type)
    if not comp_type:
        result['valid'] = False
        result['errors'].append(f"Unknown component type: {component_type}")
        return result
    
    # Check required properties
    for required_prop in comp_type.required_properties:
        if required_prop not in properties or properties[required_prop] is None:
            result['valid'] = False
            result['errors'].append(f"Missing required property: {required_prop}")
    
    # Check for unknown properties
    all_valid_props = set(comp_type.required_properties + comp_type.optional_properties)
    for prop_name in properties:
        if prop_name not in all_valid_props:
            result['warnings'].append(f"Unknown property: {prop_name}")
    
    # Type-specific validations
    if component_type == 'stock':
        initial_value = properties.get('initial_value')
        if initial_value is not None:
            min_val = properties.get('min_value')
            max_val = properties.get('max_value')
            
            if min_val is not None and initial_value < min_val:
                result['errors'].append(f"Initial value {initial_value} is below minimum {min_val}")
                result['valid'] = False
                
            if max_val is not None and initial_value > max_val:
                result['errors'].append(f"Initial value {initial_value} is above maximum {max_val}")
                result['valid'] = False
    
    elif component_type == 'calculator':
        expression = properties.get('expression', '')
        if not expression.strip():
            result['errors'].append("Calculator expression cannot be empty")
            result['valid'] = False
    
    return result


def get_default_component_name(component_type: str, existing_names: List[str] = None) -> str:
    """Generate a default name for a new component."""
    
    comp_type = get_component_type(component_type)
    if not comp_type:
        return f"Unknown_{component_type}"
    
    base_name = comp_type.display_name.replace(' ', '_')
    
    if not existing_names:
        return base_name
    
    # Find next available number
    counter = 1
    while True:
        candidate_name = f"{base_name}_{counter}"
        if candidate_name not in existing_names:
            return candidate_name
        counter += 1


def create_placeholder_dimensions() -> Dict[str, Dict[str, Any]]:
    """Create realistic placeholder dimensions for multidimensional components."""
    return {
        'age_group': {
            'labels': ['0-18', '19-35', '36-55', '56-65', '65+'],
            'description': 'Age demographic groups',
            'type': 'categorical',
            'size': 5
        },
        'income_level': {
            'labels': ['low', 'medium', 'high'],
            'description': 'Income brackets',
            'type': 'categorical',
            'size': 3
        },
        'housing_type': {
            'labels': ['single_family', 'condo', 'apartment', 'townhouse'],
            'description': 'Types of housing units',
            'type': 'categorical',
            'size': 4
        },
        'time_period': {
            'labels': ['2020', '2021', '2022', '2023', '2024'],
            'description': 'Time periods for simulation',
            'type': 'temporal',
            'size': 5
        },
        'zone': {
            'labels': ['downtown', 'suburban', 'rural'],
            'description': 'Geographic zones',
            'type': 'categorical',
            'size': 3
        },
        'parcel': {
            'labels': ['1001', '1002', '1003'],
            'description': 'Property parcel identifiers',
            'type': 'categorical',
            'size': 3
        }
    }


def create_placeholder_data(component_type: str, component_name: str, spatial_dims: List[str]) -> Dict[str, Any]:
    """Create realistic placeholder multidimensional data for a component."""

    if not spatial_dims or len(spatial_dims) < 2:
        return {}

    placeholder_dims = create_placeholder_dimensions()

    # Get labels for the spatial dimensions
    dim_labels = {}
    for dim in spatial_dims:
        if dim in placeholder_dims:
            dim_labels[dim] = placeholder_dims[dim]['labels']
        else:
            # Create default labels for unknown dimensions
            dim_labels[dim] = [f"{dim}_{i}" for i in range(3)]

    # Generate sample data based on component type
    sample_data = {}

    if component_type == 'stock':
        # Generate population-like data
        base_values = {
            'population': [2500, 3200, 2800, 1800, 1200],
            'housing_units': [800, 1200, 900, 600, 400],
            'employment': [1500, 2800, 2200, 1000, 300],
            'infrastructure': [100, 150, 120, 80, 50]
        }

        # Choose base values based on component name
        if 'population' in component_name.lower():
            base_vals = base_values['population']
        elif 'housing' in component_name.lower() or 'unit' in component_name.lower():
            base_vals = base_values['housing_units']
        elif 'employment' in component_name.lower() or 'job' in component_name.lower():
            base_vals = base_values['employment']
        else:
            base_vals = base_values['infrastructure']

    elif component_type == 'flow':
        # Generate flow rate data
        base_vals = [0.05, 0.08, 0.06, 0.04, 0.02]  # Rates

    elif component_type == 'calculator':
        # Generate calculated values
        base_vals = [1.2, 1.5, 1.3, 1.1, 0.9]  # Multipliers or ratios

    else:
        # Default values
        base_vals = [100, 150, 120, 80, 50]

    # Generate all combinations of dimensional coordinates
    import itertools

    # Limit to first 2-3 dimensions to avoid too much data
    active_dims = spatial_dims[:min(3, len(spatial_dims))]
    active_labels = [dim_labels[dim] for dim in active_dims]

    # Generate combinations
    for i, coord_combo in enumerate(itertools.product(*active_labels)):
        if i >= 50:  # Limit to 50 entries to avoid overwhelming
            break

        # Create the data key tuple
        key = tuple([component_name] + list(coord_combo))

        # Generate a realistic value
        base_idx = i % len(base_vals)
        variation = 0.8 + (i * 0.1) % 0.4  # Add some variation
        value = base_vals[base_idx] * variation

        # Round appropriately
        if component_type == 'flow':
            sample_data[key] = round(value, 3)
        elif component_type == 'stock':
            sample_data[key] = int(value)
        else:
            sample_data[key] = round(value, 2)

    return sample_data


def create_component_template(component_type: str, name: str = None, include_placeholder_data: bool = True, **kwargs) -> Dict[str, Any]:
    """Create a component template with default values and optional placeholder data."""

    comp_type = get_component_type(component_type)
    if not comp_type:
        raise ValueError(f"Unknown component type: {component_type}")

    # Start with default properties
    template = comp_type.default_properties.copy()

    # Set name
    if name:
        template['name'] = name
    else:
        template['name'] = get_default_component_name(component_type)

    # Add placeholder data for multidimensional components
    if include_placeholder_data and comp_type.supports_dimensions:
        # Add realistic spatial dimensions
        if component_type == 'stock':
            if 'population' in template['name'].lower():
                template['spatial_dims'] = ['age_group', 'income_level', 'time_period']
                template['units'] = 'people'
                template['initial_value'] = 10000
            elif 'housing' in template['name'].lower():
                template['spatial_dims'] = ['housing_type', 'zone', 'time_period']
                template['units'] = 'units'
                template['initial_value'] = 5000
            else:
                template['spatial_dims'] = ['age_group', 'zone', 'time_period']
                template['units'] = 'units'
                template['initial_value'] = 1000

        elif component_type == 'flow':
            template['spatial_dims'] = ['age_group', 'zone']
            template['units'] = 'units/year'
            template['rate'] = 0.05

        elif component_type == 'calculator':
            template['spatial_dims'] = ['zone', 'time_period']
            template['units'] = 'calculated_units'
            template['expression'] = 'input_flow + adjustment_factor'
            template['dependencies'] = ['input_flow', 'adjustment_factor']

        # Generate placeholder multidimensional data
        if template.get('spatial_dims'):
            placeholder_data = create_placeholder_data(
                component_type,
                template['name'],
                template['spatial_dims']
            )
            if placeholder_data:
                template['multidimensional_data'] = placeholder_data

    # Apply any provided overrides
    template.update(kwargs)

    return template


# Connection type definitions
CONNECTION_TYPES = {
    'inflow': {
        'name': 'inflow',
        'display_name': 'Inflow',
        'description': 'Flow that increases a stock',
        'from_types': ['flow'],
        'to_types': ['stock'],
        'arrow_style': 'solid',
        'color': '#00AA00'  # Green
    },
    'outflow': {
        'name': 'outflow',
        'display_name': 'Outflow',
        'description': 'Flow that decreases a stock',
        'from_types': ['stock'],
        'to_types': ['flow'],
        'arrow_style': 'solid',
        'color': '#AA0000'  # Red
    },
    'dependency': {
        'name': 'dependency',
        'display_name': 'Dependency',
        'description': 'Information link between components',
        'from_types': ['stock', 'flow', 'calculator', 'auxiliary', 'constant'],
        'to_types': ['flow', 'calculator'],
        'arrow_style': 'dashed',
        'color': '#666666'  # Gray
    }
}


def get_valid_connection_types(from_type: str, to_type: str) -> List[str]:
    """Get valid connection types between two component types."""
    
    valid_types = []
    
    for conn_name, conn_info in CONNECTION_TYPES.items():
        if (from_type in conn_info['from_types'] and 
            to_type in conn_info['to_types']):
            valid_types.append(conn_name)
    
    return valid_types


def is_valid_connection(from_type: str, to_type: str, connection_type: str) -> bool:
    """Check if a connection is valid."""
    
    conn_info = CONNECTION_TYPES.get(connection_type)
    if not conn_info:
        return False
    
    return (from_type in conn_info['from_types'] and 
            to_type in conn_info['to_types'])


# Dimension support utilities
def supports_multidimensional_data(component_type: str) -> bool:
    """Check if a component type supports multidimensional data."""
    
    comp_type = get_component_type(component_type)
    return comp_type.supports_dimensions if comp_type else False


def get_dimensional_properties(component_type: str) -> List[str]:
    """Get properties that can have dimensional data."""
    
    if not supports_multidimensional_data(component_type):
        return []
    
    # Properties that can be multidimensional
    dimensional_props = {
        'stock': ['initial_value'],
        'flow': ['rate'],
        'calculator': ['expression'],  # Output can be multidimensional
    }
    
    return dimensional_props.get(component_type, [])
