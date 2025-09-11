#!/usr/bin/env python3
"""
Test script to debug component clicking and editor opening.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

# Mock component class
class MockComponent:
    def __init__(self, name, component_type):
        self.name = name
        self.component_type = component_type
        self.properties = {
            'spatial_dims': ['parcel', 'time'],
            'description': f'Mock {component_type} component',
            'units': 'units',
            'initial_value': 0
        }

# Mock model class
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

class ComponentClickTestWindow(QMainWindow):
    """Test window to simulate component clicking."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Component Click Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create mock data
        self.mock_component = MockComponent("test_stock", "stock")
        self.mock_model = MockModel()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Info label
        info_label = QLabel("Click the button to simulate double-clicking a component:")
        layout.addWidget(info_label)
        
        # Test button
        test_btn = QPushButton("Simulate Component Double-Click")
        test_btn.clicked.connect(self.simulate_component_click)
        layout.addWidget(test_btn)
        
        # Status label
        self.status_label = QLabel("Ready to test...")
        layout.addWidget(self.status_label)
        
    def simulate_component_click(self):
        """Simulate what happens when a component is double-clicked."""
        
        self.status_label.setText("Testing component click...")
        
        try:
            # This simulates the open_multidimensional_editor method
            self.status_label.setText("Importing spreadsheet editor...")
            
            from inspector.spreadsheet_editor import SpreadsheetDataEditor
            
            self.status_label.setText("Creating editor with mock data...")
            
            # Create editor with mock data
            editor = SpreadsheetDataEditor([self.mock_component], self.mock_model, parent=self)
            
            self.status_label.setText("Showing editor window...")
            
            # Show the editor
            editor.show()
            
            self.status_label.setText("✅ Editor opened successfully!")
            
            # Connect to modification signal
            editor.component_modified.connect(self.on_component_modified)
            
        except ImportError as e:
            self.status_label.setText(f"❌ Import Error: {e}")
            print(f"Import Error: {e}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error: {e}")
            print(f"Error opening editor: {e}")
            import traceback
            traceback.print_exc()
            
    def on_component_modified(self, component):
        """Handle component modification."""
        self.status_label.setText(f"Component {component.name} was modified!")

def main():
    """Main test function."""
    
    print("Component Click Test")
    print("=" * 30)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = ComponentClickTestWindow()
    test_window.show()
    
    print("Test window opened. Click the button to test component clicking.")
    print("This simulates what happens when you double-click a component in the GUI.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
