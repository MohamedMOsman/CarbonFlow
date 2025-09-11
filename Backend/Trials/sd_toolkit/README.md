# High-Resolution Spatiotemporal System Dynamics Toolkit

A Python-based software toolkit for system dynamics modeling with multi-dimensional, unit-aware data structures designed for climate action adaptation modeling.

## Features

- **Unit-Aware Calculations**: Built-in support for dimensional analysis and unit conversions
- **Spatiotemporal Data Handling**: Multi-dimensional data structures for spatial and temporal modeling
- **System Dynamics Engine**: Core modeling components including stocks, flows, and feedback loops
- **Climate Adaptation Focus**: Specialized tools for climate action and adaptation modeling
- **Visualization Tools**: Comprehensive plotting and analysis capabilities

## Project Structure

```
sd_toolkit/
├── sd_toolkit/           # Main package
│   ├── core/            # Core utilities (units, math)
│   ├── data/            # Data loading and handling
│   ├── engine/          # System dynamics modeling engine
│   └── analysis/        # Analysis and visualization tools
├── models/              # Example models
├── notebooks/           # Jupyter notebook examples
└── tests/              # Test suite
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

```python
from sd_toolkit.engine.system import SystemModel
from sd_toolkit.engine.elements import Stock, Flow
from sd_toolkit.analysis.plotting import SystemPlotter

# Create a simple system dynamics model
model = SystemModel("Basic Growth Model")
inventory = Stock("Inventory", initial_value=1000, units="units")
production_rate = Flow("Production", rate=0.02, units="units/year")

# Add elements to model
model.add_element(inventory)
model.add_element(production_rate)

# Connect flow to stock
inventory.add_inflow(production_rate)

# Run simulation
results = model.simulate(time_horizon=50, dt=0.1)

# Visualize results
plotter = SystemPlotter(model)
plotter.plot_time_series(results, ['Inventory'])
```

## Detailed Usage

### 1. Building Models

The toolkit provides several core elements for building system dynamics models:

- **Stocks**: Accumulations in the system (e.g., population, inventory)
- **Flows**: Rates of change (e.g., birth rate, production rate)
- **Auxiliaries**: Helper calculations and constants
- **Connectors**: Information links between elements

### 2. Unit Management

All calculations are unit-aware using the Pint library:

```python
from sd_toolkit.core.units import Q_, unit_registry

# Create quantities with units
population = Q_(1000, 'people')
birth_rate = Q_(0.02, 'people/year')

# Automatic unit checking and conversion
result = population * birth_rate  # Automatically handles units
```

### 3. Spatial Data Handling

The toolkit supports spatially-explicit modeling:

```python
from sd_toolkit.data.loader import SpatioTemporalData, DataLoader

# Load spatial data
loader = DataLoader()
spatial_data = loader.load('climate_data.nc', var_name='temperature')

# Access spatial coordinates and data
print(spatial_data.coords)
print(spatial_data.shape)
```

### 4. Analysis and Visualization

Comprehensive analysis tools are provided:

```python
from sd_toolkit.analysis.plotting import SystemPlotter, SpatialPlotter

# Time series analysis
plotter = SystemPlotter(model)
plotter.plot_time_series(results)
plotter.plot_phase_diagram(results, 'Stock', 'Auxiliary_Variable')

# Spatial visualization
spatial_plotter = SpatialPlotter()
spatial_plotter.plot_spatial_field(spatial_data)
```

## Examples

The toolkit provides templates and examples for building system dynamics models:

1. **Template-based model creation**: Use built-in templates for common model patterns
   - Exponential growth models
   - Logistic growth with carrying capacity
   - Temperature-dependent rate models

2. **YAML configuration**: Build models using declarative YAML files
   - Separate model structure from parameters
   - Easy scenario comparison and parameter sweeps
   - Multidimensional variable support

## API Reference

### Core Modules

- `sd_toolkit.core.units`: Unit management and dimensional analysis
- `sd_toolkit.data.loader`: Data loading and spatiotemporal data handling
- `sd_toolkit.engine.elements`: System dynamics model elements
- `sd_toolkit.engine.system`: Model container and simulation engine
- `sd_toolkit.analysis.plotting`: Visualization and analysis tools

### Key Classes

- `SystemModel`: Main model container
- `Stock`: Accumulation element
- `Flow`: Rate element
- `Auxiliary`: Helper calculation element
- `SpatioTemporalData`: Multi-dimensional data container
- `SystemPlotter`: Main plotting class
- `MultidimensionalPlotter`: Advanced multidimensional visualization

## Testing

Run the test suite:

```bash
cd sd_toolkit
python -m pytest tests/ -v
```

## Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install in development mode:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{sd_toolkit,
  title={High-Resolution Spatiotemporal System Dynamics Toolkit},
  author={System Dynamics Toolkit Team},
  year={2024},
  url={https://github.com/your-org/sd-toolkit}
}
```

## Support

For questions and support:
- Open an issue on GitHub
- Check the documentation in `notebooks/`
- Review the example models in `models/`
