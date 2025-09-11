#!/usr/bin/env python3
"""
Test script to validate multidimensional improvement rates in climate adaptation model.
This script tests that the basement_height_improvement_rate and offset_improvement_rate
parameters are correctly structured as multidimensional arrays.
"""

import sys
import os
import yaml
import numpy as np

# Add the parent directory to the path to import the BPTK framework
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def load_yaml_file(filepath):
    """Load and parse a YAML file."""
    try:
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def validate_multidimensional_structure(data, param_name, expected_shape):
    """Validate that a parameter has the expected multidimensional structure."""
    print(f"\n=== Validating {param_name} ===")
    
    if param_name not in data.get('constants', {}):
        print(f"❌ {param_name} not found in constants")
        return False
    
    param_data = data['constants'][param_name]
    
    # Convert to numpy array for shape validation
    try:
        param_array = np.array(param_data)
        actual_shape = param_array.shape
        
        print(f"Expected shape: {expected_shape}")
        print(f"Actual shape: {actual_shape}")
        
        if actual_shape == tuple(expected_shape):
            print(f"✅ {param_name} has correct shape")
            
            # Validate that all values are positive numbers
            if np.all(param_array > 0):
                print(f"✅ All values in {param_name} are positive")
            else:
                print(f"❌ Some values in {param_name} are not positive")
                return False
                
            # Print sample values for verification
            print(f"Sample values:")
            print(f"  parcel_1001, pre_war, residential: {param_array[0, 0, 0]}")
            print(f"  parcel_1002, post_war, commercial: {param_array[1, 1, 1]}")
            print(f"  parcel_1003, modern, residential: {param_array[2, 2, 0]}")
            
            return True
        else:
            print(f"❌ {param_name} has incorrect shape")
            return False
            
    except Exception as e:
        print(f"❌ Error converting {param_name} to array: {e}")
        return False

def validate_dimension_consistency(model_data):
    """Validate that dimensions are consistently defined."""
    print("\n=== Validating Dimension Consistency ===")
    
    dimensions = model_data.get('dimensions', {})
    expected_dims = ['parcel', 'year_built_cohort', 'building_type']
    expected_sizes = [3, 3, 2]
    
    for i, dim_name in enumerate(expected_dims):
        if dim_name not in dimensions:
            print(f"❌ Dimension {dim_name} not found")
            return False
        
        dim_info = dimensions[dim_name]
        if dim_info.get('size') != expected_sizes[i]:
            print(f"❌ Dimension {dim_name} has incorrect size: {dim_info.get('size')} (expected {expected_sizes[i]})")
            return False
        
        print(f"✅ Dimension {dim_name}: size={dim_info.get('size')}, labels={dim_info.get('labels')}")
    
    return True

def test_scenario_file(filepath, scenario_name):
    """Test a specific scenario file."""
    print(f"\n{'='*60}")
    print(f"Testing {scenario_name}: {filepath}")
    print(f"{'='*60}")
    
    data = load_yaml_file(filepath)
    if not data:
        return False
    
    expected_shape = [3, 3, 2]  # [parcel, year_built_cohort, building_type]
    
    # Test both improvement rate parameters
    basement_valid = validate_multidimensional_structure(
        data, 'basement_height_improvement_rate', expected_shape
    )
    offset_valid = validate_multidimensional_structure(
        data, 'offset_improvement_rate', expected_shape
    )
    
    return basement_valid and offset_valid

def main():
    """Main test function."""
    print("Testing Multidimensional Improvement Rates in Climate Adaptation Model")
    print("="*70)
    
    # Test files
    test_files = [
        ('yaml_models/climate_adaptation_model.yaml', 'Model Structure (Default)'),
        ('yaml_models/climate_adaptation_scenario.yaml', 'Aggressive Adaptation Scenario'),
        ('yaml_models/climate_adaptation_baseline.yaml', 'Baseline Scenario')
    ]
    
    all_tests_passed = True
    
    # First, validate the model structure dimensions
    model_data = load_yaml_file('yaml_models/climate_adaptation_model.yaml')
    if model_data:
        if not validate_dimension_consistency(model_data):
            all_tests_passed = False
    else:
        all_tests_passed = False
    
    # Test each scenario file
    for filepath, scenario_name in test_files:
        if not test_scenario_file(filepath, scenario_name):
            all_tests_passed = False
    
    # Summary
    print(f"\n{'='*70}")
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Multidimensional improvement rates are correctly structured.")
    else:
        print("❌ SOME TESTS FAILED! Please check the issues above.")
    print(f"{'='*70}")
    
    return all_tests_passed

if __name__ == "__main__":
    # Change to examples directory
    os.chdir(os.path.dirname(__file__))
    
    success = main()
    sys.exit(0 if success else 1)
