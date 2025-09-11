#!/usr/bin/env python3
"""
Test script for the model canvas functionality.

This script tests the visual model editor canvas with the integrated model.
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

from model_canvas import ModelCanvas
from yaml_integration.yaml_loader import YAMLModelLoader


class CanvasTestWindow(QMainWindow):
    """Test window for the model canvas."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Model Canvas Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create button bar
        button_layout = QHBoxLayout()
        
        load_button = QPushButton("Load Test Model")
        load_button.clicked.connect(self.load_test_model)
        button_layout.addWidget(load_button)
        
        clear_button = QPushButton("Clear Canvas")
        clear_button.clicked.connect(self.clear_canvas)
        button_layout.addWidget(clear_button)
        
        fit_button = QPushButton("Fit to Content")
        fit_button.clicked.connect(self.fit_to_content)
        button_layout.addWidget(fit_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Create canvas
        self.canvas = ModelCanvas()
        layout.addWidget(self.canvas)
        
        # Connect canvas signals
        self.canvas.component_selected.connect(self.on_component_selected)
        self.canvas.connection_created.connect(self.on_connection_created)
        self.canvas.model_modified.connect(self.on_model_modified)
        
        # Status bar
        self.statusBar().showMessage("Ready - Load a model to test the canvas")
        
        # Store model data
        self.gui_model = None
        self.sd_model = None
        
    def load_test_model(self):
        """Load the integrated test model."""
        try:
            loader = YAMLModelLoader()
            
            # Paths to test files
            model_path = Path(__file__).parent.parent.parent / "integrated_model_structure.yaml"
            scenario_path = Path(__file__).parent.parent.parent / "integrated_scenario_parameters.yaml"
            
            if not model_path.exists():
                self.statusBar().showMessage(f"❌ Model file not found: {model_path}")
                return
                
            if not scenario_path.exists():
                self.statusBar().showMessage(f"⚠️ Scenario file not found, loading model only")
                scenario_path = None
                
            # Load the model
            self.gui_model, self.sd_model = loader.load_model_from_file(
                str(model_path), 
                str(scenario_path) if scenario_path else None
            )
            
            # Load into canvas
            self.canvas.load_model(self.gui_model)
            
            self.statusBar().showMessage(
                f"✅ Model loaded: {self.gui_model.name} "
                f"({len(self.gui_model.components)} components, "
                f"{len(self.gui_model.connections)} connections)"
            )
            
        except Exception as e:
            self.statusBar().showMessage(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            
    def clear_canvas(self):
        """Clear the canvas."""
        self.canvas.clear_canvas()
        self.statusBar().showMessage("Canvas cleared")
        
    def fit_to_content(self):
        """Fit canvas view to content."""
        self.canvas.fit_to_content()
        self.statusBar().showMessage("View fitted to content")
        
    def on_component_selected(self, component):
        """Handle component selection."""
        dims = component.properties.get('spatial_dims', [])
        dims_str = f" [{', '.join(dims)}]" if dims else ""
        units = component.properties.get('units', '')
        units_str = f" ({units})" if units else ""
        
        self.statusBar().showMessage(
            f"Selected: {component.name} ({component.component_type}){dims_str}{units_str}"
        )
        
    def on_connection_created(self, from_name, to_name, conn_type):
        """Handle connection creation."""
        self.statusBar().showMessage(f"Connection created: {from_name} → {to_name} ({conn_type})")
        
    def on_model_modified(self):
        """Handle model modification."""
        self.statusBar().showMessage("Model modified")


def test_canvas_basic():
    """Test basic canvas functionality without loading a model."""
    print("Testing basic canvas functionality...")
    
    try:
        app = QApplication(sys.argv)
        
        # Create canvas
        canvas = ModelCanvas()
        
        print("✅ Canvas created successfully")
        
        # Test basic methods
        canvas.clear_canvas()
        canvas.fit_to_content()
        zoom_level = canvas.get_zoom_level()
        canvas.set_zoom_level(1.5)
        canvas.set_zoom_level(zoom_level)  # Reset
        
        print("✅ Basic canvas methods work")
        
        return True
        
    except Exception as e:
        print(f"❌ Canvas test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run canvas tests."""
    print("System Dynamics GUI - Canvas Test")
    print("=" * 50)
    
    # Test basic functionality first
    if not test_canvas_basic():
        print("❌ Basic canvas test failed!")
        return 1
        
    # Run interactive test
    print("\n🎨 Starting interactive canvas test...")
    print("Instructions:")
    print("1. Click 'Load Test Model' to load the integrated model")
    print("2. Try zooming with mouse wheel")
    print("3. Try selecting components by clicking")
    print("4. Try creating connections with Ctrl+Click and drag")
    print("5. Right-click for context menu")
    
    app = QApplication(sys.argv)
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    window = CanvasTestWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
