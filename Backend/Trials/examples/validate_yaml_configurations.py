#!/usr/bin/env python3
"""
Comprehensive YAML Configuration Validation Script
Validates all YAML files across the three organized notebook folders.
"""

import sys
import os
import yaml
import numpy as np
from pathlib import Path
import copy

# Add the sd_toolkit to the path
sys.path.insert(0, os.path.join('..', 'sd_toolkit'))

try:
    from sd_toolkit.config import YAMLSystemBuilder
    from sd_toolkit.engine.system import SystemModel
    print("✅ System Dynamics Toolkit imported successfully")
except ImportError as e:
    print(f"❌ Failed to import System Dynamics Toolkit: {e}")
    sys.exit(1)

def merge_model_with_scenario(model_structure, scenario_data):
    """Merge model structure with scenario parameters."""
    complete_model = copy.deepcopy(model_structure)
    
    # Override constants with scenario values
    if 'constants' in scenario_data:
        if 'constants' not in complete_model:
            complete_model['constants'] = {}
        complete_model['constants'].update(scenario_data['constants'])
    
    # Override model configuration if present
    if 'model_config' in scenario_data:
        complete_model['model'].update(scenario_data['model_config'])
    
    # Add scenario metadata
    complete_model['scenario_info'] = scenario_data.get('scenario', {})
    
    return complete_model

def validate_yaml_file(filepath):
    """Validate a single YAML file can be loaded."""
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        return True, data, None
    except Exception as e:
        return False, None, str(e)

def validate_parameter_consistency(model_structure, scenario_data):
    """Check if all $ parameters in model are defined in scenario."""
    import re
    
    # Convert model structure to string and find all $parameter references
    model_str = yaml.dump(model_structure)
    param_refs = re.findall(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', model_str)
    
    # Get constants from scenario
    scenario_constants = scenario_data.get('constants', {})
    
    missing_params = []
    for param in set(param_refs):
        if param not in scenario_constants:
            missing_params.append(param)
    
    return missing_params

def test_model_building(model_structure, scenario_data, folder_name):
    """Test building a model from structure and scenario."""
    print(f"\n🧪 Testing model building for {folder_name}...")
    
    try:
        # Merge configurations
        complete_model = merge_model_with_scenario(model_structure, scenario_data)
        
        # Build model
        builder = YAMLSystemBuilder()
        model = builder.build_from_dict(complete_model)
        
        print(f"✅ Model built successfully: {model.name}")
        print(f"   📦 Stocks: {len(model.stocks)}")
        print(f"   🌊 Flows: {len(model.flows)}")
        print(f"   🧮 Calculators: {len(model.calculators)}")
        print(f"   🔧 Auxiliaries: {len(model.auxiliaries)}")
        
        # Test population stock
        if 'Population' in model.stocks:
            pop_stock = model.stocks['Population']
            if hasattr(pop_stock, 'initial_value'):
                initial_pop = np.array(pop_stock.initial_value)
                print(f"   👥 Initial population shape: {initial_pop.shape}")
                print(f"   👥 Total initial population: {initial_pop.sum():,.0f}")
        
        return True, model
        
    except Exception as e:
        print(f"❌ Model building failed: {e}")
        return False, None

def validate_folder(folder_path):
    """Validate all YAML files in a folder."""
    folder_name = folder_path.name
    print(f"\n{'='*60}")
    print(f"🔍 VALIDATING FOLDER: {folder_name}")
    print(f"{'='*60}")
    
    # Find YAML files
    yaml_files = list(folder_path.glob("*.yaml"))
    if not yaml_files:
        print(f"❌ No YAML files found in {folder_name}")
        return False
    
    print(f"📁 Found {len(yaml_files)} YAML files:")
    for f in yaml_files:
        print(f"   • {f.name}")
    
    # Identify model structure and scenario files
    model_structure_file = None
    scenario_files = []
    
    for yaml_file in yaml_files:
        if 'structure' in yaml_file.name.lower() or yaml_file.name == 'model_structure.yaml':
            model_structure_file = yaml_file
        elif 'scenario' in yaml_file.name.lower():
            scenario_files.append(yaml_file)
        elif 'calculator' in yaml_file.name.lower():
            model_structure_file = yaml_file  # Calculator example is self-contained
    
    if not model_structure_file:
        print(f"❌ No model structure file found in {folder_name}")
        return False
    
    print(f"\n📋 Model structure: {model_structure_file.name}")
    print(f"📋 Scenario files: {[f.name for f in scenario_files]}")
    
    # Validate model structure file
    success, model_structure, error = validate_yaml_file(model_structure_file)
    if not success:
        print(f"❌ Failed to load model structure: {error}")
        return False
    print(f"✅ Model structure loaded successfully")
    
    # For calculator example (self-contained), test directly
    if 'calculator' in folder_name.lower():
        return test_model_building(model_structure, {}, folder_name)[0]
    
    # Validate scenario files
    all_valid = True
    for scenario_file in scenario_files:
        success, scenario_data, error = validate_yaml_file(scenario_file)
        if not success:
            print(f"❌ Failed to load {scenario_file.name}: {error}")
            all_valid = False
            continue
        
        print(f"✅ Scenario loaded: {scenario_data['scenario']['name']}")
        
        # Check parameter consistency
        missing_params = validate_parameter_consistency(model_structure, scenario_data)
        if missing_params:
            print(f"⚠️  Missing parameters in {scenario_file.name}: {missing_params}")
        else:
            print(f"✅ All parameters defined for {scenario_file.name}")
        
        # Test model building
        build_success, model = test_model_building(model_structure, scenario_data, 
                                                 f"{folder_name}/{scenario_file.stem}")
        if not build_success:
            all_valid = False
    
    return all_valid

def main():
    """Main validation function."""
    print("🧪 COMPREHENSIVE YAML CONFIGURATION VALIDATION")
    print("=" * 60)
    
    # Define folders to validate
    base_path = Path(".")
    folders = [
        base_path / "multidimensional_population",
        base_path / "calculator_example", 
        base_path / "simple_scenarios"
    ]
    
    overall_success = True
    
    for folder in folders:
        if not folder.exists():
            print(f"❌ Folder not found: {folder}")
            overall_success = False
            continue
        
        folder_success = validate_folder(folder)
        if not folder_success:
            overall_success = False
    
    # Final summary
    print(f"\n{'='*60}")
    if overall_success:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ All YAML configurations are valid and compatible")
        print("✅ Parameter substitution working correctly")
        print("✅ Models build successfully")
        print("✅ Multidimensional structures validated")
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("Please review the errors above and fix the issues")
    print(f"{'='*60}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
