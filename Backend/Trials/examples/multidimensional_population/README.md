# Multidimensional Population Model

This folder contains a comprehensive multidimensional population dynamics model for climate adaptation analysis.

## Files

### Model Structure
- **`model_structure.yaml`** - Complete model definition with multidimensional stocks, flows, and climate-sensitive functions
- **`03_multidimensional_yaml_population.ipynb`** - Demonstration notebook

### Scenarios
- **`baseline_scenario.yaml`** - Baseline climate conditions with moderate parameters
- **`high_climate_stress_scenario.yaml`** - Elevated climate stress scenario with increased impacts

## Model Features

### Dimensions
- **Age Groups**: Young (0-18), Adult (19-65), Elderly (65+)
- **Income Levels**: Low, Medium, High income
- **Regions**: Urban, Rural

### Key Components
- **Population Stock**: Multidimensional [3×3×2] array
- **Climate-Sensitive Flows**: Births, deaths, migration with climate impacts
- **Dynamic Auxiliaries**: Climate stress index, economic conditions
- **Advanced Functions**: Temperature-dependent rates, climate migration

### Parameters
All parameters are properly defined in scenario files with realistic values for climate adaptation modeling:
- Demographic rates with climate sensitivity
- Migration parameters responding to climate stress
- Economic impact factors
- Regional carrying capacity and area specifications

## Usage

1. Load the model structure from `model_structure.yaml`
2. Apply scenario parameters from either scenario file
3. Run simulation using the notebook
4. Analyze multidimensional population dynamics under different climate conditions

## Validation Status
✅ All parameter references validated
✅ Multidimensional consistency verified
✅ Climate adaptation parameters properly calibrated
✅ Cross-file compatibility confirmed
