#!/usr/bin/env python3
"""
Test the new component properties dialog.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt

from yaml_integration.yaml_loader import GuiModel, ModelComponent
from dialogs.component_properties_dialog import ComponentPropertiesDialog


class TestWindow(QMainWindow):
    """Test window for the component properties dialog."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Component Properties Dialog Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create test data
        self.model = GuiModel("Test Model", "Test model for component properties")
        
        # Add some test dimensions
        self.model.dimensions['age_group'] = {
            'size': 5,
            'labels': ['0-17', '18-24', '25-44', '45-64', '65+'],
            'description': 'Age groups for population analysis',
            'type': 'categorical'
        }
        
        self.model.dimensions['zone'] = {
            'size': 3,
            'labels': ['Urban', 'Suburban', 'Rural'],
            'description': 'Geographic zones',
            'type': 'spatial'
        }
        
        self.model.dimensions['time_period'] = {
            'size': 10,
            'labels': [str(year) for year in range(2020, 2030)],
            'description': 'Time periods for simulation',
            'type': 'temporal'
        }
        
        # Create test stock component
        self.stock = ModelComponent(
            name="Population",
            component_type="stock",
            properties={
                'initial_value': 10000,
                'units': 'people',
                'spatial_dims': ['age_group'],
                'description': 'Population stock with age dimension'
            }
        )
        
        self.model.add_component(self.stock)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the test UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Test button
        test_btn = QPushButton("Open Stock Properties Dialog")
        test_btn.clicked.connect(self.open_properties_dialog)
        layout.addWidget(test_btn)
        
        # Info
        info_text = """
        This test creates a stock component with:
        - Name: Population
        - Initial Value: 10,000 people
        - Dimensions: age_group (5 age groups)
        
        Available model dimensions:
        - age_group (0-17, 18-24, 25-44, 45-64, 65+)
        - zone (Urban, Suburban, Rural)
        - time_period (2020-2029)
        
        Click the button to open the properties dialog.
        """
        
        from PyQt6.QtWidgets import QLabel
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(info_label)
    
    def open_properties_dialog(self):
        """Open the component properties dialog."""
        try:
            dialog = ComponentPropertiesDialog(self.stock, self.model, parent=self)
            dialog.component_modified.connect(self.on_component_modified)
            dialog.exec()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Dialog Error",
                f"Error opening properties dialog:\n\n{e}"
            )
            import traceback
            traceback.print_exc()
    
    def on_component_modified(self, component):
        """Handle component modification."""
        print(f"Component modified: {component.name}")
        print(f"Properties: {component.properties}")


def main():
    """Run the test."""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
