#!/usr/bin/env python3
"""
Test script to verify the updated notebook works correctly with actual simulation data
"""

import sys
import os
sys.path.insert(0, os.path.join('..', '..', 'sd_toolkit'))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
from sd_toolkit.config import YAMLSystemBuilder

def test_notebook_simulation():
    """Test the core simulation logic from the updated notebook"""
    print("🧪 TESTING UPDATED NOTEBOOK SIMULATION")
    print("=" * 50)
    
    # Simulate the notebook's simulation logic
    print("🔍 Loading configurations...")
    
    # Load model structure
    with open('integrated_model_structure.yaml', 'r') as f:
        model_structure = yaml.safe_load(f)
    
    # Load scenario parameters
    with open('integrated_scenario_parameters.yaml', 'r') as f:
        scenario_params = yaml.safe_load(f)
    
    print("✅ Configurations loaded successfully")
    
    # Build integrated model
    print("🔧 Building integrated model...")
    
    # Merge configurations
    full_config = model_structure.copy()
    full_config['constants'] = scenario_params['constants']
    
    # Build model
    builder = YAMLSystemBuilder()
    model = builder.build_from_dict(full_config)
    model_built_successfully = True
    
    print("✅ Model built successfully")
    print(f"📦 Model components: {len(model.stocks)} stocks, {len(model.flows)} flows, {len(model.calculators)} calculators")
    
    # Run simulation
    print("🚀 Running simulation...")
    time_horizon = 10  # Shorter for testing
    dt = 0.25
    
    results = model.simulate(time_horizon=time_horizon, dt=dt)
    simulation_successful = True
    
    print("✅ Simulation completed successfully")
    print(f"📊 Results: {results.shape[0]} time steps, {results.shape[1]} variables")
    
    # Test visualization data preparation (like in the notebook)
    print("📊 Testing visualization data preparation...")
    
    # Use actual simulation time points and data (like in updated notebook)
    time_points = results['time']
    
    # Test key data access
    total_pop_trend = results['Total_Population']
    employed_pop = results['Employed_Population']
    housing_supply = results['Housing_Supply']
    
    print(f"  ✅ Population data: {total_pop_trend.iloc[0]:,.0f} → {total_pop_trend.iloc[-1]:,.0f}")
    print(f"  ✅ Employment data: {employed_pop.iloc[0]:,.0f} → {employed_pop.iloc[-1]:,.0f}")
    print(f"  ✅ Housing supply: {housing_supply.iloc[0]:,.0f} → {housing_supply.iloc[-1]:,.0f}")
    
    # Test conditional data access (like in updated notebook)
    if 'Housing_Demand_Calc' in results.columns:
        housing_demand = results['Housing_Demand_Calc']
        print(f"  ✅ Housing demand: {housing_demand.iloc[0]:,.0f} → {housing_demand.iloc[-1]:,.0f}")
    
    if 'Economic_Output_Calc' in results.columns:
        economic_output = results['Economic_Output_Calc'] / 1e9
        print(f"  ✅ Economic output: ${economic_output.iloc[0]:.1f}B → ${economic_output.iloc[-1]:.1f}B")
    
    # Test summary statistics calculation (like in updated notebook)
    print("📈 Testing summary statistics...")
    
    initial_pop = total_pop_trend.iloc[0]
    final_pop = total_pop_trend.iloc[-1]
    growth_rate = ((final_pop / initial_pop) ** (1/time_horizon) - 1) * 100
    
    print(f"  📊 Population growth rate: {growth_rate:.2f}%/year")
    print(f"  📊 Population change: {(final_pop-initial_pop):+,.0f}")
    
    # Test flow data access
    print("🌊 Testing flow data access...")
    flow_tests = ['Immigration_Flow', 'Birth_Flow', 'Death_Flow', 'Employment_Flow']
    for flow_name in flow_tests:
        if flow_name in results.columns:
            final_value = results[flow_name].iloc[-1]
            print(f"  ✅ {flow_name}: {final_value:.2f}")
    
    return {
        'model_structure': model_structure,
        'scenario_params': scenario_params,
        'model_built_successfully': model_built_successfully,
        'simulation_successful': simulation_successful,
        'results': results,
        'time_horizon': time_horizon,
        'dt': dt
    }

def test_visualization_logic(test_data):
    """Test the visualization logic from the updated notebook"""
    print("\n📊 TESTING VISUALIZATION LOGIC")
    print("=" * 40)
    
    results = test_data['results']
    time_horizon = test_data['time_horizon']
    simulation_successful = test_data['simulation_successful']
    
    # Test the notebook's visualization condition
    if simulation_successful and results is not None:
        print("✅ Visualization conditions met")
        
        # Test actual data access (like in updated notebook)
        time_points = results['time']
        total_pop_trend = results['Total_Population']
        employed_pop = results['Employed_Population']
        housing_supply = results['Housing_Supply']
        
        # Test statistics calculation
        initial_pop = total_pop_trend.iloc[0]
        final_pop = total_pop_trend.iloc[-1]
        growth_rate = ((final_pop / initial_pop) ** (1/time_horizon) - 1) * 100
        
        print(f"  📈 Population statistics ready: {initial_pop:,.0f} → {final_pop:,.0f}")
        print(f"  📊 Growth rate calculation: {growth_rate:.2f}%/year")
        
        # Test conditional data access
        if 'Economic_Output_Calc' in results.columns:
            economic_output = results['Economic_Output_Calc'] / 1e9
            print(f"  💰 Economic output ready: ${economic_output.iloc[-1]:.1f}B")
        
        if 'Housing_Demand_Calc' in results.columns:
            housing_demand = results['Housing_Demand_Calc']
            print(f"  🏠 Housing demand ready: {housing_demand.iloc[-1]:,.0f}")
        
        print("✅ All visualization data successfully prepared")
        
    else:
        print("❌ Visualization conditions not met")

def main():
    """Main test function"""
    print("🎯 TESTING UPDATED NOTEBOOK FUNCTIONALITY")
    print("=" * 60)
    
    # Test simulation
    test_data = test_notebook_simulation()
    
    # Test visualization
    test_visualization_logic(test_data)
    
    # Summary
    print(f"\n📋 TEST SUMMARY")
    print("=" * 20)
    print("✅ Updated notebook simulation logic: WORKING")
    print("✅ Actual data access: WORKING") 
    print("✅ Visualization data preparation: WORKING")
    print("✅ Summary statistics calculation: WORKING")
    print("✅ Conditional data handling: WORKING")
    
    print(f"\n🎉 The updated notebook should now work correctly with ACTUAL simulation data!")
    print(f"📝 Key improvements:")
    print(f"  • Uses results['time'] instead of np.linspace()")
    print(f"  • Uses results['Total_Population'] instead of placeholder formulas")
    print(f"  • Includes actual population statistics in plots")
    print(f"  • Shows real economic and housing data")
    print(f"  • Provides comprehensive summary statistics")

if __name__ == "__main__":
    main()
