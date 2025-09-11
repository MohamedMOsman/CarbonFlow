# Multidimensional Population Modeling with YAML Configuration

## 🌍 Advanced Climate Adaptation Modeling Framework

This directory contains a comprehensive example of multidimensional population modeling using the System Dynamics Toolkit with YAML configuration. The framework demonstrates sophisticated climate adaptation modeling with population dynamics across multiple demographic dimensions.

## 📁 File Structure

```
examples/
├── 03_multidimensional_yaml_population.ipynb    # Main demonstration notebook
├── test_multidimensional_yaml.py               # Standalone test script
├── yaml_models/
│   ├── multidimensional_population_model.yaml  # Model structure definition
│   ├── baseline_scenario.yaml                  # Baseline climate scenario
│   └── high_climate_stress_scenario.yaml       # High stress climate scenario
└── README_Multidimensional_Modeling.md         # This file
```

## 🏗️ Model Architecture

### Multidimensional Structure
The model tracks population across three key dimensions:

- **Age Groups**: Young (0-18), Adult (19-65), Elderly (65+)
- **Income Levels**: Low, Medium, High income
- **Regions**: Urban, Rural

This creates a 3D population array: `Population[age, income, region, time]`

### Key Features
- ✅ **Declarative YAML Configuration**: Model structure separate from parameters
- ✅ **Climate-Sensitive Demographics**: Temperature and extreme event impacts
- ✅ **Economic Integration**: GDP effects and regional economic differences
- ✅ **Migration Modeling**: Climate and economic-driven population flows
- ✅ **Multidimensional Visualization**: Advanced plotting for complex data
- ✅ **Scenario Analysis**: Easy parameter modification for different futures

## 🚀 Quick Start

### Option 1: Jupyter Notebook (Recommended)
```bash
cd examples/
jupyter notebook 03_multidimensional_yaml_population.ipynb
```

### Option 2: Standalone Script
```bash
cd examples/
python test_multidimensional_yaml.py
```

## 📊 Model Components

### 1. Model Structure (`multidimensional_population_model.yaml`)

Defines the fundamental model architecture:

```yaml
dimensions:
  age_group:
    size: 3
    labels: ["young_0_18", "adult_19_65", "elderly_65_plus"]
  income_level:
    size: 3  
    labels: ["low_income", "medium_income", "high_income"]
  region:
    size: 2
    labels: ["urban", "rural"]

elements:
  stocks:
    - name: "Population"
      initial_value:
        array:
          shape: [3, 3, 2]
          values: "$initial_population_distribution"
      spatial_dims: ["age_group", "income_level", "region"]
```

### 2. Scenario Parameters

#### Baseline Scenario (`baseline_scenario.yaml`)
- Moderate climate change (2°C warming by 2100)
- Current demographic and economic trends
- Standard climate sensitivity parameters

#### High Stress Scenario (`high_climate_stress_scenario.yaml`)
- Accelerated climate change (7.5°C warming by 2100)
- Enhanced climate sensitivity
- Increased extreme events and economic disruption

### 3. Custom Functions

The model includes sophisticated rate calculation functions:

```yaml
functions:
  multidimensional_birth_calculator:
    expression: "base_birth_rate * fertility_multiplier * (1 - climate_fertility_impact * climate_stress) * population"
    dependencies: ["population", "climate_stress", "fertility_multiplier"]
    output_dimensions: ["age_group", "income_level", "region"]
```

## 🎯 Key Modeling Insights

### Climate Impacts
- **Differential Vulnerability**: Elderly, low-income, and rural populations face higher risks
- **Compound Effects**: Climate, economic, and demographic factors interact
- **Threshold Effects**: Non-linear responses to climate stress
- **Adaptation Capacity**: Income and location affect resilience

### Population Dynamics
- **Demographic Momentum**: Age structure affects future growth
- **Migration Patterns**: Climate drives rural-to-urban migration
- **Economic Mobility**: Climate stress affects income transitions
- **Intergenerational Effects**: Impacts compound over time

