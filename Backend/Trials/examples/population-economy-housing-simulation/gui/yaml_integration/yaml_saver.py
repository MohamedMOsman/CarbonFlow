"""
YAML Model Saver

This module provides functionality to save GUI models back to YAML format
compatible with the sd_toolkit framework.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import OrderedDict

from yaml_integration.yaml_loader import GuiModel, ModelComponent


class YAMLModelSaver:
    """Saves GUI models back to YAML format."""
    
    def __init__(self):
        pass
        
    def save_model_to_file(self, gui_model: GuiModel, model_path: str, 
                          scenario_path: Optional[str] = None, 
                          save_scenario_separately: bool = True) -> None:
        """
        Save GUI model to YAML file(s).
        
        Parameters:
        -----------
        gui_model : GuiModel
            The GUI model to save
        model_path : str
            Path for the model structure file
        scenario_path : str, optional
            Path for the scenario parameters file
        save_scenario_separately : bool
            Whether to save scenario parameters in a separate file
        """
        
        # Generate model structure YAML
        model_yaml = self._generate_model_yaml(gui_model)
        
        if save_scenario_separately and gui_model.constants:
            # Save model structure without constants
            self._save_yaml_file(model_yaml, model_path)
            
            # Generate and save scenario YAML
            if scenario_path:
                scenario_yaml = self._generate_scenario_yaml(gui_model)
                self._save_yaml_file(scenario_yaml, scenario_path)
        else:
            # Include constants in model file
            if gui_model.constants:
                model_yaml['constants'] = gui_model.constants
            self._save_yaml_file(model_yaml, model_path)
            
    def _generate_model_yaml(self, gui_model: GuiModel) -> Dict[str, Any]:
        """Generate model structure YAML from GUI model."""
        
        model_yaml = OrderedDict()
        
        # Model metadata
        model_yaml['model'] = OrderedDict([
            ('name', gui_model.name),
            ('description', gui_model.description),
            ('time_horizon', gui_model.time_horizon),
            ('dt', gui_model.dt),
            ('time_units', gui_model.time_units)
        ])
        
        # Dimensions
        if gui_model.dimensions:
            model_yaml['dimensions'] = gui_model.dimensions
            
        # Functions
        if gui_model.functions:
            model_yaml['functions'] = gui_model.functions
            
        # Elements
        elements = OrderedDict()
        
        # Stocks
        stocks = gui_model.get_components_by_type('stock')
        if stocks:
            elements['stocks'] = [self._component_to_yaml(comp) for comp in stocks]
            
        # Flows
        flows = gui_model.get_components_by_type('flow')
        if flows:
            elements['flows'] = [self._component_to_yaml(comp) for comp in flows]
            
        # Calculators
        calculators = gui_model.get_components_by_type('calculator')
        if calculators:
            elements['calculators'] = [self._component_to_yaml(comp) for comp in calculators]
            
        # Auxiliaries
        auxiliaries = gui_model.get_components_by_type('auxiliary')
        if auxiliaries:
            elements['auxiliaries'] = [self._component_to_yaml(comp) for comp in auxiliaries]
            
        if elements:
            model_yaml['elements'] = elements
            
        # Connections
        if gui_model.connections:
            connections = []
            for from_name, to_name, conn_type in gui_model.connections:
                connections.append(OrderedDict([
                    ('from', from_name),
                    ('to', to_name),
                    ('type', conn_type)
                ]))
            model_yaml['connections'] = connections
            
        return model_yaml
        
    def _generate_scenario_yaml(self, gui_model: GuiModel) -> Dict[str, Any]:
        """Generate scenario parameters YAML from GUI model."""
        
        scenario_yaml = OrderedDict()
        
        # Scenario metadata
        scenario_yaml['scenario'] = OrderedDict([
            ('name', f"{gui_model.name} Scenario"),
            ('description', f"Scenario parameters for {gui_model.name}"),
            ('version', '1.0'),
            ('model_file', 'model_structure.yaml')  # Default reference
        ])
        
        # Constants
        if gui_model.constants:
            scenario_yaml['constants'] = gui_model.constants
            
        return scenario_yaml
        
    def _component_to_yaml(self, component: ModelComponent) -> Dict[str, Any]:
        """Convert a GUI component back to YAML format."""
        
        # Start with original YAML data if available
        if 'yaml_data' in component.properties:
            yaml_data = component.properties['yaml_data'].copy()
        else:
            yaml_data = OrderedDict()
            
        # Update with current component properties
        yaml_data['name'] = component.name
        
        if component.component_type == 'stock':
            self._update_stock_yaml(yaml_data, component)
        elif component.component_type == 'flow':
            self._update_flow_yaml(yaml_data, component)
        elif component.component_type == 'calculator':
            self._update_calculator_yaml(yaml_data, component)
        elif component.component_type == 'auxiliary':
            self._update_auxiliary_yaml(yaml_data, component)
            
        # Remove internal properties
        yaml_data.pop('yaml_data', None)
        yaml_data.pop('position', None)  # Remove position as it's GUI-specific

        # Clean up data for YAML serialization
        yaml_data = self._clean_for_serialization(yaml_data)

        return yaml_data
        
    def _update_stock_yaml(self, yaml_data: Dict[str, Any], component: ModelComponent):
        """Update YAML data for a stock component."""
        props = component.properties
        
        if props.get('initial_value') is not None:
            yaml_data['initial_value'] = props['initial_value']
        if props.get('units'):
            yaml_data['units'] = props['units']
        if props.get('spatial_dims'):
            yaml_data['spatial_dims'] = props['spatial_dims']
        if props.get('min_value') is not None:
            yaml_data['min_value'] = props['min_value']
        if props.get('max_value') is not None:
            yaml_data['max_value'] = props['max_value']
        if props.get('description'):
            yaml_data['description'] = props['description']
            
    def _update_flow_yaml(self, yaml_data: Dict[str, Any], component: ModelComponent):
        """Update YAML data for a flow component."""
        props = component.properties
        
        if props.get('rate') is not None:
            yaml_data['rate'] = props['rate']
        if props.get('units'):
            yaml_data['units'] = props['units']
        if props.get('spatial_dims'):
            yaml_data['spatial_dims'] = props['spatial_dims']
        if props.get('description'):
            yaml_data['description'] = props['description']
        if props.get('parameters'):
            yaml_data['parameters'] = props['parameters']
            
    def _update_calculator_yaml(self, yaml_data: Dict[str, Any], component: ModelComponent):
        """Update YAML data for a calculator component."""
        props = component.properties
        
        if props.get('expression'):
            yaml_data['expression'] = props['expression']
        if props.get('units'):
            yaml_data['units'] = props['units']
        if props.get('spatial_dims'):
            yaml_data['spatial_dims'] = props['spatial_dims']
        if props.get('description'):
            yaml_data['description'] = props['description']
        if props.get('dependencies'):
            yaml_data['dependencies'] = props['dependencies']
            
    def _update_auxiliary_yaml(self, yaml_data: Dict[str, Any], component: ModelComponent):
        """Update YAML data for an auxiliary component."""
        props = component.properties
        
        if props.get('value') is not None:
            yaml_data['value'] = props['value']
        if props.get('units'):
            yaml_data['units'] = props['units']
        if props.get('description'):
            yaml_data['description'] = props['description']

    def _clean_for_serialization(self, data: Any) -> Any:
        """Clean data for YAML/JSON serialization by converting tuples to lists."""
        if isinstance(data, dict):
            return {key: self._clean_for_serialization(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._clean_for_serialization(item) for item in data]
        elif isinstance(data, tuple):
            return list(data)  # Convert tuples to lists
        else:
            return data

    def _save_yaml_file(self, data: Dict[str, Any], file_path: str):
        """Save data to a YAML file with proper formatting."""
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Clean data before saving
        clean_data = self._clean_for_serialization(data)

        with open(path, 'w', encoding='utf-8') as file:
            yaml.dump(
                clean_data,
                file,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                width=120,
                allow_unicode=True
            )
            
    def export_model_summary(self, gui_model: GuiModel) -> str:
        """Export a human-readable summary of the model."""
        
        summary = []
        summary.append(f"Model: {gui_model.name}")
        summary.append(f"Description: {gui_model.description}")
        summary.append(f"Time Horizon: {gui_model.time_horizon} {gui_model.time_units}")
        summary.append(f"Time Step: {gui_model.dt} {gui_model.time_units}")
        summary.append("")
        
        # Dimensions
        if gui_model.dimensions:
            summary.append("Dimensions:")
            for dim_name, dim_info in gui_model.dimensions.items():
                labels = dim_info.get('labels', [])
                summary.append(f"  - {dim_name}: {labels} (size: {dim_info.get('size', len(labels))})")
            summary.append("")
            
        # Components by type
        for comp_type in ['stock', 'flow', 'calculator', 'auxiliary']:
            components = gui_model.get_components_by_type(comp_type)
            if components:
                summary.append(f"{comp_type.title()}s ({len(components)}):")
                for comp in components:
                    dims = comp.properties.get('spatial_dims', [])
                    dims_str = f" [{', '.join(dims)}]" if dims else ""
                    units = comp.properties.get('units', '')
                    units_str = f" ({units})" if units else ""
                    summary.append(f"  - {comp.name}{dims_str}{units_str}")
                summary.append("")
                
        # Connections
        if gui_model.connections:
            summary.append(f"Connections ({len(gui_model.connections)}):")
            for from_name, to_name, conn_type in gui_model.connections:
                summary.append(f"  - {from_name} → {to_name} ({conn_type})")
            summary.append("")
            
        return "\n".join(summary)
