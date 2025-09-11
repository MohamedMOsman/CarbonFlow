# Multidimensional Improvement Rates in Climate Adaptation Model

## Overview

The climate adaptation model has been updated to use **multidimensional improvement rates** for both `basement_height_improvement_rate` and `offset_improvement_rate` parameters. These rates now vary across three dimensions:

- **Parcel** (3 levels): parcel_1001, parcel_1002, parcel_1003
- **Year Built Cohort** (3 levels): pre_war, post_war, modern  
- **Building Type** (2 levels): residential, commercial

This creates a 3×3×2 = 18 different rate values for each improvement type, enabling more realistic and detailed modeling of climate adaptation measures.

## Structure

### Array Format
```yaml
basement_height_improvement_rate:
  # parcel_1001
  - [
      [0.015, 0.012],  # pre_war: [residential, commercial]
      [0.020, 0.018],  # post_war
      [0.025, 0.022]   # modern
    ]
  # parcel_1002  
  - [
      [0.018, 0.015],  # pre_war
      [0.022, 0.020],  # post_war
      [0.028, 0.025]   # modern
    ]
  # parcel_1003
  - [
      [0.020, 0.018],  # pre_war
      [0.025, 0.022],  # post_war
      [0.030, 0.028]   # modern
    ]
```

### Accessing Values
To access a specific rate value:
```python
# Load rates from YAML
basement_rates = np.array(yaml_data['constants']['basement_height_improvement_rate'])

# Access rate for parcel_1002, post_war, commercial
rate = basement_rates[1, 1, 1]  # [parcel_idx, cohort_idx, building_idx]
```

## Updated Files

### Model Structure Files
- **`climate_adaptation_model.yaml`**: Updated with default multidimensional rates
- **`climate_adaptation_scenario.yaml`**: Enhanced rates for aggressive adaptation scenario
- **`climate_adaptation_baseline.yaml`**: Minimal rates for baseline/business-as-usual scenario

### Validation and Testing
- **`test_multidimensional_rates.py`**: Comprehensive validation script
- **`multidimensional_rates_example.py`**: Demonstration script showing usage patterns
- **`multidimensional_rates_demo.ipynb`**: Interactive notebook with visualizations

## Key Benefits

### 1. Realistic Modeling
- **Age Effects**: Newer buildings (modern cohort) can be improved more easily than older ones
- **Spatial Variation**: Different parcels have different improvement potential based on resources and conditions
- **Building Type Differences**: Residential and commercial buildings have different improvement characteristics

### 2. Policy Analysis
- **Targeted Investment**: Identify which combinations of parcel/cohort/building type offer best returns
- **Scenario Planning**: Compare different policy commitment levels (baseline vs aggressive)
- **Resource Allocation**: Optimize adaptation investments across different building categories

### 3. Enhanced Realism
- **Heterogeneous Rates**: Reflects real-world variation in improvement potential
- **Dimensional Consistency**: Maintains consistency with other multidimensional model elements
- **Scalable Structure**: Easy to extend to additional dimensions if needed

## Rate Patterns

### Observed Trends
1. **Cohort Effects**: modern > post_war > pre_war (newer buildings improve faster)
2. **Parcel Effects**: parcel_1003 > parcel_1002 > parcel_1001 (higher-numbered parcels have better rates)
3. **Building Type**: residential ≥ commercial (slight preference for residential improvements)
4. **Scenario Scaling**: aggressive ≈ 4.5× baseline, default ≈ 2.6× baseline

### Example Rate Ranges (m/year)
| Scenario   | Min Rate | Max Rate | Mean Rate | Improvement Factor |
|------------|----------|----------|-----------|-------------------|
| Baseline   | 0.006    | 0.024    | 0.014     | 1.0× (reference)  |
| Default    | 0.020    | 0.055    | 0.037     | 2.6×              |
| Aggressive | 0.037    | 0.095    | 0.064     | 4.5×              |

## Usage Examples

### Basic Access
```python
import yaml
import numpy as np

# Load scenario
with open('yaml_models/climate_adaptation_model.yaml', 'r') as f:
    data = yaml.safe_load(f)

basement_rates = np.array(data['constants']['basement_height_improvement_rate'])
offset_rates = np.array(data['constants']['offset_improvement_rate'])

# Get rate for specific combination
parcel_idx = 1      # parcel_1002
cohort_idx = 2      # modern
building_idx = 0    # residential

rate = basement_rates[parcel_idx, cohort_idx, building_idx]
print(f"Rate: {rate:.3f} m/year")
```

### Scenario Comparison
```python
scenarios = ['baseline', 'default', 'aggressive']
for scenario in scenarios:
    rates = load_rates(f'climate_adaptation_{scenario}.yaml')
    print(f"{scenario}: {rates.mean():.3f} ± {rates.std():.3f} m/year")
```

### Projection Calculations
```python
# Calculate 20-year improvement potential
years = 20
total_improvement = (basement_rates + offset_rates) * years
print(f"Max improvement potential: {total_improvement.max():.2f} meters")
```

## Validation

Run the validation script to verify the multidimensional structure:

```bash
cd examples
python test_multidimensional_rates.py
```

Expected output: ✅ ALL TESTS PASSED!

## Integration with System Dynamics

The multidimensional rates integrate seamlessly with the existing system dynamics framework:

1. **Flow Rates**: The flows `Basement_Height_Improvement` and `Offset_Improvement` use these multidimensional rates
2. **Spatial Dimensions**: Both flows have `spatial_dims: ["parcel", "year_built_cohort", "building_type"]`
3. **Parameter Substitution**: Rates are referenced using `$basement_height_improvement_rate` and `$offset_improvement_rate`
4. **Validation**: Updated validation rules check multidimensional parameter bounds

This enhancement makes the climate adaptation model significantly more realistic and useful for policy analysis while maintaining full compatibility with the existing system dynamics toolkit.
