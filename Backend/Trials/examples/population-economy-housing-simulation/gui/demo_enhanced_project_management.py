#!/usr/bin/env python3
"""
Enhanced Project Management Demo

Demonstrates the new hierarchical project management capabilities including:
- Multi-project organization with automatic folder structure
- System-level component organization
- Enhanced multidimensional editing
- Informants data management
- Integration with existing sd_toolkit patterns
"""

import sys
import os
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt

from enhanced_main_window import EnhancedSystemDynamicsMainWindow
from project_management.project_manager import ProjectManager, Project, SystemModel
from project_management.component_manager import ComponentManager
from project_management.informants_manager import InformantsManager
from yaml_integration.yaml_loader import ModelComponent


def create_demo_project():
    """Create a demonstration project with sample systems and components."""
    
    print("🏗️ Creating demonstration project...")
    
    # Initialize project manager
    project_manager = ProjectManager()
    component_manager = ComponentManager()
    informants_manager = InformantsManager()
    
    # Create project
    project = project_manager.create_project(
        name="Climate Adaptation Demo",
        description="Demonstration project for climate adaptation modeling with hierarchical organization"
    )
    
    print(f"✅ Created project: {project.name}")
    print(f"📁 Project path: {project.project_path}")
    
    # Create first system: Population Dynamics
    population_system = SystemModel(
        name="Population Dynamics",
        description="Multidimensional population modeling with climate sensitivity"
    )
    
    # Add dimensions to population system
    population_system.dimensions = {
        'age_group': {
            'size': 3,
            'labels': ['young_0_18', 'adult_19_65', 'elderly_65_plus'],
            'description': 'Age group categories',
            'type': 'categorical'
        },
        'income_level': {
            'size': 3,
            'labels': ['low_income', 'medium_income', 'high_income'],
            'description': 'Income level categories',
            'type': 'ordinal'
        },
        'region': {
            'size': 2,
            'labels': ['urban', 'rural'],
            'description': 'Geographic regions',
            'type': 'spatial'
        }
    }
    
    # Add components to population system
    population_stock = ModelComponent(
        name="Population",
        component_type="stock",
        properties={
            'initial_value': {
                'array': {
                    'shape': [3, 3, 2],
                    'values': '$initial_population_distribution'
                }
            },
            'units': 'people',
            'spatial_dims': ['age_group', 'income_level', 'region'],
            'min_value': 0,
            'description': 'Multidimensional population stock'
        }
    )
    population_system.add_component(population_stock)
    
    births_flow = ModelComponent(
        name="Births",
        component_type="flow",
        properties={
            'rate': 'birth_rate_function',
            'units': 'people/year',
            'spatial_dims': ['age_group', 'income_level', 'region'],
            'description': 'Birth flow with demographic sensitivity',
            'parameters': {
                'base_birth_rate': '$base_birth_rate',
                'climate_fertility_impact': '$climate_fertility_impact'
            }
        }
    )
    population_system.add_component(births_flow)
    
    deaths_flow = ModelComponent(
        name="Deaths",
        component_type="flow",
        properties={
            'rate': 'mortality_rate_function',
            'units': 'people/year',
            'spatial_dims': ['age_group', 'income_level', 'region'],
            'description': 'Death flow with age and climate sensitivity',
            'parameters': {
                'base_mortality_rate': '$base_mortality_rate',
                'climate_mortality_impact': '$climate_mortality_impact'
            }
        }
    )
    population_system.add_component(deaths_flow)
    
    net_migration_calc = ModelComponent(
        name="Net_Migration",
        component_type="calculator",
        properties={
            'expression': 'Economic_Migration_In - Climate_Migration_Out',
            'units': 'people/year',
            'spatial_dims': ['age_group', 'income_level', 'region'],
            'description': 'Net migration calculator',
            'dependencies': ['Economic_Migration_In', 'Climate_Migration_Out']
        }
    )
    population_system.add_component(net_migration_calc)
    
    # Add constants
    population_system.constants = {
        'initial_population_distribution': [
            [[1500, 800], [2000, 1000], [1000, 500]],  # young
            [[2500, 1200], [3000, 1500], [1500, 800]], # adult
            [[600, 400], [800, 500], [400, 300]]       # elderly
        ],
        'base_birth_rate': [0.025, 0.020, 0.015],  # by age group
        'base_mortality_rate': [0.005, 0.010, 0.050],  # by age group
        'climate_fertility_impact': 0.1,
        'climate_mortality_impact': 0.15
    }
    
    # Add connections
    population_system.connections = [
        ('Births', 'Population', 'inflow'),
        ('Deaths', 'Population', 'outflow'),
        ('Net_Migration', 'Population', 'inflow')
    ]
    
    project.add_system(population_system)
    print(f"✅ Added system: {population_system.name}")
    
    # Create second system: Flood Protection
    flood_system = SystemModel(
        name="Flood Protection",
        description="Parcel-based flood protection measures with building-specific adaptations"
    )
    
    # Add dimensions to flood system
    flood_system.dimensions = {
        'parcel': {
            'size': 3,
            'labels': ['1001', '1002', '1003'],
            'description': 'Property parcel identifiers',
            'type': 'categorical'
        },
        'building_type': {
            'size': 2,
            'labels': ['residential', 'commercial'],
            'description': 'Building type categories',
            'type': 'categorical'
        },
        'year': {
            'size': 5,
            'labels': ['2020', '2025', '2030', '2035', '2040'],
            'description': 'Time periods for adaptation measures',
            'type': 'temporal'
        }
    }
    
    # Add flood protection components
    basement_height_stock = ModelComponent(
        name="Basement_Height_Measures",
        component_type="stock",
        properties={
            'initial_value': 0,
            'units': 'meters',
            'spatial_dims': ['parcel', 'building_type'],
            'description': 'Basement height improvement measures'
        }
    )
    flood_system.add_component(basement_height_stock)
    
    offset_measures_stock = ModelComponent(
        name="Structure_Offset_Measures",
        component_type="stock",
        properties={
            'initial_value': 0,
            'units': 'meters',
            'spatial_dims': ['parcel', 'building_type'],
            'description': 'Structure offset from ground improvements'
        }
    )
    flood_system.add_component(offset_measures_stock)
    
    improvement_flow = ModelComponent(
        name="Flood_Protection_Improvements",
        component_type="flow",
        properties={
            'rate': 'improvement_rate_function',
            'units': 'meters/year',
            'spatial_dims': ['parcel', 'building_type'],
            'description': 'Rate of flood protection improvements',
            'parameters': {
                'improvement_rate': '$improvement_rate_by_type',
                'climate_urgency_factor': '$climate_urgency_factor'
            }
        }
    )
    flood_system.add_component(improvement_flow)
    
    project.add_system(flood_system)
    print(f"✅ Added system: {flood_system.name}")
    
    # Create third system: Albedo Management
    albedo_system = SystemModel(
        name="Albedo Management",
        description="Urban albedo modification for climate adaptation"
    )
    
    # Add dimensions to albedo system
    albedo_system.dimensions = {
        'zone': {
            'size': 4,
            'labels': ['downtown', 'residential', 'industrial', 'parks'],
            'description': 'Urban zones',
            'type': 'spatial'
        },
        'time_period': {
            'size': 3,
            'labels': ['2020_2030', '2030_2040', '2040_2050'],
            'description': '10-year time periods',
            'type': 'temporal'
        }
    }
    
    # Add albedo components
    albedo_stock = ModelComponent(
        name="Albedo_Modifications",
        component_type="stock",
        properties={
            'initial_value': 0.3,  # Base urban albedo
            'units': 'albedo_units',
            'spatial_dims': ['zone', 'time_period'],
            'description': 'Albedo modification measures by zone and time'
        }
    )
    albedo_system.add_component(albedo_stock)
    
    albedo_improvement_flow = ModelComponent(
        name="Albedo_Improvements",
        component_type="flow",
        properties={
            'rate': 'albedo_improvement_function',
            'units': 'albedo_units/year',
            'spatial_dims': ['zone', 'time_period'],
            'description': 'Rate of albedo improvements',
            'parameters': {
                'improvement_rate': '$albedo_improvement_rate',
                'temperature_sensitivity': '$temperature_sensitivity'
            }
        }
    )
    albedo_system.add_component(albedo_improvement_flow)
    
    temperature_impact_calc = ModelComponent(
        name="Temperature_Impact",
        component_type="calculator",
        properties={
            'expression': 'Albedo_Modifications * temperature_reduction_factor',
            'units': 'degrees_C',
            'spatial_dims': ['zone', 'time_period'],
            'description': 'Temperature reduction from albedo changes',
            'dependencies': ['Albedo_Modifications'],
            'parameters': {
                'temperature_reduction_factor': '$temperature_reduction_factor'
            }
        }
    )
    albedo_system.add_component(temperature_impact_calc)
    
    project.add_system(albedo_system)
    print(f"✅ Added system: {albedo_system.name}")
    
    # Save the complete project
    project_manager.save_project(project)
    print(f"💾 Saved complete project with {len(project.systems)} systems")
    
    # Validate all systems
    print("\n🔍 Validating project systems...")
    for system_name, system in project.systems.items():
        validation_results = informants_manager.validate_system_informants(system)
        if validation_results:
            print(f"⚠️  {system_name}: Found {len(validation_results)} validation issues")
            for component_name, errors in validation_results.items():
                print(f"   • {component_name}: {', '.join(errors)}")
        else:
            print(f"✅ {system_name}: Validation passed")
    
    return project


