#!/usr/bin/env python3
"""
Simple test to verify connection functionality is working.
"""

import sys
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPointF

from canvas.model_canvas import ModelCanvas
from yaml_integration.yaml_loader import GuiModel


def test_connection_creation():
    """Test programmatic connection creation."""
    
    print("🧪 Testing Connection Creation")
    print("=" * 40)
    
    # Create application
    app = QApplication.instance() or QApplication([])
    
    # Create canvas and model
    canvas = ModelCanvas()
    gui_model = GuiModel("Test Model", "Connection test model")
    canvas.load_model(gui_model)
    
    print("✅ Created canvas and model")
    
    # Create test components
    canvas.create_new_component('flow', QPointF(-100, 0))
    canvas.create_new_component('stock', QPointF(100, 0))
    canvas.create_new_component('calculator', QPointF(0, 100))
    
    print(f"✅ Created {len(gui_model.components)} components")
    
    # Get component items
    component_items = list(canvas.component_items.values())
    flow_item = component_items[0]  # Should be flow
    stock_item = component_items[1]  # Should be stock
    calc_item = component_items[2]   # Should be calculator
    
    print(f"Components: {[item.component.name for item in component_items]}")
    
    # Test valid connections
    print("\n🔗 Testing valid connections...")
    
    # Test 1: Flow -> Stock (should create inflow)
    initial_connections = len(gui_model.connections)
    canvas.create_connection(flow_item, stock_item)
    new_connections = len(gui_model.connections)
    
    if new_connections > initial_connections:
        print("✅ Flow -> Stock connection created successfully")
        print(f"   Connection: {gui_model.connections[-1]}")
    else:
        print("❌ Flow -> Stock connection failed")
    
    # Test 2: Stock -> Calculator (should create dependency)
    initial_connections = len(gui_model.connections)
    canvas.create_connection(stock_item, calc_item)
    new_connections = len(gui_model.connections)
    
    if new_connections > initial_connections:
        print("✅ Stock -> Calculator connection created successfully")
        print(f"   Connection: {gui_model.connections[-1]}")
    else:
        print("❌ Stock -> Calculator connection failed")
    
    # Test 3: Calculator -> Flow (should create dependency)
    initial_connections = len(gui_model.connections)
    canvas.create_connection(calc_item, flow_item)
    new_connections = len(gui_model.connections)
    
    if new_connections > initial_connections:
        print("✅ Calculator -> Flow connection created successfully")
        print(f"   Connection: {gui_model.connections[-1]}")
    else:
        print("❌ Calculator -> Flow connection failed")
    
    print(f"\n📊 Total connections created: {len(gui_model.connections)}")
    print(f"📊 Total visual connections: {len(canvas.connection_items)}")
    
    # Test invalid connection (should show warning but not create connection)
    print("\n⚠️ Testing invalid connection (Stock -> Stock)...")
    initial_connections = len(gui_model.connections)
    
    # Create another stock for testing invalid connection
    canvas.create_new_component('stock', QPointF(200, 0))
    stock2_item = list(canvas.component_items.values())[-1]
    
    # This should show a warning and not create a connection
    canvas.create_connection(stock_item, stock2_item)
    new_connections = len(gui_model.connections)
    
    if new_connections == initial_connections:
        print("✅ Invalid connection correctly rejected")
    else:
        print("❌ Invalid connection was created (should not happen)")
    
    print(f"\n🎯 Final Results:")
    print(f"   Components: {len(gui_model.components)}")
    print(f"   Connections: {len(gui_model.connections)}")
    print(f"   Visual items: {len(canvas.connection_items)}")
    
    # Verify visual connections match model connections
    if len(gui_model.connections) == len(canvas.connection_items):
        print("✅ Visual connections match model connections")
    else:
        print("❌ Visual connections don't match model connections")
        
    return len(gui_model.connections) > 0


def main():
    """Run the connection test."""
    
    success = test_connection_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Connection functionality is working!")
        print("\nManual test instructions:")
        print("1. Run: python main.py")
        print("2. Create or load a model")
        print("3. Add some components to the canvas")
        print("4. Hold Ctrl and click on a component")
        print("5. Drag to another component and release")
        print("6. You should see a connection created (no popup message)")
    else:
        print("❌ Connection functionality has issues")
        
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 