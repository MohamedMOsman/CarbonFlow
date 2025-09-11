# Enhanced System Dynamics GUI - Project Management System

## Overview

The enhanced System Dynamics GUI now includes comprehensive hierarchical project management capabilities that support multi-project organization, system-level component management, and advanced multidimensional modeling workflows.

## Key Features

### 🏗️ **Hierarchical Project Organization**
- **Multi-project workspace** with automatic folder structure generation
- **System-level organization** within projects for complex modeling scenarios
- **Component categorization** (Stocks, Flows, Calculators, Informants)
- **Project metadata management** with version control and descriptions

### 📊 **Enhanced Component Management**
- **Automatic YAML file generation** maintaining full sd_toolkit compatibility
- **Component file organization** with separate files for each component type
- **Multidimensional data structures** with comprehensive validation
- **Parameter substitution** mechanisms preserved from existing patterns

### 🔍 **Informants Data Management**
- **Dimensional data separation** from component definitions
- **Referential integrity checking** between components and informants
- **Multi-value array dimensions** and scalar single-point dimensions
- **Validation and consistency checking** across all model elements

### 🖥️ **Enhanced User Interface**
- **Hierarchical tree view** with expandable project/system/component nodes
- **Context menus** for all operations (create, edit, delete, validate)
- **In-place editing** capabilities with real-time validation
- **Drag-and-drop support** for component organization

## Project Structure

The enhanced system automatically generates the following folder hierarchy:

```
project_name/
├── project_config.yaml          # Project metadata and configuration
├── systems/                     # All systems within the project
│   ├── system_1/
│   │   ├── components/          # Component definitions by type
│   │   │   ├── stocks.yaml      # Stock components
│   │   │   ├── flows.yaml       # Flow components
│   │   │   └── calculators.yaml # Calculator components
│   │   ├── informants/          # Dimensional data management
│   │   │   └── dimensional_data.yaml
│   │   └── system_metadata.yaml # System configuration and connections
│   └── system_2/
│       └── [same structure]
└── exports/                     # Generated files for notebooks/analysis
    ├── system_1_model_structure.yaml
    ├── system_1_scenario_parameters.yaml
    └── [other exports]
```

## Core Classes

### ProjectManager
Main interface for project operations:
- `create_project(name, description)` - Create new project with folder structure
- `load_project(project_path)` - Load existing project from disk
- `save_project(project)` - Save project and all systems

### SystemModel
Represents a system within a project:
- Organizes components by type (stocks, flows, calculators)
- Manages dimensions, functions, and connections
- Provides conversion to GuiModel for backward compatibility

### ComponentManager
Handles component file operations:
- `save_system(system, project)` - Save system with organized component files
- `load_system(system_path, project)` - Load system from directory structure
- `generate_integrated_yaml(system, project)` - Create sd_toolkit compatible YAML
- `export_system_for_notebook(system, project, export_dir)` - Generate notebook-ready files

### InformantsManager
Manages dimensional data and validation:
- `validate_system_informants(system)` - Check dimensional consistency
- `save_informants(system, informants_path)` - Save dimensional data
- `load_informants(informants_path)` - Load dimensional data

## Usage Examples

### Creating a New Project

```python
from project_management import ProjectManager, SystemModel
from yaml_integration.yaml_loader import ModelComponent

# Initialize project manager
project_manager = ProjectManager()

# Create project
project = project_manager.create_project(
    name="Climate Adaptation Study",
    description="Multi-system climate adaptation modeling"
)

# Create system
population_system = SystemModel(
    name="Population Dynamics",
    description="Demographic modeling with climate sensitivity"
)

# Add dimensions
population_system.dimensions = {
    'age_group': {
        'size': 3,
        'labels': ['young', 'adult', 'elderly'],
        'description': 'Age group categories'
    },
    'region': {
        'size': 2,
        'labels': ['urban', 'rural'],
        'description': 'Geographic regions'
    }
}

# Add components
population_stock = ModelComponent(
    name="Population",
    component_type="stock",
    properties={
        'initial_value': {
            'array': {
                'shape': [3, 2],
                'values': '$initial_population'
            }
        },
        'units': 'people',
        'spatial_dims': ['age_group', 'region']
    }
)
population_system.add_component(population_stock)

# Add system to project
project.add_system(population_system)

# Save project
project_manager.save_project(project)
```

### Loading and Working with Projects

```python
# Load existing project
project = project_manager.load_project("/path/to/project")

# Access systems
population_system = project.get_system("Population Dynamics")

# Validate system
from project_management import InformantsManager
informants_manager = InformantsManager()
validation_results = informants_manager.validate_system_informants(population_system)

if validation_results:
    print("Validation issues found:")
    for component_name, errors in validation_results.items():
        print(f"  {component_name}: {', '.join(errors)}")
else:
    print("System validation passed!")
```

### Exporting for Notebooks

```python
from project_management import ComponentManager
from pathlib import Path

component_manager = ComponentManager()

# Export system for notebook use
export_paths = component_manager.export_system_for_notebook(
    population_system, 
    project, 
    Path("exports/population_model")
)

print(f"Model structure: {export_paths['model_structure']}")
print(f"Scenario parameters: {export_paths['scenario_parameters']}")
```

## GUI Integration

### Enhanced Main Window
The `EnhancedSystemDynamicsMainWindow` provides:
- **Project tree sidebar** with hierarchical navigation
- **Tabbed center panel** for canvas and other views
- **Enhanced component palette** and inspector
- **Menu system** with project operations
- **Backward compatibility** with existing single-model workflows

### Project Tree Widget
The `ProjectTreeWidget` offers:
- **Expandable tree structure** showing projects → systems → components
- **Context menus** for all operations
- **Drag-and-drop** component organization
- **Real-time validation** indicators
- **In-place renaming** capabilities

### Enhanced Component Editor
The `EnhancedComponentEditor` includes:
- **Project context awareness** with system dimension validation
- **Integrated informants management** 
- **Real-time validation feedback**
- **Enhanced multidimensional editing**
- **Referential integrity checking**

## Testing and Validation

### Running Tests
```bash
cd examples/population-economy-housing-simulation/gui
python test_project_management_integration.py
```

### Demo Application
```bash
cd examples/population-economy-housing-simulation/gui
python demo_enhanced_project_management.py
```

## Backward Compatibility

The enhanced system maintains full backward compatibility with existing workflows:

- **Legacy YAML models** can be imported and converted to project structure
- **Existing GUI components** continue to work with GuiModel conversion
- **sd_toolkit integration** preserved through YAML generation methods
- **Notebook workflows** supported through export functionality

## Migration Guide

### From Single Models to Projects

1. **Create new project** using the enhanced GUI or API
2. **Import existing YAML model** using legacy import functions
3. **Organize into systems** by grouping related components
4. **Define dimensions** at the system level
5. **Validate and save** using the new project structure

### Updating Existing Notebooks

1. **Export systems** using `export_system_for_notebook()`
2. **Update notebook imports** to use generated files
3. **Leverage enhanced validation** for model consistency
4. **Use project structure** for better organization

## Future Enhancements

- **Version control integration** for project history
- **Collaborative editing** capabilities
- **Model comparison tools** across systems/projects
- **Advanced visualization** of project hierarchies
- **Template system** for common project patterns
- **Cloud storage integration** for project sharing

## Support and Documentation

For additional help:
- Review the comprehensive test suite in `test_project_management_integration.py`
- Run the demo application in `demo_enhanced_project_management.py`
- Check existing documentation in the `inspector/` and `yaml_integration/` modules
- Examine the multidimensional modeling examples in the `dasht/` directory
