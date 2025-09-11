#!/usr/bin/env python3
"""
Test script for the component inspector functionality.

This script tests the component inspector with different component types.
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt

from component_inspector import ComponentInspector
from yaml_integration.yaml_loader import YAMLModelLoader, GuiModel, ModelComponent
from components.component_types import create_component_template


class InspectorTestWindow(QMainWindow):
    """Test window for the component inspector."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Component Inspector Test")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create control panel
        control_panel = QWidget()
        control_panel.setMaximumWidth(200)
        control_layout = QVBoxLayout(control_panel)
        
        # Test buttons
        load_model_btn = QPushButton("Load Test Model")
        load_model_btn.clicked.connect(self.load_test_model)
        control_layout.addWidget(load_model_btn)
        
        control_layout.addWidget(QWidget())  # Spacer
        
        # Component test buttons
        test_stock_btn = QPushButton("Test Stock")
        test_stock_btn.clicked.connect(lambda: self.test_component('stock'))
        control_layout.addWidget(test_stock_btn)
        
        test_flow_btn = QPushButton("Test Flow")
        test_flow_btn.clicked.connect(lambda: self.test_component('flow'))
        control_layout.addWidget(test_flow_btn)
        
        test_calc_btn = QPushButton("Test Calculator")
        test_calc_btn.clicked.connect(lambda: self.test_component('calculator'))
        control_layout.addWidget(test_calc_btn)
        
        test_aux_btn = QPushButton("Test Auxiliary")
        test_aux_btn.clicked.connect(lambda: self.test_component('auxiliary'))
        control_layout.addWidget(test_aux_btn)
        
        control_layout.addWidget(QWidget())  # Spacer
        
        clear_btn = QPushButton("Clear Selection")
        clear_btn.clicked.connect(self.clear_selection)
        control_layout.addWidget(clear_btn)
        
        control_layout.addStretch()
        
        main_layout.addWidget(control_panel)
        
        # Create inspector
        self.inspector = ComponentInspector()
        main_layout.addWidget(self.inspector)
        
        # Connect inspector signals
        self.inspector.component_modified.connect(self.on_component_modified)
        self.inspector.property_changed.connect(self.on_property_changed)
        
        # Status bar
        self.statusBar().showMessage("Ready - Load a model or test individual components")
        
        # Store test data
        self.test_model = None
        self.test_components = {}
        
    def load_test_model(self):
        """Load the integrated test model."""
        try:
            loader = YAMLModelLoader()
            
            # Try to load the integrated model
            model_path = Path(__file__).parent.parent.parent / "integrated_model_structure.yaml"
            scenario_path = Path(__file__).parent.parent.parent / "integrated_scenario_parameters.yaml"
            
            if model_path.exists():
                # Load existing model
                self.test_model, _ = loader.load_model_from_file(
                    str(model_path), 
                    str(scenario_path) if scenario_path.exists() else None
                )
                
                # Set model in inspector
                self.inspector.set_model(self.test_model)
                
                self.statusBar().showMessage(
                    f"✅ Model loaded: {self.test_model.name} "
                    f"({len(self.test_model.components)} components)"
                )
                
                # Select first component for testing
                if self.test_model.components:
                    first_component = next(iter(self.test_model.components.values()))
                    self.inspector.set_component(first_component)
                    self.statusBar().showMessage(f"Selected: {first_component.name}")
                    
            else:
                self.statusBar().showMessage(f"❌ Model file not found: {model_path}")
                
        except Exception as e:
            self.statusBar().showMessage(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            
    def test_component(self, component_type: str):
        """Test inspector with a specific component type."""
        try:
            # Create test component
            template = create_component_template(component_type, f"Test_{component_type.title()}")
            
            # Add some test properties
            if component_type == 'stock':
                template['initial_value'] = 1000
                template['spatial_dims'] = ['age_group', 'gender']
                template['min_value'] = 0
                template['description'] = "A test stock component with multidimensional data"
                
            elif component_type == 'flow':
                template['rate'] = 0.05
                template['spatial_dims'] = ['age_group', 'gender']
                template['parameters'] = {'growth_rate': 0.02, 'base_rate': 0.03}
                template['description'] = "A test flow component with parameters"
                
            elif component_type == 'calculator':
                template['expression'] = "Stock_A + Stock_B * 0.5"
                template['spatial_dims'] = ['region']
                template['dependencies'] = ['Stock_A', 'Stock_B']
                template['description'] = "A test calculator with expression and dependencies"
                
            elif component_type == 'auxiliary':
                template['value'] = 42.5
                template['description'] = "A test auxiliary component"
                
            # Create ModelComponent
            component = ModelComponent(
                name=template['name'],
                component_type=component_type,
                properties=template
            )
            
            # Store for reference
            self.test_components[component_type] = component
            
            # Create minimal test model if needed
            if not self.test_model:
                self.test_model = GuiModel("Test Model", "A test model for inspector functionality")
                self.test_model.dimensions = {
                    'age_group': {
                        'size': 3,
                        'labels': ['young', 'adult', 'elderly'],
                        'description': 'Age groups'
                    },
                    'gender': {
                        'size': 2,
                        'labels': ['male', 'female'],
                        'description': 'Gender categories'
                    },
                    'region': {
                        'size': 2,
                        'labels': ['urban', 'rural'],
                        'description': 'Geographic regions'
                    }
                }
                self.inspector.set_model(self.test_model)
                
            # Add component to model
            self.test_model.add_component(component)
            
            # Set component in inspector
            self.inspector.set_component(component)
            
            self.statusBar().showMessage(f"Testing {component_type}: {component.name}")
            
        except Exception as e:
            self.statusBar().showMessage(f"❌ Error creating test component: {e}")
            import traceback
            traceback.print_exc()
            
    def clear_selection(self):
        """Clear component selection."""
        self.inspector.set_component(None)
        self.statusBar().showMessage("Selection cleared")
        
    def on_component_modified(self, component):
        """Handle component modification."""
        self.statusBar().showMessage(f"Component modified: {component.name}")
        
    def on_property_changed(self, component_name, property_name, new_value):
        """Handle property changes."""
        self.statusBar().showMessage(f"Property changed: {component_name}.{property_name} = {new_value}")


def test_inspector_basic():
    """Test basic inspector functionality."""
    print("Testing basic inspector functionality...")
    
    try:
        app = QApplication(sys.argv)
        
        # Create inspector
        inspector = ComponentInspector()
        
        print("✅ Inspector widget created successfully")
        
        # Test with empty state
        inspector.set_component(None)
        print("✅ Empty state handled correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Inspector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run inspector tests."""
    print("System Dynamics GUI - Component Inspector Test")
    print("=" * 50)
    
    # Test basic functionality first
    if not test_inspector_basic():
        print("❌ Basic inspector test failed!")
        return 1
        
    # Run interactive test
    print("\n🔍 Starting interactive inspector test...")
    print("Instructions:")
    print("1. Click 'Load Test Model' to load the integrated model")
    print("2. Or click individual component test buttons")
    print("3. Edit properties in the Properties tab")
    print("4. View multidimensional data in the Data tab")
    print("5. Check connections in the Connections tab")
    print("6. Try switching between Design and Runtime modes")
    
    app = QApplication(sys.argv)
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    window = InspectorTestWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
