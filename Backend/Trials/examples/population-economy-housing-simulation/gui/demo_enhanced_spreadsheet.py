#!/usr/bin/env python3
"""
Demonstration of Enhanced Spreadsheet Editor Features

This script demonstrates the new comprehensive dimension and data management 
capabilities of the spreadsheet editor, including:

1. Dimension Data Modification
2. Data Locking Mechanism  
3. Automatic Save on Close
4. Integration with YAML models

Run this script to see the enhanced features in action.
"""

import sys
import os
from pathlib import Path

def demo_enhanced_spreadsheet():
    """Demonstrate enhanced spreadsheet editor features."""
    
    print("🚀 Enhanced Spreadsheet Editor Demo")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent, GuiModel
        
        print("✅ Successfully imported enhanced spreadsheet editor")
        
        # Create demo model and components
        demo_model, demo_components = create_demo_model()
        
        # Create the enhanced spreadsheet editor
        editor = SpreadsheetDataEditor(demo_components, demo_model, parent=None)
        
        # Set up YAML model info for auto-save
        gui_model = create_demo_gui_model()
        model_path = Path.cwd() / "demo_model.yaml"
        scenario_path = Path.cwd() / "demo_scenario.yaml"
        editor.set_yaml_model_info(gui_model, str(model_path), str(scenario_path))
        
        # Configure the editor window
        editor.setWindowTitle("Enhanced Spreadsheet Editor Demo")
        editor.resize(1200, 800)
        
        # Show welcome message
        welcome_msg = """
🎉 Welcome to the Enhanced Spreadsheet Editor Demo!

NEW FEATURES TO EXPLORE:

🔒 DATA LOCKING:
   • Click the "🔒 Lock Data" button to prevent accidental modifications
   • Visual indicators show when data is locked
   • Toggle lock/unlock as needed

📐 DIMENSION EDITING:
   • Right-click on column/row headers to edit dimensions
   • Add/remove coordinates from dimensions
   • Rename dimensions
   • Edit dimension labels directly

💾 AUTO-SAVE:
   • Toggle "Auto-save on Close" to automatically save changes
   • Changes are saved back to YAML files when closing
   • Manual save options still available

🔗 YAML INTEGRATION:
   • Full integration with YAML model structure
   • Dimension changes update the model
   • Component data synchronized with YAML

Try these features:
1. Right-click on headers to modify dimensions
2. Toggle the lock button to see visual changes
3. Make some edits and close to test auto-save
4. Use the toolbar buttons for enhanced functionality
        """
        
        QMessageBox.information(editor, "Enhanced Features Demo", welcome_msg)
        
        # Show the editor
        editor.show()
        
        print("🎯 Demo editor launched with enhanced features!")
        print("\nFeatures to try:")
        print("• Right-click on column/row headers for dimension editing")
        print("• Use the 🔒 Lock Data button to protect your data")
        print("• Toggle Auto-save on Close for automatic YAML saving")
        print("• Make changes and close to see auto-save in action")
        
        # Run the application
        return app.exec()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install PyQt6 PyYAML")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def create_demo_model():
    """Create a demo model with climate adaptation components."""

    class DemoModel:
        def __init__(self):
            self.name = "Climate Adaptation Demo Model"
            self.dimensions = {
                'age': {
                    'labels': ['0-18', '19-35', '36-55', '56-70', '70+'],
                    'description': 'Age groups for population analysis',
                    'type': 'categorical',
                    'size': 5
                },
                'housetype': {
                    'labels': ['single_family', 'townhouse', 'condo', 'apartment', 'other'],
                    'description': 'Housing types',
                    'type': 'categorical',
                    'size': 5
                },
                'year': {
                    'labels': ['2020', '2025', '2030', '2035', '2040', '2045', '2050'],
                    'description': 'Projection years',
                    'type': 'temporal',
                    'size': 7
                },
                'parcel': {
                    'labels': ['1001', '1002', '1003', '1004', '1005'],
                    'description': 'Property parcels',
                    'type': 'categorical',
                    'size': 5
                },
                'building_type': {
                    'labels': ['residential', 'commercial', 'industrial'],
                    'description': 'Building types',
                    'type': 'categorical',
                    'size': 3
                },
                'zone': {
                    'labels': ['downtown', 'suburbs', 'industrial'],
                    'description': 'Urban zones',
                    'type': 'categorical',
                    'size': 3
                }
            }
    
    # Create demo components with placeholder data
    components = [
        ModelComponent(
            name="population",
            component_type="stock",
            properties={
                'initial_value': {
                    'data_type': 'multidimensional',
                    'base_value': 15000,
                    'sample_data': {
                        ('population', '0-18', 'single_family', '2020'): 3200,
                        ('population', '19-35', 'single_family', '2020'): 4100,
                        ('population', '36-55', 'single_family', '2020'): 3800,
                        ('population', '56-70', 'single_family', '2020'): 2500,
                        ('population', '70+', 'single_family', '2020'): 1400,
                        ('population', '19-35', 'condo', '2020'): 2800,
                        ('population', '36-55', 'condo', '2020'): 2200,
                        ('population', '19-35', 'apartment', '2020'): 1900,
                        ('population', '36-55', 'apartment', '2020'): 1600,
                    }
                },
                'units': 'people',
                'spatial_dims': ['age', 'housetype', 'year'],
                'description': 'Population by age, housing type, and year'
            }
        ),
        ModelComponent(
            name="housing_stock",
            component_type="stock",
            properties={
                'initial_value': {
                    'data_type': 'multidimensional',
                    'base_value': 8000,
                    'sample_data': {
                        ('housing_stock', 'single_family', '2020'): 4200,
                        ('housing_stock', 'townhouse', '2020'): 1200,
                        ('housing_stock', 'condo', '2020'): 1800,
                        ('housing_stock', 'apartment', '2020'): 800,
                        ('housing_stock', 'single_family', '2025'): 4350,
                        ('housing_stock', 'townhouse', '2025'): 1280,
                        ('housing_stock', 'condo', '2025'): 1920,
                        ('housing_stock', 'apartment', '2025'): 850,
                    }
                },
                'units': 'units',
                'spatial_dims': ['housetype', 'year'],
                'description': 'Housing stock by type and year'
            }
        ),
        ModelComponent(
            name="flood_protection_measures",
            component_type="stock",
            properties={
                'initial_value': {
                    'data_type': 'multidimensional',
                    'base_value': 5,
                    'sample_data': {
                        ('flood_protection_measures', '1001', 'residential', '2020'): 2,
                        ('flood_protection_measures', '1002', 'residential', '2020'): 3,
                        ('flood_protection_measures', '1003', 'residential', '2020'): 1,
                        ('flood_protection_measures', '1001', 'commercial', '2020'): 5,
                        ('flood_protection_measures', '1002', 'commercial', '2020'): 4,
                        ('flood_protection_measures', '1001', 'residential', '2025'): 4,
                        ('flood_protection_measures', '1002', 'residential', '2025'): 6,
                    }
                },
                'units': 'measures',
                'spatial_dims': ['parcel', 'building_type', 'year'],
                'description': 'Flood protection measures by parcel, building type, and year',
                'min_value': 0,
                'max_value': 100
            }
        ),
        ModelComponent(
            name="household_income",
            component_type="auxiliary",
            properties={
                'value': {
                    'data_type': 'multidimensional',
                    'base_value': 72000,
                    'sample_data': {
                        ('household_income', '19-35', 'single_family', '2020'): 65000,
                        ('household_income', '36-55', 'single_family', '2020'): 85000,
                        ('household_income', '56-70', 'single_family', '2020'): 92000,
                        ('household_income', '19-35', 'condo', '2020'): 58000,
                        ('household_income', '36-55', 'condo', '2020'): 75000,
                        ('household_income', '19-35', 'apartment', '2020'): 48000,
                        ('household_income', '36-55', 'apartment', '2020'): 62000,
                    }
                },
                'units': 'dollars/year',
                'spatial_dims': ['age', 'housetype', 'year'],
                'description': 'Average household income by age, housing type, and year'
            }
        )
    ]
    
    return DemoModel(), components

