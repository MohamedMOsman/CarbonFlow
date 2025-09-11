# Calculator Component Examples

This directory contains examples demonstrating the new Calculator component in the System Dynamics Toolkit.

## Overview

The Calculator component allows you to create derived values by combining other model elements (stocks, flows, constants, other calculators) using simple arithmetic expressions. This eliminates the need to write custom Python functions for basic mathematical operations.

## Files in this Directory

### YAML Configuration Examples

1. **`yaml_models/calculator_example.yaml`**
   - Basic calculator usage with simple population model
   - Demonstrates net flow calculations (immigration - emigration)
   - Shows stock combinations (urban + rural population)
   - Includes all required calculator examples from the specification

2. **`yaml_models/multidimensional_calculator_example.yaml`**
   - Advanced multidimensional calculator operations
   - Climate adaptation population modeling
   - Array aggregation across dimensions
   - Complex demographic calculations

### Test and Demo Scripts

3. **`test_calculator_functionality.py`**
   - Comprehensive test suite for calculator functionality
   - Unit tests for Calculator class methods
   - Integration tests with YAML configuration
   - Multidimensional array operation tests
   - Run with: `python test_calculator_functionality.py`

## Quick Start

### 1. Basic Calculator Usage

```python
from sd_toolkit.engine.elements import Stock, Flow, Calculator

# Create model elements
population = Stock("Population", initial_value=1000, units="people")
births = Flow("Birth_Flow", rate=25, units="people/year")
deaths = Flow("Death_Flow", rate=15, units="people/year")

# Create calculator for net growth
growth = Calculator(
    name="Growth_Flow",
    expression="Birth_Flow - Death_Flow",
    units="people/year"
)

# Add dependencies
growth.add_dependency(births)
growth.add_dependency(deaths)

# Calculate result
result = growth.calculate(time=0.0, dt=0.25)
print(f"Net growth: {result} people/year")  # Output: 10 people/year
```

### 2. YAML Configuration

```yaml
elements:
  stocks:
    - name: "Population"
      initial_value: 1000
      units: "people"
  
  flows:
    - name: "Birth_Flow"
      rate: 0.025
      units: "people/year"
    
    - name: "Death_Flow"
      rate: 0.015
      units: "people/year"
  
  calculators:
    - name: "Growth_Flow"
      expression: "Birth_Flow - Death_Flow"
      units: "people/year"
      description: "Net population growth"
      dependencies: ["Birth_Flow", "Death_Flow"]
```

### 3. Load and Run YAML Model

```python
from sd_toolkit.config import YAMLSystemBuilder

# Load model from YAML
builder = YAMLSystemBuilder()
model = builder.build_from_file("yaml_models/calculator_example.yaml")

# Access calculators
for calc_id, calc in model.calculators.items():
    result = calc.calculate(0.0, 0.25)
    print(f"{calc.name}: {result} {calc.units}")
```

## Specific Examples from Requirements

The examples implement all the specific calculator types requested:

### 1. Net Immigration Flow
```yaml
calculators:
  - name: "Net_Immigration_Flow"
    expression: "Immigration_Flow - Emigration_Flow"
    units: "people/year"
    description: "Net immigration = immigration - emigration"
```

### 2. Growth Flow
```yaml
calculators:
  - name: "Growth_Flow"
    expression: "Birth_Flow - Death_Flow"
    units: "people/year"
    description: "Natural growth = births - deaths"
```

### 3. Population Calculation
```yaml
calculators:
  - name: "Population_Calc"
    expression: "Urban_Population + Rural_Population"
    units: "people"
    description: "Total population = urban + rural populations"
```

## Multidimensional Examples

### Population Aggregation
```yaml
calculators:
  - name: "Urban_Population_Total"
    expression: "np.sum(Population[:, :, 0])"  # Sum urban across age/income
    units: "people"
    dependencies: ["Population"]
  
  - name: "Dependency_Ratio"
    expression: "(Young_Population + Elderly_Population) / Working_Age_Population"
    units: "dimensionless"
    dependencies: ["Young_Population", "Elderly_Population", "Working_Age_Population"]
```

## Running the Examples

### Test All Calculator Functionality
```bash
cd examples
python test_calculator_functionality.py
```

Expected output:
```
🚀 Calculator Functionality Test Suite
============================================================

🔬 Running Calculator Unit Tests
==================================================
✅ Expression parsing passed
✅ Parameter handling passed
✅ Simple calculation passed: 14
✅ Parameter calculation passed: 22.0
✅ Error handling passed

🧮 Testing Basic Calculator Functionality
==================================================
✅ Basic calculator tests passed!

🔧 Testing YAML Calculator Integration
==================================================
✅ Model loaded: Population Model with Calculators
🧮 Created calculators: ['Net_Immigration_Flow', 'Growth_Flow', 'Population_Calc', ...]

📐 Testing Multidimensional Calculators
==================================================
✅ Multidimensional calculator tests passed!

🎉 All calculator tests passed!
```

### Load YAML Models Interactively

```python
# In Python or Jupyter notebook
import sys
sys.path.append('../sd_toolkit')

from sd_toolkit.config import YAMLSystemBuilder

# Load basic example
builder = YAMLSystemBuilder()
model = builder.build_from_file('yaml_models/calculator_example.yaml')

print(f"Model: {model.name}")
print(f"Calculators: {len(model.calculators)}")

# Test calculator
calc = list(model.calculators.values())[0]
result = calc.calculate(0.0, 0.25)
print(f"{calc.name}: {result}")
```

## Key Features Demonstrated

1. **Basic Arithmetic**: Addition, subtraction, multiplication, division
2. **Multidimensional Support**: Array operations with numpy functions
3. **Unit Awareness**: Proper unit handling and consistency checking
4. **Dependency Resolution**: Automatic and explicit dependency management
5. **YAML Integration**: Seamless configuration file support
6. **Error Handling**: Graceful handling of undefined variables and errors

## Integration with Existing Toolkit

The Calculator component integrates seamlessly with existing toolkit features:

- **Stocks and Flows**: Can reference and be referenced by other model elements
- **BPTK Converter**: Works with existing converter capabilities
- **Multidimensional Data**: Supports same spatial dimension system
- **Unit System**: Maintains unit awareness throughout calculations
- **Simulation Engine**: Evaluated in proper dependency order
- **Visualization**: Calculator results can be plotted like other elements

## Next Steps

1. **Explore the YAML files** to understand configuration syntax
2. **Run the test script** to see all functionality in action
3. **Modify examples** to experiment with different expressions
4. **Create your own models** using calculators for your specific use cases
5. **Check the documentation** in `docs/Calculator_Component_Guide.md` for detailed reference

## Support

For questions or issues with the Calculator component:
1. Check the comprehensive documentation in `docs/Calculator_Component_Guide.md`
2. Review the test cases in `test_calculator_functionality.py`
3. Examine the YAML examples for configuration patterns
4. Look at the Calculator class implementation in `sd_toolkit/engine/elements.py`
