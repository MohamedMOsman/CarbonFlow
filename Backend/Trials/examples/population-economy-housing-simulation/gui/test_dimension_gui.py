#!/usr/bin/env python3
"""
Test GUI for dimension editing workflow.

This creates a minimal GUI to test the dimension editing functionality
without the full complexity of the main application.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt

from yaml_integration.yaml_loader import GuiModel, ModelComponent
from inspector.component_inspector import ComponentInspector
from inspector.dimension_management import DimensionDetailsEditor


class DimensionTestWindow(QMainWindow):
    """Test window for dimension editing functionality."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Dimension Editing Test")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create test model and component
        self.model = None
        self.component = None
        
        self.setup_ui()
        self.create_test_data()
    
    def setup_ui(self):
        """Set up the test UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Left panel - controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title_label = QLabel("Dimension Editing Test")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        left_layout.addWidget(title_label)
        
        # Test buttons
        self.create_stock_btn = QPushButton("1. Create Stock Component")
        self.create_stock_btn.clicked.connect(self.create_stock_component)
        left_layout.addWidget(self.create_stock_btn)
        
        self.add_age_dim_btn = QPushButton("2. Add Age Dimension")
        self.add_age_dim_btn.clicked.connect(self.add_age_dimension)
        self.add_age_dim_btn.setEnabled(False)
        left_layout.addWidget(self.add_age_dim_btn)
        
        self.edit_age_dim_btn = QPushButton("3. Edit Age Dimension")
        self.edit_age_dim_btn.clicked.connect(self.edit_age_dimension)
        self.edit_age_dim_btn.setEnabled(False)
        left_layout.addWidget(self.edit_age_dim_btn)
        
        self.show_results_btn = QPushButton("4. Show Results")
        self.show_results_btn.clicked.connect(self.show_results)
        self.show_results_btn.setEnabled(False)
        left_layout.addWidget(self.show_results_btn)
        
        # Status display
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(200)
        self.status_text.setPlainText("Ready to test dimension editing workflow...\n")
        left_layout.addWidget(QLabel("Status:"))
        left_layout.addWidget(self.status_text)
        
        left_layout.addStretch()
        
        # Right panel - component inspector
        self.inspector = ComponentInspector()
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.inspector)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
    
    def create_test_data(self):
        """Create initial test data."""
        self.model = GuiModel("Test Model", "Model for testing dimension editing")
        self.inspector.set_model(self.model)
        self.log("✅ Test model created")
    
    def create_stock_component(self):
        """Create a test stock component."""
        try:
            self.component = ModelComponent(
                name="Population",
                component_type="stock",
                properties={
                    'initial_value': 10000,
                    'units': 'people',
                    'spatial_dims': [],
                    'description': 'Population stock for testing dimension editing'
                }
            )
            
            self.model.add_component(self.component)
            self.inspector.set_component(self.component)
            
            self.add_age_dim_btn.setEnabled(True)
            self.log("✅ Stock component 'Population' created")
            self.log("   Initial value: 10,000 people")
            self.log("   Spatial dimensions: []")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create stock component: {e}")
            self.log(f"❌ Error creating stock: {e}")
    
    def add_age_dimension(self):
        """Add an age dimension to the component."""
        try:
            # Add dimension to model
            self.model.dimensions['age'] = {
                'size': 3,
                'labels': ['0-17', '18-64', '65+'],
                'description': 'Age groups for population analysis',
                'type': 'categorical'
            }
            
            # Add dimension to component
            self.component.properties['spatial_dims'] = ['age']
            
            # Update inspector
            self.inspector.set_component(self.component)
            
            self.edit_age_dim_btn.setEnabled(True)
            self.show_results_btn.setEnabled(True)
            
            self.log("✅ Age dimension added to component")
            self.log("   Labels: ['0-17', '18-64', '65+']")
            self.log("   Size: 3")
            self.log("   Component now has spatial_dims: ['age']")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add age dimension: {e}")
            self.log(f"❌ Error adding dimension: {e}")
    
    def edit_age_dimension(self):
        """Edit the age dimension using the detailed editor."""
        try:
            if 'age' not in self.model.dimensions:
                QMessageBox.warning(self, "No Dimension", "Age dimension not found in model")
                return
            
            age_data = self.model.dimensions['age']
            self.log("🔧 Opening dimension details editor...")
            
            # Open the dimension details editor
            editor = DimensionDetailsEditor('age', age_data, parent=self)
            
            if editor.exec() == editor.DialogCode.Accepted:
                # Get updated data
                updated_data = editor.get_updated_dimension_data()
                self.model.dimensions['age'] = updated_data
                
                # Update inspector
                self.inspector.set_component(self.component)
                
                self.log("✅ Age dimension updated successfully!")
                self.log(f"   New size: {updated_data.get('size', 0)}")
                self.log(f"   New labels: {updated_data.get('labels', [])}")
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Age dimension updated!\n"
                    f"New size: {updated_data.get('size', 0)} age groups\n"
                    f"Labels: {', '.join(updated_data.get('labels', [])[:3])}..."
                )
            else:
                self.log("⚠️ Dimension editing cancelled")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit dimension: {e}")
            self.log(f"❌ Error editing dimension: {e}")
            import traceback
            traceback.print_exc()
    
    def show_results(self):
        """Show the final results."""
        try:
            if not self.component or not self.model:
                return
            
            self.log("\n📊 FINAL RESULTS:")
            self.log("=" * 30)
            
            # Component info
            self.log(f"Component: {self.component.name}")
            self.log(f"Type: {self.component.component_type}")
            self.log(f"Initial Value: {self.component.properties.get('initial_value')}")
            self.log(f"Units: {self.component.properties.get('units')}")
            
            # Dimension info
            spatial_dims = self.component.properties.get('spatial_dims', [])
            self.log(f"Spatial Dimensions: {spatial_dims}")
            
            for dim_name in spatial_dims:
                if dim_name in self.model.dimensions:
                    dim_data = self.model.dimensions[dim_name]
                    self.log(f"\nDimension '{dim_name}':")
                    self.log(f"  Size: {dim_data.get('size', 0)}")
                    self.log(f"  Type: {dim_data.get('type', 'unknown')}")
                    self.log(f"  Labels: {dim_data.get('labels', [])}")
                    self.log(f"  Description: {dim_data.get('description', 'N/A')}")
            
            self.log("\n🎉 Test completed successfully!")
            
        except Exception as e:
            self.log(f"❌ Error showing results: {e}")
    
    def log(self, message):
        """Add a message to the status log."""
        self.status_text.append(message)
        self.status_text.ensureCursorVisible()


def main():
    """Run the dimension editing test."""
    app = QApplication(sys.argv)
    
    window = DimensionTestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
