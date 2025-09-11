#!/usr/bin/env python3
"""
Final test to verify component double-click functionality works correctly.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QLabel
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QMouseEvent

# Import the correct classes
from yaml_integration.yaml_loader import ModelComponent
from canvas.graphics_items import StockItem

class FinalComponentClickTest(QMainWindow):
    """Final test window to verify component clicking works."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Final Component Click Test")
        self.setGeometry(100, 100, 700, 500)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Instructions
        instructions = QLabel("""
Final Component Click Test

Instructions:
1. Double-click on the blue rectangular component below
2. The spreadsheet editor should open automatically
3. If it works, the component clicking issue is resolved!

Note: This test uses the correct ModelComponent from yaml_integration.yaml_loader
        """)
        instructions.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(instructions)
        
        # Create graphics view and scene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setMinimumHeight(300)
        layout.addWidget(self.view)
        
        # Create a test component with the correct class
        test_component = ModelComponent(
            name="test_stock",
            component_type="stock",
            properties={
                'initial_value': 100,
                'units': 'people',
                'spatial_dims': ['parcel', 'time'],
                'description': 'Test stock component for double-click testing'
            }
        )
        
        # Create a stock item
        self.stock_item = StockItem(test_component)
        self.stock_item.setPos(200, 100)
        
        # Create a mock model for the scene
        class MockGuiModel:
            def __init__(self):
                self.dimensions = {
                    'parcel': {
                        'labels': ['1001', '1002', '1003'],
                        'description': 'Property parcel identifiers',
                        'type': 'categorical',
                        'size': 3
                    },
                    'time': {
                        'labels': [str(year) for year in range(2020, 2031)],
                        'description': 'Annual time steps',
                        'type': 'temporal',
                        'size': 11
                    }
                }
        
        # Add the mock model to the scene so the component can find it
        self.scene.gui_model = MockGuiModel()
        
        # Add to scene
        self.scene.addItem(self.stock_item)
        
        # Add some visual context
        self.scene.setSceneRect(0, 0, 500, 300)
        
        print("Final Component Click Test Setup Complete")
        print("=" * 50)
        print("✅ ModelComponent imported from yaml_integration.yaml_loader")
        print("✅ StockItem created with test component")
        print("✅ Mock GUI model attached to scene")
        print("✅ Component positioned in graphics view")
        print("\nDouble-click the blue rectangle to test the spreadsheet editor!")
        print("=" * 50)

def main():
    """Main test function."""
    
    print("Final Component Click Test")
    print("=" * 30)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = FinalComponentClickTest()
    test_window.show()
    
    print("Test window opened. Double-click the component to test!")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
