#!/usr/bin/env python3
"""
Project Management Integration Tests

Comprehensive tests for the enhanced project management system including:
- Project creation and file structure validation
- System and component management
- YAML compatibility with sd_toolkit
- Informants data management
- Round-trip testing (save/load consistency)
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

import yaml
import numpy as np
from project_management.project_manager import ProjectManager, Project, SystemModel
from project_management.component_manager import ComponentManager
from project_management.informants_manager import InformantsManager
from yaml_integration.yaml_loader import ModelComponent, YAMLModelLoader
from sd_toolkit.config import YAMLSystemBuilder


def test_project_creation():
    """Test basic project creation and file structure."""
    print("\n🧪 Testing project creation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_manager = ProjectManager(temp_dir)
        
        # Create project
        project = project_manager.create_project(
            name="Test Project",
            description="A test project for validation"
        )
        
        # Verify project structure
        project_path = Path(project.project_path)
        assert project_path.exists(), "Project directory not created"
        assert (project_path / "systems").exists(), "Systems directory not created"
        assert (project_path / "project_config.yaml").exists(), "Project config not created"
        
        # Verify project config content
        with open(project_path / "project_config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        assert config['project']['name'] == "Test Project"
        assert config['project']['description'] == "A test project for validation"
        
        print("✅ Project creation test passed")
        return True


def test_system_management():
    """Test system creation, saving, and loading."""
    print("\n🧪 Testing system management...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_manager = ProjectManager(temp_dir)
        component_manager = ComponentManager()
        
        # Create project and system
        project = project_manager.create_project("Test Project")
        system = SystemModel(
            name="Test System",
            description="A test system with components"
        )
        
        # Add dimensions
        system.dimensions = {
            'age': {'size': 2, 'labels': ['young', 'old']},
            'region': {'size': 2, 'labels': ['urban', 'rural']}
        }
        
        # Add components
        stock = ModelComponent(
            name="Population",
            component_type="stock",
            properties={
                'initial_value': 1000,
                'units': 'people',
                'spatial_dims': ['age', 'region'],
                'description': 'Test population stock'
            }
        )
        system.add_component(stock)
        
        flow = ModelComponent(
            name="Growth",
            component_type="flow",
            properties={
                'rate': 0.02,
                'units': 'people/year',
                'spatial_dims': ['age', 'region'],
                'description': 'Population growth flow'
            }
        )
        system.add_component(flow)
        
        # Add system to project
        project.add_system(system)
        
        # Save system
        component_manager.save_system(system, project)
        
        # Verify system structure
        system_path = Path(project.project_path) / "systems" / "test_system"
        assert system_path.exists(), "System directory not created"
        assert (system_path / "components").exists(), "Components directory not created"
        assert (system_path / "informants").exists(), "Informants directory not created"
        assert (system_path / "system_metadata.yaml").exists(), "System metadata not created"
        
        # Load system back
        loaded_system = component_manager.load_system(system_path, project)
        assert loaded_system is not None, "Failed to load system"
        assert loaded_system.name == "Test System"
        assert len(loaded_system.stocks) == 1
        assert len(loaded_system.flows) == 1
        assert "Population" in loaded_system.stocks
        assert "Growth" in loaded_system.flows
        
        print("✅ System management test passed")
        return True


def test_yaml_compatibility():
    """Test YAML compatibility with sd_toolkit."""
    print("\n🧪 Testing YAML compatibility with sd_toolkit...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_manager = ProjectManager(temp_dir)
        component_manager = ComponentManager()
        
        # Create a system with multidimensional components
        project = project_manager.create_project("YAML Test Project")
        system = SystemModel(name="YAML Test System")
        
        # Add realistic dimensions and components
        system.dimensions = {
            'age_group': {
                'size': 3,
                'labels': ['young', 'adult', 'elderly'],
                'description': 'Age groups'
            },
            'region': {
                'size': 2,
                'labels': ['urban', 'rural'],
                'description': 'Geographic regions'
            }
        }
        
        # Add multidimensional stock
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
                'spatial_dims': ['age_group', 'region'],
                'min_value': 0,
                'description': 'Population by age and region'
            }
        )
        system.add_component(population_stock)
        
        # Add flow with parameters
        birth_flow = ModelComponent(
            name="Births",
            component_type="flow",
            properties={
                'rate': 'exponential_growth',
                'units': 'people/year',
                'spatial_dims': ['age_group', 'region'],
                'parameters': {
                    'growth_rate': '$birth_rate'
                },
                'description': 'Birth flow'
            }
        )
        system.add_component(birth_flow)
        
        # Add calculator
        net_growth_calc = ModelComponent(
            name="Net_Growth",
            component_type="calculator",
            properties={
                'expression': 'Births - Deaths',
                'units': 'people/year',
                'spatial_dims': ['age_group', 'region'],
                'dependencies': ['Births', 'Deaths'],
                'description': 'Net population growth'
            }
        )
        system.add_component(net_growth_calc)
        
        # Add constants
        system.constants = {
            'initial_population': [[1000, 500], [2000, 1000], [500, 300]],
            'birth_rate': [0.025, 0.020, 0.005]
        }
        
        # Add connections
        system.connections = [
            ('Births', 'Population', 'inflow'),
            ('Net_Growth', 'Population', 'inflow')
        ]
        
        project.add_system(system)
        
        # Generate integrated YAML
        yaml_structure = component_manager.generate_integrated_yaml(system, project)
        
        # Verify YAML structure
        assert 'model' in yaml_structure
        assert 'dimensions' in yaml_structure
        assert 'constants' in yaml_structure
        assert 'elements' in yaml_structure
        assert 'connections' in yaml_structure
        
        # Verify elements structure
        elements = yaml_structure['elements']
        assert 'stocks' in elements
        assert 'flows' in elements
        assert 'calculators' in elements
        
        # Test with sd_toolkit YAMLSystemBuilder
        try:
            builder = YAMLSystemBuilder()
            sd_model = builder.build_from_dict(yaml_structure)
            
            assert sd_model.name == "YAML Test System"
            assert len(sd_model.stocks) >= 1
            assert len(sd_model.flows) >= 1
            assert len(sd_model.calculators) >= 1
            
            print("✅ YAML compatibility test passed")
            return True
            
        except Exception as e:
            print(f"❌ YAML compatibility test failed: {e}")
            return False


def test_informants_management():
    """Test informants data management and validation."""
    print("\n🧪 Testing informants management...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        informants_manager = InformantsManager()
        
        # Create system with dimensional inconsistencies
        system = SystemModel(name="Informants Test System")
        
        # Add dimensions
        system.dimensions = {
            'age': {'size': 3, 'labels': ['young', 'adult', 'elderly']},
            'region': {'size': 2, 'labels': ['urban', 'rural']}
        }
        
        # Add component with correct dimensions
        good_component = ModelComponent(
            name="Good_Component",
            component_type="stock",
            properties={
                'initial_value': {
                    'array': {
                        'shape': [3, 2],  # Matches dimensions
                        'values': [[100, 50], [200, 100], [50, 25]]
                    }
                },
                'spatial_dims': ['age', 'region'],
                'units': 'people'
            }
        )
        system.add_component(good_component)
        
        # Add component with dimension mismatch
        bad_component = ModelComponent(
            name="Bad_Component",
            component_type="stock",
            properties={
                'initial_value': {
                    'array': {
                        'shape': [2, 3],  # Wrong shape
                        'values': [[100, 200, 50], [50, 100, 25]]
                    }
                },
                'spatial_dims': ['age', 'region'],  # Claims to match but doesn't
                'units': 'people'
            }
        )
        system.add_component(bad_component)
        
        # Add component with undefined dimension reference
        undefined_component = ModelComponent(
            name="Undefined_Component",
            component_type="flow",
            properties={
                'rate': 0.02,
                'spatial_dims': ['age', 'income'],  # 'income' not defined
                'units': 'people/year'
            }
        )
        system.add_component(undefined_component)
        
        # Validate system
        validation_results = informants_manager.validate_system_informants(system)
        
        # Should find errors in bad_component and undefined_component
        assert len(validation_results) >= 2, f"Expected validation errors, got: {validation_results}"
        assert "Bad_Component" in validation_results
        assert "Undefined_Component" in validation_results
        
        # Good component should not have errors
        assert "Good_Component" not in validation_results
        
        # Test informants file creation
        informants_path = Path(temp_dir) / "test_informants.yaml"
        informants_manager.save_informants(system, informants_path)
        
        assert informants_path.exists(), "Informants file not created"
        
        # Load and verify informants
        loaded_informants = informants_manager.load_informants(informants_path)
        assert 'dimensions' in loaded_informants
        assert 'informants' in loaded_informants
        
        print("✅ Informants management test passed")
        return True


def test_round_trip_consistency():
    """Test save/load consistency (round-trip test)."""
    print("\n🧪 Testing round-trip consistency...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_manager = ProjectManager(temp_dir)
        component_manager = ComponentManager()
        
        # Create original project
        original_project = project_manager.create_project(
            "Round Trip Test",
            "Testing save/load consistency"
        )
        
        # Create system with complex structure
        system = SystemModel(
            name="Complex System",
            description="System with multiple component types"
        )
        
        # Add comprehensive dimensions
        system.dimensions = {
            'age': {'size': 3, 'labels': ['0-18', '19-65', '65+']},
            'income': {'size': 3, 'labels': ['low', 'medium', 'high']},
            'region': {'size': 2, 'labels': ['urban', 'rural']}
        }
        
        # Add multiple components of each type
        for i in range(2):
            stock = ModelComponent(
                name=f"Stock_{i}",
                component_type="stock",
                properties={
                    'initial_value': 1000 * (i + 1),
                    'units': 'units',
                    'spatial_dims': ['age', 'region'],
                    'description': f'Test stock {i}'
                }
            )
            system.add_component(stock)
            
            flow = ModelComponent(
                name=f"Flow_{i}",
                component_type="flow",
                properties={
                    'rate': 0.02 * (i + 1),
                    'units': 'units/year',
                    'spatial_dims': ['age', 'region'],
                    'description': f'Test flow {i}'
                }
            )
            system.add_component(flow)
            
            calc = ModelComponent(
                name=f"Calculator_{i}",
                component_type="calculator",
                properties={
                    'expression': f'Stock_{i} * 0.1',
                    'units': 'units',
                    'dependencies': [f'Stock_{i}'],
                    'description': f'Test calculator {i}'
                }
            )
            system.add_component(calc)
        
        # Add constants and connections
        system.constants = {
            'test_param_1': 100,
            'test_param_2': [1, 2, 3],
            'test_param_3': {'nested': 'value'}
        }
        
        system.connections = [
            ('Flow_0', 'Stock_0', 'inflow'),
            ('Flow_1', 'Stock_1', 'inflow')
        ]
        
        original_project.add_system(system)
        
        # Save project
        project_manager.save_project(original_project)
        
        # Load project back
        loaded_project = project_manager.load_project(original_project.project_path)
        
        # Verify project-level consistency
        assert loaded_project.name == original_project.name
        assert loaded_project.description == original_project.description
        assert len(loaded_project.systems) == len(original_project.systems)
        
        # Verify system-level consistency
        loaded_system = loaded_project.systems["Complex System"]
        assert loaded_system.name == system.name
        assert loaded_system.description == system.description
        assert len(loaded_system.stocks) == len(system.stocks)
        assert len(loaded_system.flows) == len(system.flows)
        assert len(loaded_system.calculators) == len(system.calculators)
        
        # Verify component-level consistency
        for stock_name in system.stocks:
            assert stock_name in loaded_system.stocks
            original_stock = system.stocks[stock_name]
            loaded_stock = loaded_system.stocks[stock_name]
            assert original_stock.name == loaded_stock.name
            assert original_stock.component_type == loaded_stock.component_type
        
        print("✅ Round-trip consistency test passed")
        return True


def run_all_tests():
    """Run all project management tests."""
    print("🚀 Running Project Management Integration Tests")
    print("=" * 60)
    
    tests = [
        test_project_creation,
        test_system_management,
        test_yaml_compatibility,
        test_informants_management,
        test_round_trip_consistency
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Project management system is ready.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review and fix issues.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
