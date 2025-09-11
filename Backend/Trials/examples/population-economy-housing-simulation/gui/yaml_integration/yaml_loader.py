"""
YAML Model Loader

This module provides functionality to load YAML-based system dynamics models
and convert them to internal GUI representations.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sys

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'sd_toolkit'))

from sd_toolkit.config import YAMLSystemBuilder
from sd_toolkit.engine.system import SystemModel


class ModelComponent:
    """Base class for GUI model components."""
    
    def __init__(self, name: str, component_type: str, properties: Dict[str, Any]):
        self.name = name
        self.component_type = component_type  # 'stock', 'flow', 'calculator', 'constant'
        self.properties = properties
        self.position = (0, 0)  # Canvas position
        self.connections = []  # Connected components
        
    def __repr__(self):
        return f"{self.component_type.title()}('{self.name}')"


class GuiModel:
    """Internal GUI representation of a system dynamics model."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.time_horizon = 50
        self.dt = 0.25
        self.time_units = "year"
        
        # Model structure
        self.dimensions = {}
        self.functions = {}
        self.constants = {}
        
        # Components
        self.components = {}  # name -> ModelComponent
        self.connections = []  # List of (from_name, to_name, connection_type)
        
        # Original YAML data for round-trip compatibility
        self.original_yaml_data = None
        
    def add_component(self, component: ModelComponent):
        """Add a component to the model."""
        self.components[component.name] = component
        
    def get_component(self, name: str) -> Optional[ModelComponent]:
        """Get a component by name."""
        return self.components.get(name)
        
    def get_components_by_type(self, component_type: str) -> List[ModelComponent]:
        """Get all components of a specific type."""
        return [comp for comp in self.components.values() 
                if comp.component_type == component_type]
        
    def add_connection(self, from_name: str, to_name: str, connection_type: str):
        """Add a connection between components."""
        self.connections.append((from_name, to_name, connection_type))
        
        # Update component connections
        from_comp = self.get_component(from_name)
        to_comp = self.get_component(to_name)
        
        if from_comp and to_comp:
            from_comp.connections.append((to_comp, connection_type))


