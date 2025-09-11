#!/usr/bin/env python3
"""
Debug test to see exactly what happens when a component is double-clicked.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import Qt

# Import the correct classes
from yaml_integration.yaml_loader import ModelComponent
from canvas.graphics_items import StockItem

class DebugComponentClickTest(QMainWindow):
    """Debug test for component clicking."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Debug Component Click Test")
        self.setGeometry(100, 100, 600, 500)
        
        # Store references to prevent garbage collection
        self.test_component = None
        self.stock_item = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Debug Component Click Test")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title_label)
        
        # Test button
        test_btn = QPushButton("Simulate Component Double-Click")
        test_btn.clicked.connect(self.simulate_double_click)
        layout.addWidget(test_btn)
        
        # Log area
        self.log_area = QTextEdit()
        layout.addWidget(self.log_area)
        
        self.log("Ready to test component double-click simulation...")
        
    def log(self, message):
        """Add a message to the log area."""
        self.log_area.append(message)
        print(message)
        
    def simulate_double_click(self):
        """Simulate what happens when a component is double-clicked."""
        
        self.log("🔍 Starting component double-click simulation...")
        
        try:
            # Step 1: Create a test component
            self.log("1. Creating test component...")
            self.test_component = ModelComponent(
                name="debug_stock",
                component_type="stock",
                properties={
                    'initial_value': 100,
                    'units': 'units',
                    'spatial_dims': ['parcel', 'time'],
                    'description': 'Debug test stock component'
                }
            )
            self.log(f"   ✅ Component created: {self.test_component.name}")
            
            # Step 2: Create a graphics item
            self.log("2. Creating graphics item...")
            self.stock_item = StockItem(self.test_component)
            self.log("   ✅ Graphics item created")
            
            # Step 3: Create a mock scene with model
            self.log("3. Creating mock scene...")
            from PyQt6.QtWidgets import QGraphicsScene
            
            scene = QGraphicsScene()
            
            # Add mock model to scene
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
                            'labels': [str(year) for year in range(2020, 2026)],
                            'description': 'Annual time steps',
                            'type': 'temporal',
                            'size': 6
                        }
                    }
            
            scene.gui_model = MockGuiModel()
            scene.addItem(self.stock_item)
            self.log("   ✅ Mock scene created with gui_model")
            
            # Step 4: Simulate the double-click
            self.log("4. Simulating double-click...")
            self.log("   Calling open_multidimensional_editor()...")
            
            # This should trigger all the debug output we added
            self.stock_item.open_multidimensional_editor()
            
            self.log("🎉 Double-click simulation completed!")
            
        except Exception as e:
            self.log(f"❌ Error during simulation: {e}")
            import traceback
            error_details = traceback.format_exc()
            self.log(f"Error details:\n{error_details}")

def main():
    """Main test function."""
    
    print("Debug Component Click Test")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = DebugComponentClickTest()
    test_window.show()
    
    print("Test window opened. Click the button to simulate component double-click.")
    print("Watch the console and log area for detailed debug output.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
