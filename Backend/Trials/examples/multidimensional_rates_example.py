#!/usr/bin/env python3
"""
Example script demonstrating how to work with multidimensional improvement rates
in the climate adaptation model.

This script shows how to:
1. Load multidimensional rates from YAML files
2. Access specific rate values by dimension
3. Perform calculations with multidimensional rates
4. Compare rates across scenarios
"""

import yaml
import numpy as np
import pandas as pd

def load_rates_from_yaml(filepath):
    """Load improvement rates from a YAML scenario file."""
    with open(filepath, 'r') as file:
        data = yaml.safe_load(file)
    
    constants = data['constants']
    basement_rates = np.array(constants['basement_height_improvement_rate'])
    offset_rates = np.array(constants['offset_improvement_rate'])
    
    return basement_rates, offset_rates

def demonstrate_rate_access():
    """Demonstrate how to access specific rate values."""
    print("🔍 Accessing Specific Rate Values")
    print("=" * 40)
    
    # Load rates from default model
    basement_rates, offset_rates = load_rates_from_yaml('yaml_models/climate_adaptation_model.yaml')
    
    # Define dimension indices
    parcel_indices = {'parcel_1001': 0, 'parcel_1002': 1, 'parcel_1003': 2}
    cohort_indices = {'pre_war': 0, 'post_war': 1, 'modern': 2}
    building_indices = {'residential': 0, 'commercial': 1}
    
    # Example: Get rate for parcel_1002, post_war, commercial building
    parcel_idx = parcel_indices['parcel_1002']
    cohort_idx = cohort_indices['post_war']
    building_idx = building_indices['commercial']
    
    basement_rate = basement_rates[parcel_idx, cohort_idx, building_idx]
    offset_rate = offset_rates[parcel_idx, cohort_idx, building_idx]
    
    print(f"Rates for parcel_1002, post_war, commercial building:")
    print(f"  Basement height improvement: {basement_rate:.3f} m/year")
    print(f"  Offset improvement: {offset_rate:.3f} m/year")
    print(f"  Combined improvement: {basement_rate + offset_rate:.3f} m/year")
    
    return basement_rates, offset_rates

def calculate_improvement_projections(basement_rates, offset_rates, years=20):
    """Calculate projected improvements over time."""
    print(f"\n📊 Projected Improvements Over {years} Years")
    print("=" * 45)
    
    # Calculate total improvements
    basement_improvement = basement_rates * years
    offset_improvement = offset_rates * years
    total_improvement = basement_improvement + offset_improvement
    
    # Create summary statistics
    stats = {
        'Basement Height': {
            'min': basement_improvement.min(),
            'max': basement_improvement.max(),
            'mean': basement_improvement.mean(),
            'std': basement_improvement.std()
        },
        'Offset Height': {
            'min': offset_improvement.min(),
            'max': offset_improvement.max(),
            'mean': offset_improvement.mean(),
            'std': offset_improvement.std()
        },
        'Total Protection': {
            'min': total_improvement.min(),
            'max': total_improvement.max(),
            'mean': total_improvement.mean(),
            'std': total_improvement.std()
        }
    }
    
    # Print statistics
    for metric, values in stats.items():
        print(f"\n{metric}:")
        print(f"  Range: {values['min']:.3f} - {values['max']:.3f} meters")
        print(f"  Average: {values['mean']:.3f} ± {values['std']:.3f} meters")
    
    return total_improvement

