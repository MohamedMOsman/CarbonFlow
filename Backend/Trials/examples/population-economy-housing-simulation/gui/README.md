# System Dynamics GUI Application

A desktop graphical user interface for the system dynamics modeling toolkit, providing visual model design, simulation execution, and results analysis capabilities.

## Features

### Core Functionality
- **Visual Model Editor**: Drag-and-drop canvas for designing system dynamics models
- **Component Palette**: Library of stocks, flows, calculators, and constants
- **Component Inspector**: Detailed property viewing and editing for model elements
- **YAML Integration**: Load/save models in YAML format compatible with sd_toolkit
- **Simulation Control**: Run simulations with progress monitoring and control
- **Results Visualization**: Charts, graphs, and multidimensional data displays

### System Dynamics Support
- **Multidimensional Variables**: Full support for complex dimensional structures
- **Cross-Module Integration**: Handle integrated models with multiple modules
- **Scenario Analysis**: Switch between different parameter sets
- **Real-time Debugging**: Inspect component values during simulation

## Installation

### Prerequisites
- Python 3.8 or higher
- PyQt6 (installed via requirements.txt)
- System Dynamics Toolkit (sd_toolkit)

### Setup
1. Navigate to the GUI directory:
   ```bash
   cd examples/population-economy-housing-simulation/gui/
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Loading a Model
1. **File → Open Model** or `Ctrl+O`
2. Select a YAML model file (e.g., `../integrated_model_structure.yaml`)
3. The model will be loaded and displayed on the canvas

### Visual Model Design
1. **Component Palette**: Drag components from the left panel to the canvas
2. **Connections**: Draw connections between components by clicking and dragging
3. **Properties**: Select components to view/edit properties in the right panel

### Running Simulations
1. **Simulation → Run Simulation** or `F5`
2. Monitor progress in the status bar
3. View results in the visualization panel

### Saving Models
1. **File → Save Model** or `Ctrl+S` to save to current file
2. **File → Save As** or `Ctrl+Shift+S` to save with new name

## Architecture

### Main Components

```
gui/
├── main.py                 # Application entry point
├── main_window.py         # Main application window
├── canvas/                # Visual model editor
│   ├── model_canvas.py    # Main canvas widget
│   └── graphics_items.py  # Visual component representations
├── components/            # Component palette and definitions
│   ├── palette.py         # Component palette widget
│   └── component_types.py # System dynamics component definitions
├── inspector/             # Component property inspection
│   ├── component_inspector.py  # Main inspector widget
│   └── property_editors.py     # Property editing widgets
├── yaml_integration/      # YAML loading/saving
│   ├── yaml_loader.py     # Model loading from YAML
│   └── yaml_saver.py      # Model saving to YAML
├── simulation/            # Simulation control and execution
│   ├── simulation_controller.py  # Simulation management
│   └── progress_dialog.py       # Progress monitoring
└── plotting/              # Results visualization
    ├── results_viewer.py  # Results display widget
    └── plot_widgets.py    # Individual plot components
```

### Integration with sd_toolkit

The GUI integrates seamlessly with the existing sd_toolkit:

- **YAMLSystemBuilder**: Used to load/build models from YAML files
- **SystemModel**: Core model representation and simulation execution
- **SystemPlotter**: Results visualization and analysis
- **MultidimensionalPlotter**: Advanced multidimensional data visualization

## Development Status

### Completed
- [x] Project structure and dependencies
- [x] Main application window and basic UI layout
- [x] Menu system and toolbar framework
- [x] Docked panels for palette and inspector

### In Progress
- [ ] YAML integration layer
- [ ] Visual model editor canvas
- [ ] Component palette and toolbox
- [ ] Component inspector/debugger panel
- [ ] Simulation engine integration
- [ ] Results visualization
- [ ] Visual connection system

### Planned
- [ ] Advanced editing features (undo/redo, copy/paste)
- [ ] Model validation and error checking
- [ ] Export functionality (images, data)
- [ ] Plugin system for custom components
- [ ] Collaborative editing features

## Testing

Run the GUI application:
```bash
python main.py
```

For development testing:
```bash
pytest tests/
```

## Contributing

When adding new features:
1. Follow the existing architecture patterns
2. Maintain compatibility with sd_toolkit
3. Add appropriate error handling and user feedback
4. Update documentation and tests

## License

This GUI application is part of the System Dynamics Toolkit project.