def main():
    """Main demonstration function."""
    
    print("🚀 Enhanced System Dynamics GUI - Project Management Demo")
    print("=" * 60)
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced System Dynamics Modeler")
    
    try:
        # Create demonstration project
        demo_project = create_demo_project()
        
        print(f"\n🎯 Demo project created successfully!")
        print(f"📊 Project contains {len(demo_project.systems)} systems:")
        for system_name, system in demo_project.systems.items():
            component_count = len(system.get_all_components())
            print(f"   • {system_name}: {component_count} components")
        
        # Create and show enhanced main window
        print(f"\n🖥️  Launching enhanced GUI...")
        main_window = EnhancedSystemDynamicsMainWindow()
        
        # Load the demo project into the GUI
        main_window.project_tree.add_project_to_tree(demo_project)
        main_window.current_project = demo_project
        main_window.update_window_title()
        
        main_window.show()
        
        # Show information dialog
        QMessageBox.information(
            main_window,
            "Demo Project Loaded",
            f"Demonstration project '{demo_project.name}' has been loaded!\n\n"
            f"Features demonstrated:\n"
            f"• Hierarchical project organization\n"
            f"• Multi-system architecture\n"
            f"• Multidimensional components\n"
            f"• Climate adaptation modeling\n"
            f"• Component validation\n\n"
            f"Explore the project tree on the left to see the organization."
        )
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()
        
        if 'app' in locals():
            QMessageBox.critical(None, "Demo Error", f"Failed to run demo: {e}")


if __name__ == "__main__":
    main()
