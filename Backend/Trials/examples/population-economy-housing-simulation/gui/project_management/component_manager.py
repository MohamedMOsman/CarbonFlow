"""
Component File Management

Handles automatic YAML file generation and management for system components,
maintaining compatibility with existing sd_toolkit schemas and patterns.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import OrderedDict

from ..yaml_integration.yaml_loader import ModelComponent
from .project_manager import SystemModel, Project


class ComponentManager:
    """
    Manages component file operations with automatic YAML generation.
    
    Maintains compatibility with sd_toolkit schemas while providing
    organized file structure for multi-project management.
    """
    
    def __init__(self):
        """Initialize component manager."""
        pass
    
    def create_system_structure(self, system_path: Path):
        """
        Create the standard system folder structure.
        
        Creates:
        - components/stocks.yaml
        - components/flows.yaml  
        - components/calculators.yaml
        - informants/dimensional_data.yaml
        """
        system_path.mkdir(parents=True, exist_ok=True)
        
        # Create components directory
        components_path = system_path / "components"
        components_path.mkdir(exist_ok=True)
        
        # Create informants directory
        informants_path = system_path / "informants"
        informants_path.mkdir(exist_ok=True)
        
        # Create empty component files with proper structure
        self._create_empty_component_file(components_path / "stocks.yaml", "stocks")
        self._create_empty_component_file(components_path / "flows.yaml", "flows")
        self._create_empty_component_file(components_path / "calculators.yaml", "calculators")
        
        # Create empty informants file
        self._create_empty_informants_file(informants_path / "dimensional_data.yaml")
    
    def save_system(self, system: SystemModel, project: Project):
        """
        Save a complete system to its directory structure.
        
        Parameters:
        -----------
        system : SystemModel
            The system to save
        project : Project
            The parent project
        """
        if not project.project_path:
            raise ValueError("Project path not set")
        
        # Determine system path
        project_path = Path(project.project_path)
        system_path = project_path / "systems" / self._sanitize_name(system.name)
        
        # Create system structure
        self.create_system_structure(system_path)
        
        # Save components by type
        self._save_components_by_type(system.stocks, system_path / "components" / "stocks.yaml", "stocks")
        self._save_components_by_type(system.flows, system_path / "components" / "flows.yaml", "flows")
        self._save_components_by_type(system.calculators, system_path / "components" / "calculators.yaml", "calculators")
        
        # Save system metadata
        self._save_system_metadata(system, system_path)
        
        # Update system path
        system.system_path = str(system_path.relative_to(project_path))
    
    def load_system(self, system_path: Path, project: Project) -> Optional[SystemModel]:
        """
        Load a system from its directory structure.
        
        Parameters:
        -----------
        system_path : Path
            Path to the system directory
        project : Project
            The parent project
            
        Returns:
        --------
        SystemModel : The loaded system, or None if loading fails
        """
        if not system_path.exists():
            return None
        
        # Load system metadata
        metadata_path = system_path / "system_metadata.yaml"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f)
            
            system = SystemModel(
                name=metadata['system']['name'],
                description=metadata['system'].get('description', ''),
                system_id=metadata['system'].get('system_id', ''),
            )
            
            # Load system configuration
            if 'dimensions' in metadata:
                system.dimensions = metadata['dimensions']
            if 'functions' in metadata:
                system.functions = metadata['functions']
            if 'constants' in metadata:
                system.constants = metadata['constants']
            if 'connections' in metadata:
                system.connections = metadata['connections']
        else:
            # Create system from directory name
            system = SystemModel(name=system_path.name)
        
        # Load components
        components_path = system_path / "components"
        if components_path.exists():
            # Load stocks
            stocks = self._load_components_from_file(components_path / "stocks.yaml", "stock")
            for component in stocks:
                system.stocks[component.name] = component
            
            # Load flows
            flows = self._load_components_from_file(components_path / "flows.yaml", "flow")
            for component in flows:
                system.flows[component.name] = component
            
            # Load calculators
            calculators = self._load_components_from_file(components_path / "calculators.yaml", "calculator")
            for component in calculators:
                system.calculators[component.name] = component
        
        # Set system path
        system.system_path = str(system_path.name)
        
        return system
    
    def _create_empty_component_file(self, file_path: Path, component_type: str):
        """Create an empty component file with proper YAML structure."""
        structure = {
            'metadata': {
                'component_type': component_type,
                'created_at': '',
                'description': f'{component_type.title()} components for this system'
            },
            'components': []
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(structure, f, default_flow_style=False, sort_keys=False)
    
    def _create_empty_informants_file(self, file_path: Path):
        """Create an empty informants file with proper structure."""
        structure = {
            'metadata': {
                'description': 'Dimensional data and informants for this system',
                'created_at': '',
                'version': '1.0'
            },
            'dimensions': {},
            'informants': {}
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(structure, f, default_flow_style=False, sort_keys=False)
    
    def _save_components_by_type(self, components: Dict[str, ModelComponent], 
                                file_path: Path, component_type: str):
        """Save components of a specific type to a YAML file."""
        if not components:
            # Keep empty file structure
            self._create_empty_component_file(file_path, component_type)
            return
        
        # Convert components to YAML-compatible format
        yaml_components = []
        for component in components.values():
            yaml_component = self._component_to_yaml(component)
            yaml_components.append(yaml_component)
        
        structure = {
            'metadata': {
                'component_type': component_type,
                'created_at': '',
                'description': f'{component_type.title()} components for this system',
                'count': len(yaml_components)
            },
            'components': yaml_components
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(structure, f, default_flow_style=False, sort_keys=False)
    
    def _save_system_metadata(self, system: SystemModel, system_path: Path):
        """Save system metadata including dimensions, functions, and connections."""
        metadata = OrderedDict()
        
        # System information
        metadata['system'] = OrderedDict([
            ('name', system.name),
            ('description', system.description),
            ('system_id', system.system_id),
            ('created_at', system.created_at.isoformat()),
            ('modified_at', system.modified_at.isoformat())
        ])
        
        # System configuration
        if system.dimensions:
            metadata['dimensions'] = system.dimensions
        
        if system.functions:
            metadata['functions'] = system.functions
        
        if system.constants:
            metadata['constants'] = system.constants
        
        if system.connections:
            metadata['connections'] = system.connections
        
        metadata_path = system_path / "system_metadata.yaml"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
    
    def _load_components_from_file(self, file_path: Path, component_type: str) -> List[ModelComponent]:
        """Load components from a YAML file."""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'components' not in data:
                return []
            
            components = []
            for comp_data in data['components']:
                component = ModelComponent(
                    name=comp_data['name'],
                    component_type=component_type,
                    properties=comp_data.get('properties', {})
                )
                components.append(component)
            
            return components
            
        except Exception as e:
            print(f"Error loading components from {file_path}: {e}")
            return []
    
    def _component_to_yaml(self, component: ModelComponent) -> Dict[str, Any]:
        """Convert a ModelComponent to YAML-compatible dictionary."""
        yaml_component = OrderedDict()
        yaml_component['name'] = component.name

        # Add properties in sd_toolkit-compatible order
        # Core properties first
        if 'initial_value' in component.properties:
            yaml_component['initial_value'] = component.properties['initial_value']

        if 'rate' in component.properties:
            yaml_component['rate'] = component.properties['rate']

        if 'expression' in component.properties:
            yaml_component['expression'] = component.properties['expression']

        # Units and dimensions
        if 'units' in component.properties:
            yaml_component['units'] = component.properties['units']

        if 'spatial_dims' in component.properties:
            yaml_component['spatial_dims'] = component.properties['spatial_dims']

        # Parameters and dependencies
        if 'parameters' in component.properties:
            yaml_component['parameters'] = component.properties['parameters']

        if 'dependencies' in component.properties:
            yaml_component['dependencies'] = component.properties['dependencies']

        # Constraints
        if 'min_value' in component.properties:
            yaml_component['min_value'] = component.properties['min_value']

        if 'max_value' in component.properties:
            yaml_component['max_value'] = component.properties['max_value']

        # Description last
        if 'description' in component.properties:
            yaml_component['description'] = component.properties['description']

        # Add any remaining properties
        for key, value in component.properties.items():
            if key not in yaml_component:
                yaml_component[key] = value

        return yaml_component
    
    def generate_integrated_yaml(self, system: SystemModel, project: Project) -> Dict[str, Any]:
        """
        Generate a complete sd_toolkit-compatible YAML structure for a system.

        This creates a single YAML file that can be used with the existing
        YAMLSystemBuilder for backward compatibility.

        Parameters:
        -----------
        system : SystemModel
            The system to convert
        project : Project
            The parent project

        Returns:
        --------
        Dict[str, Any] : Complete YAML structure compatible with sd_toolkit
        """
        yaml_structure = OrderedDict()

        # Model metadata
        yaml_structure['model'] = OrderedDict([
            ('name', system.name),
            ('description', system.description),
            ('time_horizon', 50),  # Default values
            ('dt', 0.25),
            ('time_units', 'year')
        ])

        # Dimensions
        if system.dimensions:
            yaml_structure['dimensions'] = system.dimensions

        # Functions
        if system.functions:
            yaml_structure['functions'] = system.functions

        # Constants
        if system.constants:
            yaml_structure['constants'] = system.constants

        # Elements
        elements = OrderedDict()

        # Stocks
        if system.stocks:
            elements['stocks'] = [self._component_to_yaml(comp) for comp in system.stocks.values()]

        # Flows
        if system.flows:
            elements['flows'] = [self._component_to_yaml(comp) for comp in system.flows.values()]

        # Calculators
        if system.calculators:
            elements['calculators'] = [self._component_to_yaml(comp) for comp in system.calculators.values()]

        if elements:
            yaml_structure['elements'] = elements

        # Connections
        if system.connections:
            connections = []
            for from_name, to_name, connection_type in system.connections:
                connections.append(OrderedDict([
                    ('from', from_name),
                    ('to', to_name),
                    ('type', connection_type)
                ]))
            yaml_structure['connections'] = connections

        return yaml_structure

    def save_integrated_yaml(self, system: SystemModel, project: Project, output_path: Path):
        """
        Save a system as a complete sd_toolkit-compatible YAML file.

        Parameters:
        -----------
        system : SystemModel
            The system to save
        project : Project
            The parent project
        output_path : Path
            Path for the output YAML file
        """
        yaml_structure = self.generate_integrated_yaml(system, project)

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_structure, f, default_flow_style=False, sort_keys=False)

    def export_system_for_notebook(self, system: SystemModel, project: Project,
                                  export_dir: Path) -> Dict[str, str]:
        """
        Export a system in the format expected by Jupyter notebooks.

        Creates both model structure and scenario files for easy notebook integration.

        Parameters:
        -----------
        system : SystemModel
            The system to export
        project : Project
            The parent project
        export_dir : Path
            Directory for exported files

        Returns:
        --------
        Dict[str, str] : Paths to created files
        """
        export_dir.mkdir(parents=True, exist_ok=True)

        # Generate model structure (without constants)
        model_structure = self.generate_integrated_yaml(system, project)
        if 'constants' in model_structure:
            constants = model_structure.pop('constants')
        else:
            constants = {}

        # Save model structure
        model_path = export_dir / f"{self._sanitize_name(system.name)}_model_structure.yaml"
        with open(model_path, 'w', encoding='utf-8') as f:
            yaml.dump(model_structure, f, default_flow_style=False, sort_keys=False)

        # Generate scenario file
        scenario_structure = OrderedDict([
            ('scenario', OrderedDict([
                ('name', f"{system.name} Baseline Scenario"),
                ('description', f"Baseline parameters for {system.name}"),
                ('version', '1.0'),
                ('model_file', model_path.name)
            ])),
            ('constants', constants)
        ])

        # Save scenario file
        scenario_path = export_dir / f"{self._sanitize_name(system.name)}_scenario_parameters.yaml"
        with open(scenario_path, 'w', encoding='utf-8') as f:
            yaml.dump(scenario_structure, f, default_flow_style=False, sort_keys=False)

        return {
            'model_structure': str(model_path),
            'scenario_parameters': str(scenario_path)
        }

    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use as a directory/file name."""
        return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_').lower()
