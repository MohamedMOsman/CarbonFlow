# Population-Economy-Housing Simulation

A comprehensive multi-module system dynamics simulation modeling the interconnected impacts of population dynamics, economic factors, and housing market changes. This example demonstrates advanced multidimensional modeling capabilities with proper module separation, dependency management, and scenario analysis.

## 🏗️ System Architecture

### Three Interconnected Modules

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Population    │───▶│    Economic     │───▶│    Housing      │
│   Dynamics      │    │   Indicators    │    │    Market       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    Economic Attraction Factor
```

### 1. **Population Dynamics Module** 👥
- **Core Variables**: Immigration, emigration, births, deaths
- **Dimensions**: Age group (5), Gender (2), Income bracket (3)
- **Key Stocks**: `Total_Population[age_group, gender]`
- **Outputs**: Population changes that drive economic and housing demand

### 2. **Economic Indicators Module** 💼
- **Core Variables**: Employment rates, income levels, economic output
- **Key Stocks**: `Employed_Population[age_group, gender]`, `Average_Income[age_group, income_bracket]`
- **Dependencies**: Population size drives employment demand
- **Outputs**: Economic conditions that influence housing construction and immigration attraction

### 3. **Housing Market Module** 🏠
- **Core Variables**: Housing supply, demand, pricing, affordability
- **Dimensions**: Housing type (2), Price bracket (2)
- **Key Stocks**: `Housing_Supply[housing_type, price_bracket]`, `Average_Housing_Price[housing_type, price_bracket]`
- **Dependencies**: Population drives demand, income affects affordability

## 🔗 Model Connections

### Cross-Module Dependencies

**Population → Economic:**
- Total population drives employment flows
- Population size affects employment rate calculations

**Population → Housing:**
- Total population influences housing demand calculations
- Demographic changes affect housing type preferences

**Economic → Housing:**
- Average income affects housing affordability indices
- Economic output influences construction conditions

**Economic → Population (Feedback):**
- Economic conditions create attraction factor for immigration
- Employment opportunities influence migration patterns

## 📁 Directory Structure

```
population-economy-housing-simulation/
├── population-dynamics/
│   ├── model_structure.yaml          # Population model definition
│   ├── scenario_parameters.yaml      # Population-specific parameters
│   └── test_population_dynamics.ipynb # Individual module testing
├── economic-indicators/
│   ├── model_structure.yaml          # Economic model definition
│   ├── scenario_parameters.yaml      # Economic parameters
│   └── test_economic_indicators.ipynb # Individual module testing
├── housing-market/
│   ├── model_structure.yaml          # Housing model definition
│   ├── scenario_parameters.yaml      # Housing parameters
│   └── test_housing_market.ipynb     # Individual module testing
├── integrated_model_structure.yaml   # Combined model definition
├── integrated_scenario_parameters.yaml # Unified parameters
├── run_full_simulation.ipynb         # Main execution notebook
├── demonstration_analysis.ipynb      # Advanced analysis & scenarios
├── VALIDATION_REPORT.md              # Technical validation details
└── README.md                         # This file
```

## 🚀 Getting Started

### Prerequisites

```python
# Required packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
from pathlib import Path

