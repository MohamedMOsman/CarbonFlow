# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CarbonFlow is a System Dynamics Model project with multiple components:
- **Python backend** with system dynamics toolkit (`sd_toolkit`) for climate adaptation modeling
- **React frontend** (`sdm-react`) for interactive model building and visualization
- **PyQt6 GUI application** for advanced model editing and spreadsheet-like data manipulation
- **YAML-based model configuration** system for defining model structures and scenarios

## Architecture

### Backend: System Dynamics Toolkit (`Backend/Trials/sd_toolkit/`)
- **Core engine**: Unit-aware calculations using Pint library for dimensional analysis
- **Spatiotemporal modeling**: Multi-dimensional data structures for climate modeling
- **Model elements**: Stocks, Flows, Auxiliaries, and Connectors for system dynamics
- **YAML configuration**: Declarative model building with parameter separation
- **Analysis tools**: Comprehensive plotting and visualization capabilities

### Frontend: React Application (`sdm-react/`)
- **Interactive canvas**: Drag-and-drop system for building models visually
- **Component types**: Stock, Flow, Converter, Dataset, Calculator, Reference
- **Hierarchical systems**: Tree-based organization with scenarios
- **Data management**: CSV import/export, PivotTable.js integration
- **Autosave**: localStorage persistence with full model JSON export/import

### GUI Application (`Backend/Trials/examples/population-economy-housing-simulation/gui/`)
- **PyQt6-based**: Desktop application for advanced model editing
- **Spreadsheet editor**: Data table manipulation with multidimensional support
- **Component properties**: Detailed configuration of model elements
- **Project management**: Save/load model projects

### Model Configuration
- **YAML structures**: Model definitions in `model_structure.yaml` files
- **Scenario parameters**: Separate parameter files for different scenarios
- **Multidimensional support**: Complex data structures with spatial/temporal dimensions
- **Climate adaptation focus**: Specialized for climate action modeling

## Common Development Commands

### React Frontend
```bash
cd sdm-react
npm install          # Install dependencies
npm run dev         # Start development server
npm run build       # Build for production
npm run preview     # Preview production build
```

### Python Backend
```bash
cd Backend/Trials/sd_toolkit
pip install -r requirements.txt    # Install dependencies
python -m pytest tests/ -v        # Run tests

cd Backend/Trials/examples/population-economy-housing-simulation/gui
pip install -r requirements.txt    # Install GUI dependencies
python main.py                     # Run GUI application (if main.py exists)
```

### Testing
- **Python**: Use `pytest` with coverage via `pytest-cov`
- **React**: No test framework configured yet
- **GUI**: Use `pytest-qt` for PyQt6 testing

## Key File Patterns

### Model Definition Files
- `model_structure.yaml`: Defines stocks, flows, and system structure
- `scenario_parameters.yaml`: Contains parameter values for different scenarios
- `integrated_model_structure.yaml`: Combined model definitions
- `*.json`: Model exports and component configurations

### Python Module Structure
- `sd_toolkit/core/`: Units and mathematical utilities
- `sd_toolkit/engine/`: System dynamics modeling components
- `sd_toolkit/data/`: Data loading and spatiotemporal handling
- `sd_toolkit/analysis/`: Plotting and analysis tools
- `sd_toolkit/config/`: YAML configuration and templates

### React Component Structure
- `components/`: Reusable UI components
- `context/`: React context for state management
- `App.jsx`: Main application component
- Uses Tailwind CSS via CDN

## Development Notes

### Data Flow
1. YAML configurations define model structure
2. Python toolkit processes and validates models
3. React frontend provides visual editing interface
4. PyQt6 GUI offers advanced data manipulation
5. Results flow back through JSON exports

### Integration Points
- Models defined in YAML can be loaded by both Python backend and React frontend
- JSON export format is shared between React and Python components
- GUI application can generate YAML configurations

### Dependencies Management
- Python projects use `requirements.txt` files
- React uses standard `package.json`
- GUI application requires PyQt6 and scientific computing stack
- Core toolkit requires numpy, pandas, scipy, matplotlib ecosystem

## Repository Setup
- Uses PowerShell script for GitHub repository creation
- Git repository with `main` as primary branch
- Currently on `AddBackend` branch
- Includes comprehensive `.gitignore` for Python, React, and data files