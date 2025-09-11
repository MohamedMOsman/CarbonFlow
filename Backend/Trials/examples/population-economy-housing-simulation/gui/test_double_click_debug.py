#!/usr/bin/env python3
"""
Debug script to test double-click functionality on components.
"""

import sys
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent

# Import the graphics items
from canvas.graphics_items import StockItem

# Import sd_toolkit components
try:
    from sd_toolkit.models.model_component import ModelComponent
    SD_TOOLKIT_AVAILABLE = True
except ImportError:
    SD_TOOLKIT_AVAILABLE = False
    # Create a mock component class
    class ModelComponent:
        def __init__(self, name, component_type):
            self.name = name
            self.component_type = component_type
            self.properties = {
                'spatial_dims': ['parcel', 'time'],
                'description': f'Mock {component_type} component',
                'units': 'units',
                'initial_value': 0
            }

class DoubleClickTestWindow(QMainWindow):
    """Test window to debug double-click functionality."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Double-Click Debug Test")
        self.setGeometry(100, 100, 600, 400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create graphics view and scene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)
        
        # Create a test component
        test_component = ModelComponent("test_stock", "stock")
        
        # Create a stock item
        self.stock_item = StockItem(test_component)
        self.stock_item.setPos(100, 100)
        
        # Add custom double-click handler for debugging
        original_double_click = self.stock_item.mouseDoubleClickEvent
        
        def debug_double_click(event):
            print("🔍 Double-click detected!")
            print(f"   Button: {event.button()}")
            print(f"   Position: {event.pos()}")
            print(f"   Component: {self.stock_item.component.name}")
            print("   Calling original handler...")
            
            try:
                result = original_double_click(event)
                print("   ✅ Original handler completed successfully")
                return result
            except Exception as e:
                print(f"   ❌ Error in original handler: {e}")
                import traceback
                traceback.print_exc()
                raise
        
        self.stock_item.mouseDoubleClickEvent = debug_double_click
        
        # Add to scene
        self.scene.addItem(self.stock_item)
        
        print("Double-Click Debug Test Setup Complete")
        print("=" * 50)
        print("Instructions:")
        print("1. Double-click on the rectangular component in the graphics view")
        print("2. Check the console output for debug information")
        print("3. The spreadsheet editor should open if everything works")
        print("=" * 50)

def main():
    """Main test function."""
    
    print("Double-Click Debug Test")
    print("=" * 30)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = DoubleClickTestWindow()
    test_window.show()
    
    print("Test window opened. Double-click the component to test.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
