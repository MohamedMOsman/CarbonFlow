"""
Informants Data Management

Manages dimensional data separately from component definitions,
supporting both array-based multi-value dimensions and scalar single-point dimensions.
Maintains referential integrity between component dimensions and informant data values.
"""

import yaml
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from collections import OrderedDict
from dataclasses import dataclass, field

from .project_manager import SystemModel


@dataclass
class DimensionDefinition:
    """Definition of a dimension with its properties and data."""
    
    name: str
    size: int
    labels: List[str] = field(default_factory=list)
    description: str = ""
    dimension_type: str = "categorical"  # categorical, temporal, spatial, ordinal
    units: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate dimension definition and return any errors."""
        errors = []
        
        if not self.name:
            errors.append("Dimension name cannot be empty")
        
        if self.size <= 0:
            errors.append("Dimension size must be positive")
        
        if self.labels and len(self.labels) != self.size:
            errors.append(f"Number of labels ({len(self.labels)}) must match size ({self.size})")
        
        return errors


@dataclass
class InformantData:
    """Data container for informant values with dimensional structure."""
    
    name: str
    description: str = ""
    data_type: str = "array"  # array, scalar, function
    dimensions: List[str] = field(default_factory=list)
    values: Union[np.ndarray, float, int, str] = None
    units: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self, available_dimensions: Dict[str, DimensionDefinition]) -> List[str]:
        """Validate informant data against available dimensions."""
        errors = []
        
        if not self.name:
            errors.append("Informant name cannot be empty")
        
        # Check dimension references
        for dim_name in self.dimensions:
            if dim_name not in available_dimensions:
                errors.append(f"Referenced dimension '{dim_name}' not found")
        
        # Validate data shape for arrays
        if self.data_type == "array" and isinstance(self.values, np.ndarray):
            expected_shape = tuple(available_dimensions[dim].size for dim in self.dimensions 
                                 if dim in available_dimensions)
            if self.values.shape != expected_shape:
                errors.append(f"Data shape {self.values.shape} doesn't match expected {expected_shape}")
        
        return errors


class InformantsManager:
    """
    Manages dimensional data and informants for system dynamics models.
    
    Provides functionality to:
    - Define and manage dimensions with labels and metadata
    - Store and validate informant data with dimensional structure
    - Maintain referential integrity between components and informants
    - Export/import informant data in YAML format
    """
    
    def __init__(self):
        """Initialize informants manager."""
        pass
    
    def save_informants(self, system: SystemModel, informants_path: Path):
        """
        Save system informants and dimensional data to YAML file.
        
        Parameters:
        -----------
        system : SystemModel
            The system containing dimensional data
        informants_path : Path
            Path to the informants YAML file
        """
        # Prepare informants structure
        informants_data = OrderedDict()
        
        # Metadata
        informants_data['metadata'] = OrderedDict([
            ('description', f'Dimensional data and informants for {system.name}'),
            ('system_name', system.name),
            ('system_id', system.system_id),
            ('created_at', system.created_at.isoformat()),
            ('modified_at', system.modified_at.isoformat()),
            ('version', '1.0')
        ])
        
        # Dimensions
        if system.dimensions:
            informants_data['dimensions'] = self._serialize_dimensions(system.dimensions)
        
        # Informants (extracted from component properties)
        informants = self._extract_informants_from_system(system)
        if informants:
            informants_data['informants'] = informants
        
        # Save to file
        with open(informants_path, 'w', encoding='utf-8') as f:
            yaml.dump(informants_data, f, default_flow_style=False, sort_keys=False)
    
    def load_informants(self, informants_path: Path) -> Dict[str, Any]:
        """
        Load informants data from YAML file.
        
        Parameters:
        -----------
        informants_path : Path
            Path to the informants YAML file
            
        Returns:
        --------
        Dict[str, Any] : Loaded informants data
        """
        if not informants_path.exists():
            return {}
        
        try:
            with open(informants_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading informants from {informants_path}: {e}")
            return {}
    
    def validate_system_informants(self, system: SystemModel) -> Dict[str, List[str]]:
        """
        Validate all informants in a system for consistency.
        
        Parameters:
        -----------
        system : SystemModel
            The system to validate
            
        Returns:
        --------
        Dict[str, List[str]] : Validation results with component names as keys and error lists as values
        """
        validation_results = {}
        
        # Create dimension definitions from system dimensions
        dimension_defs = {}
        for dim_name, dim_data in system.dimensions.items():
            if isinstance(dim_data, dict):
                dimension_defs[dim_name] = DimensionDefinition(
                    name=dim_name,
                    size=dim_data.get('size', 1),
                    labels=dim_data.get('labels', []),
                    description=dim_data.get('description', ''),
                    dimension_type=dim_data.get('type', 'categorical'),
                    units=dim_data.get('units')
                )
        
        # Validate each component's dimensional consistency
        for component in system.get_all_components().values():
            errors = []
            
            # Check spatial_dims references
            spatial_dims = component.properties.get('spatial_dims', [])
            for dim_name in spatial_dims:
                if dim_name not in dimension_defs:
                    errors.append(f"Spatial dimension '{dim_name}' not defined in system dimensions")
            
            # Check multidimensional data consistency
            if 'initial_value' in component.properties:
                initial_value = component.properties['initial_value']
                if isinstance(initial_value, dict) and 'array' in initial_value:
                    array_data = initial_value['array']
                    if 'shape' in array_data and spatial_dims:
                        expected_shape = tuple(dimension_defs[dim].size for dim in spatial_dims 
                                             if dim in dimension_defs)
                        actual_shape = tuple(array_data['shape'])
                        if actual_shape != expected_shape:
                            errors.append(f"Array shape {actual_shape} doesn't match spatial dimensions {expected_shape}")
            
            if errors:
                validation_results[component.name] = errors
        
        return validation_results
    
    def create_dimension_template(self, name: str, size: int, 
                                dimension_type: str = "categorical") -> DimensionDefinition:
        """
        Create a dimension template with default values.
        
        Parameters:
        -----------
        name : str
            Dimension name
        size : int
            Dimension size
        dimension_type : str
            Type of dimension
            
        Returns:
        --------
        DimensionDefinition : The created dimension template
        """
        labels = [f"{name}_{i+1}" for i in range(size)]
        
        return DimensionDefinition(
            name=name,
            size=size,
            labels=labels,
            description=f"Auto-generated {dimension_type} dimension",
            dimension_type=dimension_type
        )
    
    def create_informant_template(self, name: str, dimensions: List[str], 
                                data_type: str = "array") -> InformantData:
        """
        Create an informant data template.
        
        Parameters:
        -----------
        name : str
            Informant name
        dimensions : List[str]
            List of dimension names
        data_type : str
            Type of data (array, scalar, function)
            
        Returns:
        --------
        InformantData : The created informant template
        """
        return InformantData(
            name=name,
            description=f"Auto-generated {data_type} informant",
            data_type=data_type,
            dimensions=dimensions.copy(),
            values=None,
            units="units"
        )
    
    def _serialize_dimensions(self, dimensions: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dimensions to YAML-serializable format."""
        serialized = OrderedDict()
        
        for dim_name, dim_data in dimensions.items():
            if isinstance(dim_data, dict):
                serialized[dim_name] = OrderedDict()
                for key, value in dim_data.items():
                    serialized[dim_name][key] = value
            else:
                # Handle simple dimension definitions
                serialized[dim_name] = dim_data
        
        return serialized
    
    def _extract_informants_from_system(self, system: SystemModel) -> Dict[str, Any]:
        """Extract informant data from system components."""
        informants = OrderedDict()
        
        # Extract multidimensional data from components
        for component in system.get_all_components().values():
            # Look for array-based initial values
            if 'initial_value' in component.properties:
                initial_value = component.properties['initial_value']
                if isinstance(initial_value, dict) and 'array' in initial_value:
                    informant_name = f"{component.name}_initial_data"
                    informants[informant_name] = OrderedDict([
                        ('description', f'Initial values for {component.name}'),
                        ('data_type', 'array'),
                        ('dimensions', component.properties.get('spatial_dims', [])),
                        ('values', initial_value['array'].get('values', [])),
                        ('units', component.properties.get('units', 'units')),
                        ('source_component', component.name)
                    ])
            
            # Extract parameter references that might be informants
            for prop_name, prop_value in component.properties.items():
                if isinstance(prop_value, str) and prop_value.startswith('$'):
                    # This is a parameter reference - could be an informant
                    param_name = prop_value[1:]  # Remove $ prefix
                    if param_name not in informants:
                        informants[param_name] = OrderedDict([
                            ('description', f'Parameter referenced by {component.name}.{prop_name}'),
                            ('data_type', 'scalar'),
                            ('dimensions', []),
                            ('values', None),
                            ('units', 'units'),
                            ('referenced_by', [f"{component.name}.{prop_name}"])
                        ])
                    else:
                        # Add to referenced_by list
                        if 'referenced_by' not in informants[param_name]:
                            informants[param_name]['referenced_by'] = []
                        informants[param_name]['referenced_by'].append(f"{component.name}.{prop_name}")
        
        return informants