# System Dynamics Toolkit (from repository root)
sys.path.insert(0, os.path.join('..', '..', 'sd_toolkit'))
from sd_toolkit.config import YAMLSystemBuilder
from sd_toolkit.engine.system import SystemModel
```

### Quick Start

1. **Test Individual Modules** (Optional but recommended):
   ```bash
   # Navigate to each module directory and run test notebooks
   cd population-dynamics/
   jupyter notebook test_population_dynamics.ipynb
   
   cd ../economic-indicators/
   jupyter notebook test_economic_indicators.ipynb
   
   cd ../housing-market/
   jupyter notebook test_housing_market.ipynb
   ```

2. **Run Integrated Simulation**:
   ```bash
   jupyter notebook run_full_simulation.ipynb
   ```

3. **Perform Advanced Analysis**:
   ```bash
   jupyter notebook demonstration_analysis.ipynb
   ```

## 📊 Key Features

### Multidimensional Modeling
- **Population**: 5 age groups × 2 genders × 3 income brackets = 30 demographic segments
- **Economic**: Employment and income tracking across age and gender
- **Housing**: 2 housing types × 2 price brackets = 4 market segments

### Advanced Calculations
- **Calculator Components**: Generic arithmetic operations on flows/stocks
- **Cross-Module Dependencies**: Automatic dependency resolution
- **Feedback Loops**: Economic attraction affects immigration, population drives housing demand

### Scenario Analysis
- **Baseline Scenario**: Standard conditions with moderate immigration
- **High Immigration**: 50% increased immigration rates
- **Economic Boom**: Enhanced income growth and economic expansion
- **Housing Policy**: Increased construction rates and affordable housing focus

## 🔧 Configuration

### Model Structure Files
- Each module has separate `model_structure.yaml` defining stocks, flows, calculators
- Integrated model combines all modules with cross-dependencies
- Shared dimensions ensure compatibility across modules

### Parameter Files
- Module-specific `scenario_parameters.yaml` for individual testing
- Unified `integrated_scenario_parameters.yaml` for full simulation
- Parameter substitution using `$parameter_name` syntax

### Example Parameter Configuration
```yaml
# Immigration parameters
base_immigration_rate: 0.02      # 2% annual immigration rate
immigration_multiplier: 1.0      # Baseline multiplier
economic_growth_rate: 0.03       # 3% economic growth

# Housing parameters
construction_rate: 0.05          # 5% annual construction rate
price_elasticity: 0.1           # Price adjustment sensitivity
demand_per_person: 0.4          # Housing units per person
```

## 📈 Analysis Capabilities

### Visualization Features
- **Population Pyramids**: Age-gender distribution over time
- **Employment Heatmaps**: Employment rates across demographics
- **Housing Price Trends**: Market price evolution by segment
- **Affordability Analysis**: Income-to-price ratios
- **Cross-Module Impact Charts**: Dependency relationship visualization

### Scenario Comparison
- Side-by-side scenario results
- Parameter sensitivity analysis
- Policy intervention assessment
- Economic impact evaluation

## 🔍 Technical Details

### System Dynamics Elements

**Stocks (State Variables):**
- `Total_Population[age_group, gender]`
- `Employed_Population[age_group, gender]`
- `Average_Income[age_group, income_bracket]`
- `Housing_Supply[housing_type, price_bracket]`
- `Average_Housing_Price[housing_type, price_bracket]`

**Flows (Rate Variables):**
- Immigration, Emigration, Birth, Death flows
- Employment and Income flows
- Construction and Price Adjustment flows

**Calculators (Derived Variables):**
- Net Migration = Immigration - Emigration
- Housing Demand based on population and income
- Affordability Index = Income / Housing Price
- Economic Output aggregation

**Auxiliaries (Helper Variables):**
- Economic Attraction Factor
- Housing Demand Pressure
- Employment Rate calculations

### Validation Features
- Dimension consistency checking
- Parameter bounds validation
- Cross-module constraint verification
- Model integration testing

## 🎯 Use Cases

### Urban Planning
- Population growth impact on housing demand
- Infrastructure capacity planning
- Economic development scenario analysis

### Policy Analysis
- Immigration policy impact assessment
- Housing affordability interventions
- Economic stimulus effect modeling

### Research Applications
- Urban system dynamics research
- Multi-dimensional demographic modeling
- Economic-housing market interaction studies

## 🔧 Customization

### Adding New Scenarios
1. Modify `integrated_scenario_parameters.yaml`
2. Add scenario-specific parameter sets
3. Update analysis notebooks for new scenarios

### Extending Dimensions
1. Update dimension specifications in model structure
2. Adjust initial value arrays to match new dimensions
3. Verify calculator expressions handle new dimensions

### Adding New Modules
1. Create new module directory with structure files
2. Define cross-module dependencies in integrated model
3. Update parameter files and test notebooks

## 📚 Related Examples

- `multidimensional_population/`: Basic population modeling
- `climate_adaptation_case_studies/`: Climate-specific applications
- Other system dynamics examples in the repository

## 🤝 Contributing

When extending this example:
1. Follow existing naming conventions (snake_case for files, kebab-case for directories)
2. Maintain separation between model structure and scenario parameters
3. Add comprehensive validation and testing
4. Update documentation and validation reports

## 📄 License

This example is part of the ScenaAdaptPy system dynamics toolkit and follows the same licensing terms as the main repository.
