#!/usr/bin/env python3
"""
Simple Test for Component Enhancements

Tests the core functionality without GUI dependencies:
1. Placeholder data creation
2. Component template generation
3. Data structure validation
"""

import sys
import os
from pathlib import Path

# Add the GUI directory to Python path
gui_dir = Path(__file__).parent
sys.path.insert(0, str(gui_dir))

def test_placeholder_data():
    """Test placeholder data creation."""
    
    print("=" * 50)
    print("TEST 1: Placeholder Data Creation")
    print("=" * 50)
    
    try:
        from components.component_types import create_placeholder_dimensions, create_placeholder_data
        
        # Test dimension creation
        dims = create_placeholder_dimensions()
        print(f"✅ Created {len(dims)} placeholder dimensions")
        
        expected_dims = ['age_group', 'income_level', 'housing_type', 'time_period', 'zone', 'parcel']
        for dim_name in expected_dims:
            if dim_name in dims:
                labels = dims[dim_name]['labels']
                print(f"   {dim_name}: {len(labels)} labels - {labels[:3]}...")
            else:
                print(f"❌ Missing dimension: {dim_name}")
                return False
        
        # Test data creation
        spatial_dims = ['age_group', 'zone', 'time_period']
        sample_data = create_placeholder_data('stock', 'test_population', spatial_dims)
        
        print(f"✅ Created {len(sample_data)} sample data entries")
        
        # Show some sample entries
        sample_keys = list(sample_data.keys())[:5]
        for key in sample_keys:
            print(f"   {key} = {sample_data[key]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_component_templates():
    """Test component template creation."""
    
    print("\n" + "=" * 50)
    print("TEST 2: Component Template Creation")
    print("=" * 50)
    
    try:
        from components.component_types import create_component_template
        
        # Test stock template
        stock_template = create_component_template('stock', 'test_population', include_placeholder_data=True)
        print(f"✅ Stock template: {stock_template['name']}")
        print(f"   Spatial dims: {stock_template.get('spatial_dims', [])}")
        print(f"   Units: {stock_template.get('units', 'N/A')}")
        print(f"   Initial value: {stock_template.get('initial_value', 'N/A')}")
        
        multidim_data = stock_template.get('multidimensional_data', {})
        print(f"   Multidimensional data entries: {len(multidim_data)}")
        
        if multidim_data:
            sample_key = list(multidim_data.keys())[0]
            print(f"   Sample data: {sample_key} = {multidim_data[sample_key]}")
        
        # Test flow template
        flow_template = create_component_template('flow', 'test_migration', include_placeholder_data=True)
        print(f"✅ Flow template: {flow_template['name']}")
        print(f"   Spatial dims: {flow_template.get('spatial_dims', [])}")
        print(f"   Rate: {flow_template.get('rate', 'N/A')}")
        
        # Test calculator template
        calc_template = create_component_template('calculator', 'test_calc', include_placeholder_data=True)
        print(f"✅ Calculator template: {calc_template['name']}")
        print(f"   Expression: {calc_template.get('expression', 'N/A')}")
        print(f"   Dependencies: {calc_template.get('dependencies', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_structure():
    """Test data structure validation."""
    
    print("\n" + "=" * 50)
    print("TEST 3: Data Structure Validation")
    print("=" * 50)
    
    try:
        from components.component_types import create_component_template
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create component with template
        template = create_component_template('stock', 'population', include_placeholder_data=True)
        component = ModelComponent(
            name=template['name'],
            component_type='stock',
            properties=template
        )
        
        print(f"✅ Component created: {component.name}")
        print(f"   Type: {component.component_type}")
        
        # Check properties
        props = component.properties
        print(f"   Properties: {list(props.keys())}")
        
        # Check multidimensional data
        multidim_data = props.get('multidimensional_data', {})
        print(f"   Multidimensional data entries: {len(multidim_data)}")
        
        if multidim_data:
            # Validate data structure
            valid_entries = 0
            for key, value in multidim_data.items():
                if isinstance(key, tuple) and len(key) >= 2:
                    if key[0] == component.name:  # First element should be component name
                        valid_entries += 1
            
            print(f"   Valid data entries: {valid_entries}/{len(multidim_data)}")
            
            if valid_entries == len(multidim_data):
                print("✅ All data entries have valid structure")
            else:
                print("❌ Some data entries have invalid structure")
                return False
        
        # Test data persistence simulation
        print("\n   Testing data persistence simulation...")
        
        # Simulate saving data to component
        test_data = {('population', 'young', 'downtown'): 5000}
        props['multidimensional_data'].update(test_data)
        
        # Simulate loading data from component
        loaded_data = props.get('multidimensional_data', {})
        test_key = ('population', 'young', 'downtown')
        
        if test_key in loaded_data and loaded_data[test_key] == 5000:
            print("✅ Data persistence simulation successful")
        else:
            print("❌ Data persistence simulation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    
    print("Testing Component Enhancements (Simple)")
    print("=" * 50)
    
    tests = [
        test_placeholder_data,
        test_component_templates,
        test_data_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\nEnhancements working correctly:")
        print("✅ 1. Default placeholder data for new components")
        print("✅ 2. Data structure validation")
        print("✅ 3. Component template generation")
        return True
    else:
        print("❌ Some tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