def compare_scenarios():
    """Compare improvement rates across different scenarios."""
    print(f"\n🔄 Scenario Comparison")
    print("=" * 25)
    
    scenarios = {
        'Baseline': 'yaml_models/climate_adaptation_baseline.yaml',
        'Default': 'yaml_models/climate_adaptation_model.yaml',
        'Aggressive': 'yaml_models/climate_adaptation_scenario.yaml'
    }
    
    comparison_data = []
    
    for scenario_name, filepath in scenarios.items():
        basement_rates, offset_rates = load_rates_from_yaml(filepath)
        total_rates = basement_rates + offset_rates
        
        comparison_data.append({
            'Scenario': scenario_name,
            'Min Rate': total_rates.min(),
            'Max Rate': total_rates.max(),
            'Mean Rate': total_rates.mean(),
            'Range': total_rates.max() - total_rates.min()
        })
    
    # Create comparison DataFrame
    df = pd.DataFrame(comparison_data)
    df = df.round(4)
    
    print("\nTotal Improvement Rates (basement + offset, m/year):")
    print(df.to_string(index=False))
    
    # Calculate improvement factors
    baseline_mean = df[df['Scenario'] == 'Baseline']['Mean Rate'].iloc[0]
    print(f"\nImprovement factors relative to baseline:")
    for _, row in df.iterrows():
        if row['Scenario'] != 'Baseline':
            factor = row['Mean Rate'] / baseline_mean
            print(f"  {row['Scenario']}: {factor:.1f}x faster than baseline")

def analyze_dimensional_patterns():
    """Analyze patterns across different dimensions."""
    print(f"\n📈 Dimensional Pattern Analysis")
    print("=" * 35)
    
    # Load default rates
    basement_rates, offset_rates = load_rates_from_yaml('yaml_models/climate_adaptation_model.yaml')
    total_rates = basement_rates + offset_rates
    
    # Define labels
    parcels = ['parcel_1001', 'parcel_1002', 'parcel_1003']
    cohorts = ['pre_war', 'post_war', 'modern']
    building_types = ['residential', 'commercial']
    
    # Analyze by parcel
    print("\nAverage rates by parcel:")
    for i, parcel in enumerate(parcels):
        avg_rate = total_rates[i, :, :].mean()
        print(f"  {parcel}: {avg_rate:.3f} m/year")
    
    # Analyze by cohort
    print("\nAverage rates by construction cohort:")
    for i, cohort in enumerate(cohorts):
        avg_rate = total_rates[:, i, :].mean()
        print(f"  {cohort}: {avg_rate:.3f} m/year")
    
    # Analyze by building type
    print("\nAverage rates by building type:")
    for i, building_type in enumerate(building_types):
        avg_rate = total_rates[:, :, i].mean()
        print(f"  {building_type}: {avg_rate:.3f} m/year")
    
    # Find best and worst combinations
    max_idx = np.unravel_index(total_rates.argmax(), total_rates.shape)
    min_idx = np.unravel_index(total_rates.argmin(), total_rates.shape)
    
    print(f"\nBest performing combination:")
    print(f"  {parcels[max_idx[0]]}, {cohorts[max_idx[1]]}, {building_types[max_idx[2]]}")
    print(f"  Rate: {total_rates[max_idx]:.3f} m/year")
    
    print(f"\nWorst performing combination:")
    print(f"  {parcels[min_idx[0]]}, {cohorts[min_idx[1]]}, {building_types[min_idx[2]]}")
    print(f"  Rate: {total_rates[min_idx]:.3f} m/year")

def main():
    """Main demonstration function."""
    print("🏗️  Multidimensional Climate Adaptation Rates Demo")
    print("=" * 55)
    print("This script demonstrates working with multidimensional")
    print("improvement rates for basement height and structure offset.")
    print()
    
    # Change to examples directory if needed
    import os
    if not os.path.exists('yaml_models'):
        os.chdir('examples')
    
    try:
        # Demonstrate rate access
        basement_rates, offset_rates = demonstrate_rate_access()
        
        # Calculate projections
        calculate_improvement_projections(basement_rates, offset_rates)
        
        # Compare scenarios
        compare_scenarios()
        
        # Analyze patterns
        analyze_dimensional_patterns()
        
        print(f"\n✅ Demo completed successfully!")
        print("The multidimensional rate structure enables detailed")
        print("modeling of climate adaptation measures with realistic")
        print("variation across parcels, building ages, and types.")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find required YAML files.")
        print(f"Make sure you're running this script from the examples directory.")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