## 🔧 Customization Guide

### Creating New Scenarios

1. **Copy existing scenario**:
   ```bash
   cp yaml_models/baseline_scenario.yaml yaml_models/my_scenario.yaml
   ```

2. **Modify key parameters**:
   ```yaml
   constants:
     warming_trend: 0.008  # Faster warming
     climate_fertility_impact: 0.5  # Stronger fertility impact
     climate_migration_sensitivity: 0.05  # More migration
   ```

3. **Run with new parameters**:
   ```python
   # In notebook or script
   with open('yaml_models/my_scenario.yaml', 'r') as file:
       my_scenario = yaml.safe_load(file)
   
   my_config = model_structure.copy()
   my_config['constants'] = my_scenario['constants']
   my_model = builder.build_from_dict(my_config)
   ```

### Adding New Dimensions

To add an education dimension:

1. **Update model structure**:
   ```yaml
   dimensions:
     education:
       size: 3
       labels: ["primary", "secondary", "tertiary"]
   ```

2. **Adjust array shapes**:
   ```yaml
   initial_value:
     array:
       shape: [3, 3, 2, 3]  # age, income, region, education
   ```

3. **Update rate functions** to handle new dimension

## 📈 Visualization Capabilities

The framework includes advanced visualization tools:

### Population Pyramids
- Animated age structure evolution
- Income stratification within age groups
- Regional comparisons

### Climate Impact Heatmaps
- Vulnerability across all dimensions
- Differential impact visualization
- Risk assessment matrices

### Scenario Comparison Dashboards
- Side-by-side trajectory comparison
- Growth rate analysis
- Economic impact assessment

## 🧪 Testing and Validation

### Automated Tests
```bash
python test_multidimensional_yaml.py
```

### Manual Validation
1. **Dimension Consistency**: Verify array shapes match specifications
2. **Mass Balance**: Check population conservation
3. **Parameter Bounds**: Ensure realistic rate values
4. **Scenario Logic**: Validate parameter relationships

## 📚 Technical Details

### Dependencies
- numpy: Multidimensional array operations
- pandas: Time series data management
- matplotlib/seaborn: Visualization
- xarray: Labeled multidimensional arrays
- yaml: Configuration file parsing

### Performance Considerations
- Model complexity scales with dimension sizes
- Memory usage: O(n_age × n_income × n_region × n_time)
- Computation time: Linear with time horizon
- Visualization: May be slow for large arrays

## 🌟 Research Applications

This framework supports:

### Climate Impact Assessment
- Population vulnerability analysis
- Adaptation needs assessment
- Risk quantification

### Policy Analysis
- Intervention effectiveness
- Distributional impact analysis
- Cost-benefit assessment

### Scenario Planning
- Future population projections
- Climate adaptation pathways
- Uncertainty quantification

## 🤝 Contributing

To contribute improvements:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-capability`
3. **Add tests** for new functionality
4. **Update documentation**
5. **Submit pull request**

### Areas for Enhancement
- Additional demographic dimensions (health, education)
- Spatial connectivity and migration networks
- Economic feedback mechanisms
- Policy intervention modeling
- Uncertainty quantification methods

## 📞 Support

For questions or issues:
- Review the Jupyter notebook for detailed examples
- Check the test script for basic functionality
- Examine YAML files for configuration options
- Consult the main toolkit documentation

## 🏆 Success Criteria

A successful implementation should demonstrate:
- ✅ Multidimensional population tracking
- ✅ Climate-sensitive demographic processes
- ✅ Scenario-based parameter modification
- ✅ Comprehensive visualization capabilities
- ✅ Realistic climate adaptation insights

---

**🌍 This framework provides the foundation for sophisticated climate adaptation modeling, enabling researchers and policymakers to understand complex human-environment interactions in a changing climate.**
