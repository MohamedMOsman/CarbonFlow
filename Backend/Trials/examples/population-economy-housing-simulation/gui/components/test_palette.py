#!/usr/bin/env python3
"""
Test script for the component palette functionality.

This script tests the component palette and drag-and-drop functionality.
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt

from palette import ComponentPalette
from component_types import COMPONENT_DEFINITIONS, get_component_type, validate_component_properties
from canvas.model_canvas import ModelCanvas
from yaml_integration.yaml_loader import YAMLModelLoader, GuiModel


class PaletteTestWindow(QMainWindow):
    """Test window for the component palette."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Component Palette Test")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create palette
        self.palette = ComponentPalette()
        main_layout.addWidget(self.palette)
        
        # Create canvas area
        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout(canvas_widget)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        load_button = QPushButton("Load Test Model")
        load_button.clicked.connect(self.load_test_model)
        button_layout.addWidget(load_button)
        
        clear_button = QPushButton("Clear Canvas")
        clear_button.clicked.connect(self.clear_canvas)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        canvas_layout.addLayout(button_layout)
        
        # Create canvas
        self.canvas = ModelCanvas()
        canvas_layout.addWidget(self.canvas)
        
        main_layout.addWidget(canvas_widget)
        
        # Connect signals
        self.canvas.component_selected.connect(self.on_component_selected)
        self.canvas.model_modified.connect(self.on_model_modified)
        
        # Status bar
        self.statusBar().showMessage("Ready - Drag components from palette to canvas")
        
        # Store model data
        self.gui_model = None
        
    def load_test_model(self):
        """Load a test model or create an empty one."""
        try:
            loader = YAMLModelLoader()
            
            # Try to load the integrated model
            model_path = Path(__file__).parent.parent.parent / "integrated_model_structure.yaml"
            scenario_path = Path(__file__).parent.parent.parent / "integrated_scenario_parameters.yaml"
            
            if model_path.exists():
                # Load existing model
                self.gui_model, _ = loader.load_model_from_file(
                    str(model_path), 
                    str(scenario_path) if scenario_path.exists() else None
                )
                self.statusBar().showMessage(f"✅ Loaded existing model: {self.gui_model.name}")
            else:
                # Create empty model
                self.gui_model = GuiModel("Test Model", "A test model for palette functionality")
                self.statusBar().showMessage("✅ Created empty test model")
                
            # Load into canvas
            self.canvas.load_model(self.gui_model)
            
        except Exception as e:
            self.statusBar().showMessage(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
    def clear_canvas(self):
        """Clear the canvas."""
        if self.canvas:
            self.canvas.clear_canvas()
            self.statusBar().showMessage("Canvas cleared")
            
    def on_component_selected(self, component):
        """Handle component selection."""
        self.statusBar().showMessage(f"Selected: {component.name} ({component.component_type})")
        
    def on_model_modified(self):
        """Handle model modification."""
        if self.gui_model:
            count = len(self.gui_model.components)
            self.statusBar().showMessage(f"Model modified - {count} components")


def test_component_types():
    """Test component type definitions."""
    print("Testing component type definitions...")
    
    try:
        # Test all component types
        for type_name, comp_type in COMPONENT_DEFINITIONS.items():
            print(f"✅ {comp_type.display_name}: {comp_type.description}")
            
            # Test default properties
            if comp_type.default_properties:
                validation = validate_component_properties(type_name, comp_type.default_properties)
                if validation['valid']:
                    print(f"   ✅ Default properties valid")
                else:
                    print(f"   ❌ Default properties invalid: {validation['errors']}")
                    
        return True
        
    except Exception as e:
        print(f"❌ Component type test failed: {e}")
        return False


def test_palette_creation():
    """Test palette widget creation."""
    print("\nTesting palette widget creation...")
    
    try:
        app = QApplication(sys.argv)
        
        # Create palette
        palette = ComponentPalette()
        
        print("✅ Palette widget created successfully")
        
        # Test component creation
        for comp_type in ['stock', 'flow', 'calculator']:
            component = palette.create_default_component(comp_type, f"Test_{comp_type}")
            print(f"✅ Created default {comp_type}: {component.name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Palette creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run palette tests."""
    print("System Dynamics GUI - Component Palette Test")
    print("=" * 50)
    
    # Test component types
    if not test_component_types():
        print("❌ Component type tests failed!")
        return 1
        
    # Test palette creation
    if not test_palette_creation():
        print("❌ Palette creation tests failed!")
        return 1
        
    # Run interactive test
    print("\n🎨 Starting interactive palette test...")
    print("Instructions:")
    print("1. Click 'Load Test Model' to load a model or create empty one")
    print("2. Drag components from the left palette to the canvas")
    print("3. Try creating different component types")
    print("4. Select components to see their properties")
    print("5. Try creating connections between components")
    
    app = QApplication(sys.argv)
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    window = PaletteTestWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
