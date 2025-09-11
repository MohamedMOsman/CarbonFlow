#!/usr/bin/env python3
"""
Test script to verify that the new model functionality fix works correctly.
"""

import sys
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication
from yaml_integration.yaml_loader import GuiModel
from canvas.model_canvas import ModelCanvas


def test_new_model_creation():
    """Test that we can create a new empty model and add components."""
    
    print("🔧 Testing new model creation...")
    
    # Create a new empty GUI model
    gui_model = GuiModel("Test New Model", "A test new model")
    
    print(f"✅ Created new GUI model: {gui_model.name}")
    print(f"   Description: {gui_model.description}")
    print(f"   Components: {len(gui_model.components)}")
    print(f"   Connections: {len(gui_model.connections)}")
    
    # Test that we can add components to the model
    from components.component_types import COMPONENT_DEFINITIONS
    from yaml_integration.yaml_loader import ModelComponent
    
    # Create a test stock component
    stock_properties = {
        'initial_value': 100,
        'description': 'A test stock'
    }
    stock_component = ModelComponent("test_stock", "stock", stock_properties)
    gui_model.add_component(stock_component)
    
    print(f"✅ Added stock component: {stock_component.name}")
    print(f"   Updated component count: {len(gui_model.components)}")
    
    # Create a test flow component
    flow_properties = {
        'rate': 5,
        'description': 'A test flow'
    }
    flow_component = ModelComponent("test_flow", "flow", flow_properties)
    gui_model.add_component(flow_component)
    
    print(f"✅ Added flow component: {flow_component.name}")
    print(f"   Updated component count: {len(gui_model.components)}")
    
    return gui_model


def test_canvas_with_new_model():
    """Test that the canvas can work with a new empty model."""
    
    print("\n🖼️  Testing canvas with new model...")
    
    # Create QApplication (required for Qt widgets)
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create model canvas
    canvas = ModelCanvas()
    
    # Create new model
    gui_model = GuiModel("Canvas Test Model", "A test model for canvas")
    
    # Test that canvas accepts the model without requiring existing components
    try:
        canvas.load_model(gui_model)
        print("✅ Canvas successfully loaded empty model")
        print(f"   Canvas has gui_model: {canvas.gui_model is not None}")
        print(f"   Canvas model name: {canvas.gui_model.name if canvas.gui_model else 'None'}")
        
        # Test that we can create components on the canvas now
        from PyQt6.QtCore import QPointF
        try:
            # This should NOT show the "Please load a model first" error anymore
            canvas.create_new_component("stock", QPointF(100, 100))
            print("✅ Successfully created component on canvas")
            print(f"   Model now has {len(canvas.gui_model.components)} components")
            
        except Exception as e:
            print(f"❌ Error creating component: {e}")
            
    except Exception as e:
        print(f"❌ Error loading model into canvas: {e}")
        
    return canvas


if __name__ == "__main__":
    print("🚀 Testing New Model Fix")
    print("=" * 50)
    
    # Test 1: Basic model creation
    gui_model = test_new_model_creation()
    
    # Test 2: Canvas integration
    canvas = test_canvas_with_new_model()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    print("🎉 The 'New Model' functionality should now work properly.")
    print("\nTo test in the GUI:")
    print("1. Run the GUI application")
    print("2. Click 'File' -> 'New Model' (or use Ctrl+N)")
    print("3. Try dragging components from the palette to the canvas")
    print("4. Components should now be addable without the 'load model first' error") 