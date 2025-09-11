#!/usr/bin/env python3
"""
Test script to verify the YAML models work with the parameter resolution fix.
"""

import sys
import os
sys.path.insert(0, os.path.join('..', 'sd_toolkit'))

from sd_toolkit.config import YAMLSystemBuilder
import yaml
from pathlib import Path
import copy

def merge_model_with_scenario(model_structure, scenario_data):
    """Merge model structure with scenario parameters."""
    # Deep copy the model structure
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

def test_yaml_models():
    """Test the actual YAML models from the notebook."""
    
    print('🧪 Testing YAML models with parameter resolution fix...')
    
    # Load model structure
    model_structure_path = Path('yaml_models/simple_population_model.yaml')
    with open(model_structure_path, 'r') as file:
        model_structure = yaml.safe_load(file)
    
    print(f'✅ Loaded model structure: {model_structure["model"]["name"]}')
    
    # Load baseline scenario
    baseline_scenario_path = Path('yaml_models/baseline_scenario.yaml')
    with open(baseline_scenario_path, 'r') as file:
        baseline_scenario = yaml.safe_load(file)
    
    print(f'✅ Loaded baseline scenario: {baseline_scenario["scenario"]["name"]}')
    
    # Merge model with scenario
    complete_model = merge_model_with_scenario(model_structure, baseline_scenario)
    
    print(f'✅ Merged model and scenario')
    print(f'   Constants: {list(complete_model["constants"].keys())}')
    
    # Build the model
    try:
        builder = YAMLSystemBuilder()
        model = builder.build_from_dict(complete_model)
        
        print(f'✅ Model built successfully: {model.name}')
        print(f'   📦 Stocks: {len(model.stocks)}')
        print(f'   🌊 Flows: {len(model.flows)}')
        print(f'   🧮 Calculators: {len(model.calculators)}')
        
        # Check flow rates
        print(f'\\n🔍 Flow rates:')
        for flow_id, flow in model.flows.items():
            print(f'   • {flow.name}: {flow.rate}')
        
        # Run a short simulation to test
        print(f'\\n🚀 Running short simulation...')
        results = model.simulate(time_horizon=5, dt=0.25)
        
        initial_pop = results['Population'].iloc[0]
        final_pop = results['Population'].iloc[-1]
        
        print(f'✅ Simulation completed!')
        print(f'   Initial population: {initial_pop:,.0f}')
        print(f'   Final population: {final_pop:,.0f}')
        print(f'   Change: {final_pop - initial_pop:+,.0f}')
        
        if final_pop != initial_pop:
            print('✅ Population is changing - flows are working!')
            return True
        else:
            print('❌ Population not changing - flows may not be working')
            return False
            
    except Exception as e:
        print(f'❌ Error building or running model: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_yaml_models()
    if success:
        print('\\n🎉 YAML models are working with the fix!')
    else:
        print('\\n💥 YAML models still have issues.')
