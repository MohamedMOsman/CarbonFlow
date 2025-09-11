#!/usr/bin/env python3
"""
Test script to verify the parameter resolution fix.
"""

import sys
import os
sys.path.insert(0, os.path.join('..', 'sd_toolkit'))

from sd_toolkit.config import YAMLSystemBuilder

def test_parameter_resolution():
    """Test that $parameter references are resolved correctly in flow rates."""
    
    # Test configuration with parameter reference
    test_config = {
        'model': {
            'name': 'Test Model',
            'description': 'Test parameter resolution',
            'time_horizon': 10,
            'dt': 1.0,
            'time_units': 'year'
        },
        'constants': {
            'test_rate': 0.025
        },
        'elements': {
            'stocks': [
                {
                    'name': 'Population',
                    'initial_value': 1000,
                    'units': 'people',
                    'description': 'Test population'
                }
            ],
            'flows': [
                {
                    'name': 'Growth',
                    'rate': '$test_rate',  # Using constant reference
                    'units': 'people/year',
                    'description': 'Test growth flow'
                }
            ]
        },
        'connections': [
            {
                'from': 'Growth',
                'to': 'Population',
                'type': 'inflow'
            }
        ]
    }

    print('🧪 Testing parameter resolution fix...')
    
    try:
        builder = YAMLSystemBuilder()
        model = builder.build_from_dict(test_config)
        
        # Check if the flow rate was resolved correctly
        growth_flow = None
        for flow_id, flow in model.flows.items():
            if flow.name == 'Growth':
                growth_flow = flow
                break
        
        if growth_flow:
            print(f'✅ Growth flow rate: {growth_flow.rate}')
            if growth_flow.rate == 0.025:
                print('✅ Parameter resolution working correctly!')
                return True
            else:
                print(f'❌ Expected 0.025, got {growth_flow.rate}')
                return False
        else:
            print('❌ Growth flow not found')
            return False
            
    except Exception as e:
        print(f'❌ Error during test: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_parameter_resolution()
    if success:
        print('\n🎉 Parameter resolution fix is working!')
    else:
        print('\n💥 Parameter resolution fix needs more work.')
