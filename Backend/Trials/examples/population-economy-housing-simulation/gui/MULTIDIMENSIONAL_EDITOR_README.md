# Multidimensional Component Editor

This document describes the enhanced GUI functionality for defining and editing multidimensional coordinates in system dynamics components.

## Overview

The Multidimensional Component Editor provides an intuitive, spreadsheet-like interface for managing complex multidimensional data structures in system dynamics models. This is particularly valuable for climate adaptation modeling where components often have multiple dimensions such as parcel, building type, time periods, and demographic categories.

## Features

### 1. Interactive Dimension Table Editor
- **Spreadsheet-like interface** with Excel-like functionality
- **Add/remove dimensions** (columns) with custom names
- **Add/remove coordinates** (rows) for each dimension
- **Cell editing** with real-time validation
- **Copy/paste support** for bulk data entry
- **Context menu operations** for quick actions

### 2. Comprehensive Dialog Interface
- **Tabbed interface** with separate views for editing, metadata, preview, and validation
- **Metadata management** for dimension descriptions and types
- **Real-time preview** of dimensional structure and YAML configuration
- **Validation feedback** with errors, warnings, and suggestions

### 3. Visual Integration
- **Double-click activation** on any component to open the editor
- **Visual indicators** on components showing dimensional complexity
- **Component inspector integration** with dedicated "Edit Dimensions" button
- **Status feedback** during editing operations

### 4. Data Validation and Consistency
- **Dimensional consistency checks** across related components
- **Model-level validation** against global dimension definitions
- **Real-time error detection** and user feedback
- **YAML configuration validation** for proper model integration

## Usage

### Opening the Editor

There are three ways to open the multidimensional editor:

1. **Double-click** any component (stock, flow, calculator) on the canvas
2. **Right-click** a component and select "Edit Dimensions" (if available)
3. **Use the Component Inspector** - select a component and click "Edit Dimensions..."

### Using the Dimension Table Editor

#### Adding Dimensions
- Right-click in the table and select "Add Dimension"
- Or use the "Add Dimension" button below the table
- Enter a descriptive name (e.g., "parcel", "building_type", "age_group")

#### Adding Coordinates
- Right-click and select "Add Coordinate"
- Or use the "Add Coordinate" button
- Fill in coordinate values for each dimension

#### Editing Data
- **Single cells**: Click to edit directly
- **Bulk operations**: Select multiple cells and use copy/paste
- **Dimension names**: Double-click column headers to rename

#### Context Menu Operations
- **Copy/Paste**: Standard clipboard operations
- **Add/Remove**: Quick dimension and coordinate management
- **Validation**: Check data integrity

### Metadata Management

Use the **Metadata tab** to define:
- **Description**: Detailed explanation of each dimension
- **Type**: Categorical, numerical, temporal, or spatial
- **Additional properties**: As needed for your model

### Preview and Validation

- **Preview tab**: Shows the dimensional structure and generated YAML
- **Validation tab**: Displays errors, warnings, and suggestions
- **Real-time feedback**: Status updates as you make changes

## Climate Adaptation Examples

### Example 1: Flood Protection Measures
```yaml
spatial_dims: [parcel, building_type, year_built_cohort]
dimensions:
  parcel:
    labels: ['1001', '1002', '1003']
    type: categorical
    description: Property parcel identifiers
  building_type:
    labels: [residential, commercial, industrial]
    type: categorical
    description: Type of building structure
  year_built_cohort:
    labels: [pre_1980, '1980_2000', post_2000]
    type: categorical
    description: Construction era cohorts
```

### Example 2: Population Demographics
```yaml
spatial_dims: [age, income, gender]
dimensions:
  age:
    labels: ['0-18', '19-35', '36-55', '56-75', '75+']
    type: categorical
    description: Age groups for demographic analysis
  income:
    labels: [low, medium, high]
    type: categorical
    description: Income brackets
  gender:
    labels: [male, female, other]
    type: categorical
    description: Gender categories
```

### Example 3: Albedo Changes
```yaml
spatial_dims: [parcel, time_step]
dimensions:
  parcel:
    labels: ['1001', '1002', '1003']
    type: categorical
    description: Property parcel identifiers
  time_step:
    labels: ['2020', '2030', '2040', '2050']
    type: temporal
    description: Simulation time periods
```

## Technical Integration

### Component Types Supported
- **Stocks**: Multidimensional accumulations (e.g., population by demographics)
- **Flows**: Multidimensional rates (e.g., migration by age and income)
- **Calculators**: Multidimensional computations (e.g., climate impact by location and building type)

### YAML Integration
The editor maintains full compatibility with YAML-based model definitions:
- **Preserves existing structure** when editing components
- **Generates valid YAML** for new dimensional definitions
- **Integrates with model-level dimensions** for consistency

### Core Toolkit Integration
- **Compatible with sd_toolkit classes** (Stock, Flow, Calculator)
- **Maintains multidimensional data structures** used by the simulation engine
- **Preserves unit awareness** and other toolkit features

## Validation Features

### Data Integrity Checks
- Empty dimension names detection
- Duplicate dimension name prevention
- Empty coordinate warnings
- Dimensional consistency validation

### Model Consistency Checks
- Comparison with model-level dimensions
- Type consistency validation
- Missing/extra coordinate detection
- Suggestions for model improvements

## Testing

### Running Tests

1. **Core functionality test** (no GUI dependencies):
   ```bash
   python test_dimension_validation.py
   ```

2. **Full GUI test** (requires PyQt6):
   ```bash
   python test_multidimensional_editor.py
   ```

### Test Coverage
- Component creation with multidimensional properties
- Dimensional data structure handling
- Validation logic testing
- YAML configuration generation
- Climate adaptation scenarios

## Files and Structure

### Core Components
- `multidimensional_editor.py`: Main editor dialog and table widget
- `property_editors.py`: Enhanced with dimension support
- `component_inspector.py`: Updated with dimension editing button
- `graphics_items.py`: Enhanced with visual indicators and double-click support

### Test Files
- `test_multidimensional_editor.py`: Full GUI test with climate scenarios
- `test_dimension_validation.py`: Core functionality validation
- `MULTIDIMENSIONAL_EDITOR_README.md`: This documentation

## Future Enhancements

Potential improvements for future versions:
- **Import/export** functionality for dimensional data
- **Template system** for common dimensional structures
- **Advanced visualization** of multidimensional data
- **Batch editing** across multiple components
- **Integration with external data sources**

## Troubleshooting

### Common Issues
1. **PyQt6 not installed**: Install with `pip install PyQt6`
2. **Import errors**: Ensure all GUI modules are in the Python path
3. **Validation errors**: Check dimension names and coordinate consistency
4. **YAML integration issues**: Verify model structure compatibility

### Getting Help
- Check the validation tab for specific error messages
- Use the preview tab to verify dimensional structure
- Refer to the test files for usage examples
- Review the console output for detailed error information
