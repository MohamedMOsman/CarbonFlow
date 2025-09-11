# Simple Scenario Analysis

This folder demonstrates scenario-based modeling with separate model structure and parameter files, following best practices for system dynamics modeling.

## Files

### Model Structure
- **`model_structure.yaml`** - Simple population model with basic flows and calculators
- **`05_simple_model_scenarios.ipynb`** - Scenario comparison notebook

### Scenarios
- **`baseline_scenario.yaml`** - Standard demographic conditions
- **`high_climate_stress_scenario.yaml`** - Climate stress impacts on population dynamics

## Model Architecture

### Separation of Concerns
- **Model Structure**: Defines stocks, flows, calculators, and connections
- **Scenario Files**: Only contain parameter values, no structural definitions
- **Clean Inheritance**: High stress scenario inherits from baseline with selective overrides

### Model Elements
- **Population Stock**: Multidimensional [3×3×2] population array
- **Basic Flows**: Births, deaths, immigration, emigration
- **Calculators**: Net immigration, population growth, total change
- **Dimensions**: Age groups, income levels, urban/rural regions

### Scenario Differences
**Baseline Scenario:**
- Moderate fertility (2.5%) and mortality (1.5%) rates
- Balanced immigration (0.3%) and emigration (0.2%)

**High Climate Stress Scenario:**
- Reduced fertility (2.0%) due to climate impacts
- Increased mortality (1.8%) from climate-related health effects
- Reduced immigration (0.2%) and increased emigration (0.4%)

## Usage

1. Load model structure from `model_structure.yaml`
2. Apply different scenario parameters
3. Compare results between baseline and climate stress conditions
4. Analyze population trajectories under different assumptions

## Best Practices Demonstrated
✅ Clean separation of model structure and parameters
✅ Scenario inheritance and selective overrides
✅ Consistent parameter naming conventions
✅ Realistic climate impact parameter values
✅ Proper multidimensional array handling