def create_demo_gui_model():
    """Create a GUI model for YAML integration demo."""
    gui_model = GuiModel("Climate Adaptation Demo", "Demo model for enhanced spreadsheet features")
    
    # Set model parameters
    gui_model.time_horizon = 30
    gui_model.dt = 1.0
    gui_model.time_units = "year"
    
    # Add dimensions
    gui_model.dimensions = {
        'age': {
            'labels': ['0-18', '19-35', '36-55', '56-70', '70+'],
            'description': 'Age groups for population analysis',
            'type': 'categorical',
            'size': 5
        },
        'housetype': {
            'labels': ['single_family', 'townhouse', 'condo', 'apartment', 'other'],
            'description': 'Housing types',
            'type': 'categorical',
            'size': 5
        },
        'year': {
            'labels': ['2020', '2025', '2030', '2035', '2040', '2045', '2050'],
            'description': 'Projection years',
            'type': 'temporal',
            'size': 7
        },
        'parcel': {
            'labels': ['1001', '1002', '1003', '1004', '1005'],
            'description': 'Property parcels',
            'type': 'categorical',
            'size': 5
        },
        'building_type': {
            'labels': ['residential', 'commercial', 'industrial'],
            'description': 'Building types',
            'type': 'categorical',
            'size': 3
        },
        'zone': {
            'labels': ['downtown', 'suburbs', 'industrial'],
            'description': 'Urban zones',
            'type': 'categorical',
            'size': 3
        }
    }
    
    return gui_model

if __name__ == "__main__":
    exit_code = demo_enhanced_spreadsheet()
    sys.exit(exit_code)
