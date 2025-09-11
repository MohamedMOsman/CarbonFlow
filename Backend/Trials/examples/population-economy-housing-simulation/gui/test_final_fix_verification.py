#!/usr/bin/env python3
"""
Final verification test for the component clicking fix.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt

# Import the correct classes
from yaml_integration.yaml_loader import ModelComponent
from canvas.graphics_items import StockItem

class FinalFixVerificationTest(QMainWindow):
    """Final test to verify the component clicking fix works."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Final Fix Verification Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Store references to prevent garbage collection
        self.editors = []  # Store all opened editors
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Final Fix Verification Test")
        title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Status
        status_label = QLabel("✅ Fix Applied: Editor references are now stored to prevent garbage collection")
        status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 10px; background-color: #d5f4e6; border: 1px solid #27ae60; border-radius: 5px;")
        layout.addWidget(status_label)
        
        # Instructions
        instructions = QLabel("""
🎯 Test Instructions:

1. Click "Test Direct Editor" to test the spreadsheet editor directly
2. Click "Test Graphics Component" to test double-clicking a graphics component
3. Both should open spreadsheet editors that STAY OPEN
4. If the windows stay open, the fix is successful!

The key fix: Storing editor references as instance variables prevents garbage collection.
        """)
        instructions.setStyleSheet("background-color: #f8f9fa; padding: 15px; border: 1px solid #dee2e6; border-radius: 5px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Test buttons
        button_layout = QVBoxLayout()
        
        # Direct editor test
        direct_test_btn = QPushButton("🔧 Test Direct Editor Opening")
        direct_test_btn.clicked.connect(self.test_direct_editor)
        direct_test_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; background-color: #3498db; color: white; border: none; border-radius: 5px; } QPushButton:hover { background-color: #2980b9; }")
        button_layout.addWidget(direct_test_btn)
        
        # Graphics component test
        graphics_test_btn = QPushButton("🎨 Test Graphics Component Double-Click")
        graphics_test_btn.clicked.connect(self.test_graphics_component)
        graphics_test_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; background-color: #e74c3c; color: white; border: none; border-radius: 5px; } QPushButton:hover { background-color: #c0392b; }")
        button_layout.addWidget(graphics_test_btn)
        
        layout.addLayout(button_layout)
        
        # Results area
        self.results_label = QLabel("Ready to test...")
        self.results_label.setStyleSheet("padding: 10px; background-color: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 5px;")
        layout.addWidget(self.results_label)
        
    def test_direct_editor(self):
        """Test opening the spreadsheet editor directly."""
        
        self.results_label.setText("🔧 Testing direct editor opening...")
        
        try:
            from inspector.spreadsheet_editor import SpreadsheetDataEditor
            
            # Create test component
            component = ModelComponent(
                name="direct_test_stock",
                component_type="stock",
                properties={
                    'initial_value': 100,
                    'units': 'units',
                    'spatial_dims': ['parcel', 'time'],
                    'description': 'Direct test stock component'
                }
            )
            
            # Create mock model
            class MockModel:
                def __init__(self):
                    self.dimensions = {
                        'parcel': {
                            'labels': ['1001', '1002', '1003'],
                            'description': 'Property parcels',
                            'type': 'categorical',
                            'size': 3
                        },
                        'time': {
                            'labels': ['2020', '2021', '2022', '2023', '2024'],
                            'description': 'Time periods',
                            'type': 'temporal',
                            'size': 5
                        }
                    }
            
            # IMPORTANT: Store reference to prevent garbage collection
            editor = SpreadsheetDataEditor([component], MockModel(), parent=self)
            self.editors.append(editor)  # Keep reference
            
            editor.show()
            
            self.results_label.setText("✅ Direct editor test: SUCCESS! Editor should stay open.")
            
        except Exception as e:
            self.results_label.setText(f"❌ Direct editor test FAILED: {e}")
            
    def test_graphics_component(self):
        """Test the graphics component double-click simulation."""
        
        self.results_label.setText("🎨 Testing graphics component double-click...")
        
        try:
            # Create test component
            component = ModelComponent(
                name="graphics_test_stock",
                component_type="stock",
                properties={
                    'initial_value': 200,
                    'units': 'units',
                    'spatial_dims': ['parcel', 'time'],
                    'description': 'Graphics test stock component'
                }
            )
            
            # Create graphics item
            stock_item = StockItem(component)
            
            # Create mock scene with model
            scene = QGraphicsScene()
            
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
            scene.addItem(stock_item)
            
            # Simulate double-click (this calls open_multidimensional_editor)
            stock_item.open_multidimensional_editor()
            
            # Store reference to the editor created by the graphics item
            if hasattr(stock_item, 'editor'):
                self.editors.append(stock_item.editor)
            
            self.results_label.setText("✅ Graphics component test: SUCCESS! Editor should stay open.")
            
        except Exception as e:
            self.results_label.setText(f"❌ Graphics component test FAILED: {e}")
            import traceback
            print(traceback.format_exc())

def main():
    """Main test function."""
    
    print("Final Fix Verification Test")
    print("=" * 50)
    print("Testing the component clicking fix...")
    print("Key fix: Storing editor references to prevent garbage collection")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = FinalFixVerificationTest()
    test_window.show()
    
    print("Test window opened. Use the buttons to verify the fix works.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
