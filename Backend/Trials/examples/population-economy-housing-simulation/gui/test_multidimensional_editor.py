#!/usr/bin/env python3
"""
Test script for the multidimensional component editor.

This script demonstrates the multidimensional editor functionality
with climate adaptation modeling scenarios.
"""

import sys
import os
from pathlib import Path

# Add the GUI directory to the Python path
gui_dir = Path(__file__).parent
sys.path.insert(0, str(gui_dir))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

# Import our components
from yaml_integration.yaml_loader import ModelComponent, GuiModel
from inspector.multidimensional_editor import MultidimensionalEditorDialog


class TestMainWindow(QMainWindow):
    """Main window for testing the multidimensional editor."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Multidimensional Editor Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create test components and model
        self.setup_test_data()
        
        # Setup UI
        self.setup_ui()
        
    def setup_test_data(self):
        """Create test components with multidimensional data."""
        
        # Create a test model
        self.test_model = GuiModel("Climate Adaptation Test Model")
        
        # Define dimensions for climate adaptation
        self.test_model.dimensions = {
            'parcel': {
                'labels': ['1001', '1002', '1003'],
                'size': 3,
                'type': 'categorical',
                'description': 'Property parcel identifiers'
            },
            'building_type': {
                'labels': ['residential', 'commercial', 'industrial'],
                'size': 3,
                'type': 'categorical',
                'description': 'Type of building structure'
            },
            'year_built_cohort': {
                'labels': ['pre_1980', '1980_2000', 'post_2000'],
                'size': 3,
                'type': 'categorical',
                'description': 'Construction era cohorts'
            },
            'time_step': {
                'labels': ['2020', '2030', '2040', '2050'],
                'size': 4,
                'type': 'temporal',
                'description': 'Simulation time steps'
            }
        }
        
        # Create test components
        
        # 1. Population stock with age, income, gender dimensions
        self.population_stock = ModelComponent(
            name="population",
            component_type="stock",
            properties={
                'initial_value': 10000,
                'units': 'people',
                'spatial_dims': ['age', 'income', 'gender'],
                'description': 'Population by demographic categories'
            }
        )
        
        # 2. Flood protection measures stock
        self.flood_protection_stock = ModelComponent(
            name="flood_protection_measures",
            component_type="stock",
            properties={
                'initial_value': 0,
                'units': 'measures',
                'spatial_dims': ['parcel', 'building_type', 'year_built_cohort'],
                'description': 'Flood protection measures by parcel and building characteristics'
            }
        )
        
        # 3. Albedo change flow
        self.albedo_flow = ModelComponent(
            name="albedo_change_rate",
            component_type="flow",
            properties={
                'rate': 0.01,
                'units': 'albedo_units/year',
                'spatial_dims': ['parcel', 'time_step'],
                'description': 'Rate of albedo change for climate adaptation'
            }
        )
        
        # 4. Climate impact calculator
        self.climate_calculator = ModelComponent(
            name="climate_impact_calculator",
            component_type="calculator",
            properties={
                'expression': 'temperature_increase * vulnerability_factor',
                'units': 'impact_units',
                'spatial_dims': ['parcel', 'building_type'],
                'description': 'Calculates climate impact based on temperature and vulnerability'
            }
        )
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Multidimensional Component Editor Test")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; margin: 10px; }")
        layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel(
            "Click the buttons below to test the multidimensional editor with different component types.\n"
            "Each component has different dimensional structures relevant to climate adaptation modeling."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("QLabel { margin: 10px; color: #666; }")
        layout.addWidget(instructions)
        
        # Test buttons
        
        # Population stock button
        pop_btn = QPushButton("Edit Population Stock Dimensions")
        pop_btn.clicked.connect(lambda: self.open_editor(self.population_stock))
        pop_btn.setToolTip("Population with age, income, gender dimensions")
        layout.addWidget(pop_btn)
        
        # Flood protection stock button
        flood_btn = QPushButton("Edit Flood Protection Stock Dimensions")
        flood_btn.clicked.connect(lambda: self.open_editor(self.flood_protection_stock))
        flood_btn.setToolTip("Flood protection measures with parcel, building type, year built cohort dimensions")
        layout.addWidget(flood_btn)
        
        # Albedo flow button
        albedo_btn = QPushButton("Edit Albedo Change Flow Dimensions")
        albedo_btn.clicked.connect(lambda: self.open_editor(self.albedo_flow))
        albedo_btn.setToolTip("Albedo change rate with parcel and time step dimensions")
        layout.addWidget(albedo_btn)
        
        # Climate calculator button
        climate_btn = QPushButton("Edit Climate Impact Calculator Dimensions")
        climate_btn.clicked.connect(lambda: self.open_editor(self.climate_calculator))
        climate_btn.setToolTip("Climate impact calculator with parcel and building type dimensions")
        layout.addWidget(climate_btn)
        
        layout.addStretch()
        
    def open_editor(self, component):
        """Open the multidimensional editor for the given component."""
        
        try:
            dialog = MultidimensionalEditorDialog(component, self.test_model, self)
            result = dialog.exec()
            
            if result == dialog.DialogCode.Accepted:
                print(f"Component '{component.name}' was modified successfully!")
                print(f"New spatial dimensions: {component.properties.get('spatial_dims', [])}")
            else:
                print(f"Editing of component '{component.name}' was cancelled.")
                
        except Exception as e:
            print(f"Error opening editor for {component.name}: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function to run the test."""
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Multidimensional Editor Test")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = TestMainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