class YAMLModelLoader:
    """Loads YAML system dynamics models into GUI representation."""
    
    def __init__(self):
        self.yaml_builder = YAMLSystemBuilder()
        
    def load_model_from_file(self, model_path: str, scenario_path: Optional[str] = None) -> Tuple[GuiModel, SystemModel]:
        """
        Load a model from YAML file(s).
        
        Parameters:
        -----------
        model_path : str
            Path to the model structure YAML file
        scenario_path : str, optional
            Path to the scenario parameters YAML file
            
        Returns:
        --------
        Tuple[GuiModel, SystemModel] : GUI model and sd_toolkit model
        """
        
        # Load YAML files
        model_data = self._load_yaml_file(model_path)
        scenario_data = None
        
        if scenario_path:
            scenario_data = self._load_yaml_file(scenario_path)
            
        # Create GUI model
        gui_model = self._create_gui_model(model_data, scenario_data)
        
        # Create sd_toolkit model for simulation
        full_config = model_data.copy()
        if scenario_data and 'constants' in scenario_data:
            full_config['constants'] = scenario_data['constants']
            
        sd_model = self.yaml_builder.build_from_dict(full_config)
        
        return gui_model, sd_model
        
    def _load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse a YAML file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {file_path}")
            
        with open(path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
            
    def _create_gui_model(self, model_data: Dict[str, Any], scenario_data: Optional[Dict[str, Any]] = None) -> GuiModel:
        """Create GUI model from YAML data."""
        
        # Extract model metadata
        model_info = model_data.get('model', {})
        gui_model = GuiModel(
            name=model_info.get('name', 'Unnamed Model'),
            description=model_info.get('description', '')
        )
        
        # Set simulation parameters
        gui_model.time_horizon = model_info.get('time_horizon', 50)
        gui_model.dt = model_info.get('dt', 0.25)
        gui_model.time_units = model_info.get('time_units', 'year')
        
        # Store dimensions
        gui_model.dimensions = model_data.get('dimensions', {})
        
        # Store functions
        gui_model.functions = model_data.get('functions', {})
        
        # Store constants (from scenario if available)
        if scenario_data and 'constants' in scenario_data:
            gui_model.constants = scenario_data['constants']
        else:
            gui_model.constants = model_data.get('constants', {})
            
        # Store original YAML data
        gui_model.original_yaml_data = {
            'model': model_data,
            'scenario': scenario_data
        }
        
        # Process model elements
        elements = model_data.get('elements', {})
        
        # Process stocks
        for stock_data in elements.get('stocks', []):
            component = self._create_stock_component(stock_data)
            gui_model.add_component(component)
            
        # Process flows
        for flow_data in elements.get('flows', []):
            component = self._create_flow_component(flow_data)
            gui_model.add_component(component)
            
        # Process calculators
        for calc_data in elements.get('calculators', []):
            component = self._create_calculator_component(calc_data)
            gui_model.add_component(component)
            
        # Process auxiliaries
        for aux_data in elements.get('auxiliaries', []):
            component = self._create_auxiliary_component(aux_data)
            gui_model.add_component(component)
            
        # Process connections
        for conn_data in model_data.get('connections', []):
            gui_model.add_connection(
                conn_data['from'],
                conn_data['to'],
                conn_data['type']
            )
            
        return gui_model
        
    def _create_stock_component(self, stock_data: Dict[str, Any]) -> ModelComponent:
        """Create a stock component from YAML data."""
        return ModelComponent(
            name=stock_data['name'],
            component_type='stock',
            properties={
                'initial_value': stock_data.get('initial_value'),
                'units': stock_data.get('units'),
                'spatial_dims': stock_data.get('spatial_dims', []),
                'min_value': stock_data.get('min_value'),
                'max_value': stock_data.get('max_value'),
                'description': stock_data.get('description', ''),
                'yaml_data': stock_data
            }
        )
        
    def _create_flow_component(self, flow_data: Dict[str, Any]) -> ModelComponent:
        """Create a flow component from YAML data."""
        return ModelComponent(
            name=flow_data['name'],
            component_type='flow',
            properties={
                'rate': flow_data.get('rate'),
                'units': flow_data.get('units'),
                'spatial_dims': flow_data.get('spatial_dims', []),
                'description': flow_data.get('description', ''),
                'parameters': flow_data.get('parameters', {}),
                'yaml_data': flow_data
            }
        )
        
    def _create_calculator_component(self, calc_data: Dict[str, Any]) -> ModelComponent:
        """Create a calculator component from YAML data."""
        return ModelComponent(
            name=calc_data['name'],
            component_type='calculator',
            properties={
                'expression': calc_data.get('expression'),
                'units': calc_data.get('units'),
                'spatial_dims': calc_data.get('spatial_dims', []),
                'description': calc_data.get('description', ''),
                'dependencies': calc_data.get('dependencies', []),
                'yaml_data': calc_data
            }
        )
        
    def _create_auxiliary_component(self, aux_data: Dict[str, Any]) -> ModelComponent:
        """Create an auxiliary component from YAML data."""
        return ModelComponent(
            name=aux_data['name'],
            component_type='auxiliary',
            properties={
                'value': aux_data.get('value'),
                'units': aux_data.get('units'),
                'description': aux_data.get('description', ''),
                'yaml_data': aux_data
            }
        )
        
    def get_available_scenarios(self, model_dir: str) -> List[str]:
        """Get list of available scenario files in the model directory."""
        model_path = Path(model_dir)
        scenario_files = []
        
        # Look for scenario parameter files
        for file_path in model_path.glob("*scenario*.yaml"):
            scenario_files.append(str(file_path))
            
        for file_path in model_path.glob("*scenario*.yml"):
            scenario_files.append(str(file_path))
            
        return sorted(scenario_files)
        
    def validate_model_structure(self, gui_model: GuiModel) -> Dict[str, Any]:
        """Validate the loaded model structure."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check for required components
        stocks = gui_model.get_components_by_type('stock')
        flows = gui_model.get_components_by_type('flow')
        
        if not stocks:
            validation_result['warnings'].append("No stocks found in model")
            
        if not flows:
            validation_result['warnings'].append("No flows found in model")
            
        # Check connections
        for from_name, to_name, conn_type in gui_model.connections:
            from_comp = gui_model.get_component(from_name)
            to_comp = gui_model.get_component(to_name)
            
            if not from_comp:
                validation_result['errors'].append(f"Connection source not found: {from_name}")
                validation_result['valid'] = False
                
            if not to_comp:
                validation_result['errors'].append(f"Connection target not found: {to_name}")
                validation_result['valid'] = False
                
        # Check for circular dependencies
        # (This would be a more complex check - simplified for now)
        
        return validation_result
