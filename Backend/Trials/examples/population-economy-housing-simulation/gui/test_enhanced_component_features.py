#!/usr/bin/env python3
"""
Test Enhanced Component Features

This test validates the two main enhancements:
1. Default placeholder data for new components
2. Data persistence for component editing

Tests verify that:
- New components come with realistic placeholder data
- Data persists across editor close/reopen cycles
- YAML compatibility is maintained
- The multidimensional spreadsheet editor works correctly
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the GUI directory to Python path
gui_dir = Path(__file__).parent
sys.path.insert(0, str(gui_dir))

def test_placeholder_data_creation():
    """Test that new components come with placeholder data."""
    
    print("=" * 60)
    print("TEST 1: Placeholder Data Creation")
    print("=" * 60)
    
    try:
        from components.component_types import create_component_template, create_placeholder_dimensions
        
        print("Step 1: Test placeholder dimensions creation")
        placeholder_dims = create_placeholder_dimensions()
        print(f"   ✅ Created {len(placeholder_dims)} placeholder dimensions")
        
        # Verify dimension structure
        expected_dims = ['age_group', 'income_level', 'housing_type', 'time_period', 'zone', 'parcel']
        for dim_name in expected_dims:
            if dim_name in placeholder_dims:
                dim_data = placeholder_dims[dim_name]
                print(f"   ✅ {dim_name}: {len(dim_data['labels'])} labels, type: {dim_data['type']}")
            else:
                print(f"   ❌ Missing dimension: {dim_name}")
                return False
        
        print("\nStep 2: Test component template creation with placeholder data")
        
        # Test stock component
        stock_template = create_component_template('stock', 'test_population', include_placeholder_data=True)
        print(f"   ✅ Stock template created: {stock_template['name']}")
        print(f"   ✅ Spatial dims: {stock_template.get('spatial_dims', [])}")
        print(f"   ✅ Has multidimensional data: {'multidimensional_data' in stock_template}")
        
        if 'multidimensional_data' in stock_template:
            data_count = len(stock_template['multidimensional_data'])
            print(f"   ✅ Placeholder data entries: {data_count}")
            
            # Show sample data
            sample_keys = list(stock_template['multidimensional_data'].keys())[:3]
            for key in sample_keys:
                value = stock_template['multidimensional_data'][key]
                print(f"      Sample: {key} = {value}")
        
        # Test flow component
        flow_template = create_component_template('flow', 'test_migration', include_placeholder_data=True)
        print(f"   ✅ Flow template created: {flow_template['name']}")
        print(f"   ✅ Spatial dims: {flow_template.get('spatial_dims', [])}")
        
        # Test calculator component
        calc_template = create_component_template('calculator', 'test_calculator', include_placeholder_data=True)
        print(f"   ✅ Calculator template created: {calc_template['name']}")
        print(f"   ✅ Expression: {calc_template.get('expression', 'N/A')}")
        
        print("\n✅ TEST 1 PASSED: Placeholder data creation works correctly")
        return True
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_persistence():
    """Test that data persists across editor close/reopen cycles."""
    
    print("\n" + "=" * 60)
    print("TEST 2: Data Persistence")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        from PyQt6.QtWidgets import QApplication
        
        # Ensure QApplication exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("Step 1: Create component with placeholder data")
        
        # Create mock model
        class MockModel:
            def __init__(self):
                self.dimensions = {
                    'age_group': {
                        'labels': ['0-18', '19-35', '36-55'],
                        'description': 'Age groups',
                        'type': 'categorical',
                        'size': 3
                    },
                    'zone': {
                        'labels': ['downtown', 'suburban', 'rural'],
                        'description': 'Geographic zones',
                        'type': 'categorical',
                        'size': 3
                    },
                    'time_period': {
                        'labels': ['2020', '2021', '2022'],
                        'description': 'Time periods',
                        'type': 'temporal',
                        'size': 3
                    }
                }
        
        # Create component with placeholder data
        from components.component_types import create_component_template
        template = create_component_template('stock', 'test_population', include_placeholder_data=True)
        
        component = ModelComponent(
            name=template['name'],
            component_type='stock',
            properties=template
        )
        
        print(f"   ✅ Component created: {component.name}")
        print(f"   ✅ Initial multidimensional data entries: {len(component.properties.get('multidimensional_data', {}))}")
        
        print("\nStep 2: Create first editor instance and load data")
        
        mock_model = MockModel()
        editor1 = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        # Check that data was loaded
        initial_data = editor1.table_model.get_data_matrix()
        print(f"   ✅ Editor 1 loaded data entries: {len(initial_data)}")
        
        # Set dimensions to view the data
        editor1.dimension_selector.set_selected_dimensions('age_group', 'zone')
        
        print("\nStep 3: Modify data in first editor")
        
        # Add some test data
        test_key = ('test_population', '0-18', 'downtown')
        test_value = 12345
        editor1.table_model.data_matrix[test_key] = test_value
        editor1.is_modified = True
        
        print(f"   ✅ Added test data: {test_key} = {test_value}")
        
        # Simulate saving by calling update_component_data
        editor1.update_component_data()
        
        # Verify data was saved to component
        saved_data = component.properties.get('multidimensional_data', {})
        print(f"   ✅ Component now has {len(saved_data)} data entries")
        
        if test_key in saved_data:
            print(f"   ✅ Test data found in component: {saved_data[test_key]}")
        else:
            print(f"   ❌ Test data not found in component properties")
            return False
        
        # Close first editor
        editor1.close()
        print("   ✅ First editor closed")
        
        print("\nStep 4: Create second editor instance and verify data persistence")
        
        # Create new editor with the same component
        editor2 = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        # Check that data was loaded from component properties
        loaded_data = editor2.table_model.get_data_matrix()
        print(f"   ✅ Editor 2 loaded data entries: {len(loaded_data)}")
        
        if test_key in loaded_data:
            loaded_value = loaded_data[test_key]
            print(f"   ✅ Test data persisted: {test_key} = {loaded_value}")
            
            if loaded_value == test_value:
                print("   ✅ Data value matches exactly")
            else:
                print(f"   ❌ Data value mismatch: expected {test_value}, got {loaded_value}")
                return False
        else:
            print(f"   ❌ Test data not found in second editor")
            return False
        
        # Close second editor
        editor2.close()
        print("   ✅ Second editor closed")
        
        print("\n✅ TEST 2 PASSED: Data persistence works correctly")
        return True
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yaml_compatibility():
    """Test that YAML compatibility is maintained."""
    
    print("\n" + "=" * 60)
    print("TEST 3: YAML Compatibility")
    print("=" * 60)
    
    try:
        from yaml_integration.yaml_loader import ModelComponent, GuiModel
        from yaml_integration.yaml_saver import YAMLModelSaver
        from components.component_types import create_component_template
        import tempfile
        import yaml
        
        print("Step 1: Create GUI model with enhanced components")
        
        # Create model
        gui_model = GuiModel("Test Enhanced Model")
        
        # Add dimensions
        gui_model.dimensions = {
            'age_group': {
                'labels': ['0-18', '19-35', '36-55'],
                'description': 'Age groups',
                'type': 'categorical',
                'size': 3
            },
            'zone': {
                'labels': ['downtown', 'suburban'],
                'description': 'Geographic zones', 
                'type': 'categorical',
                'size': 2
            }
        }
        
        # Create component with placeholder data
        template = create_component_template('stock', 'population', include_placeholder_data=True)
        component = ModelComponent(
            name=template['name'],
            component_type='stock',
            properties=template
        )
        
        gui_model.add_component(component)
        print(f"   ✅ Created model with component: {component.name}")
        print(f"   ✅ Component has multidimensional data: {'multidimensional_data' in component.properties}")
        
        print("\nStep 2: Save model to YAML")
        
        saver = YAMLModelSaver()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, "test_model.yaml")
            
            # Save model
            saver.save_model_to_file(gui_model, model_path)
            print(f"   ✅ Model saved to: {model_path}")
            
            # Verify file was created
            if os.path.exists(model_path):
                print("   ✅ YAML file created successfully")
                
                # Load and inspect YAML content
                with open(model_path, 'r') as f:
                    yaml_content = yaml.safe_load(f)
                
                print(f"   ✅ YAML contains {len(yaml_content)} top-level sections")
                
                # Check for expected sections
                expected_sections = ['dimensions', 'stocks']
                for section in expected_sections:
                    if section in yaml_content:
                        print(f"   ✅ Found section: {section}")
                    else:
                        print(f"   ❌ Missing section: {section}")
                        return False
                
                # Check component data
                if 'stocks' in yaml_content and 'population' in yaml_content['stocks']:
                    stock_data = yaml_content['stocks']['population']
                    print(f"   ✅ Stock component saved with properties: {list(stock_data.keys())}")
                else:
                    print("   ❌ Stock component not found in YAML")
                    return False
                    
            else:
                print("   ❌ YAML file was not created")
                return False
        
        print("\n✅ TEST 3 PASSED: YAML compatibility maintained")
        return True
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    
    print("Testing Enhanced Component Features")
    print("=" * 60)
    
    # Run all tests
    tests = [
        test_placeholder_data_creation,
        test_data_persistence,
        test_yaml_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Enhanced component features are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
