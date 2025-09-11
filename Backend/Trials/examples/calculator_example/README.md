# Calculator Component Example

This folder demonstrates the advanced calculator functionality in the system dynamics toolkit for multidimensional population modeling.

## Files

### Model Structure
- **`calculator_model_structure.yaml`** - Model showcasing calculator components with multidimensional arrays
- **`04_multidimensional_yaml_calculator.ipynb`** - Interactive demonstration notebook

## Calculator Features

### Demonstrated Calculators
1. **Net Migration Flow** - Combines economic in-migration and climate out-migration
2. **Natural Growth Flow** - Calculates births minus deaths
3. **Total Population Change** - Combines natural growth and net migration
4. **Population Aggregations** - Urban/rural and age group totals
5. **Dependency Ratio** - Working age vs. dependent population ratios

### Key Capabilities
- **Arithmetic Operations**: Addition, subtraction, multiplication
- **Multidimensional Array Operations**: NumPy-based calculations across dimensions
- **Dependency Resolution**: Automatic linking between calculators and model elements
- **Unit Consistency**: Proper unit handling across calculations

### Model Structure
- **Dimensions**: 3×3×2 (age × income × region)
- **Base Flows**: Birth, death, migration flows
- **Calculator Chain**: Hierarchical calculations building complex metrics
- **Proper Connections**: Calculator outputs connected to population stock

## Usage

1. Open the notebook `04_multidimensional_yaml_calculator.ipynb`
2. Load the calculator model structure
3. Explore calculator definitions and dependencies
4. Run simulations to see calculator effects on population dynamics
5. Visualize multidimensional results

## Validation Status
✅ Calculator expressions validated
✅ Dependency resolution confirmed
✅ Multidimensional consistency verified
✅ Flow connections properly configured
✅ Unit compatibility ensured
