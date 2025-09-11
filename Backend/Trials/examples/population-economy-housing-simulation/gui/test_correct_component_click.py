#!/usr/bin/env python3
"""
Test component clicking with the correct ModelComponent import.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import Qt

# Import the correct ModelComponent
from yaml_integration.yaml_loader import ModelComponent

class CorrectComponentTestWindow(QMainWindow):
    """Test window using the correct ModelComponent."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Correct Component Click Test")
        self.setGeometry(100, 100, 500, 400)
        
        # Create test component using the correct class
        self.test_component = ModelComponent(
            name="test_stock",
            component_type="stock",
            properties={
                'initial_value': 100,
                'units': 'units',
                'spatial_dims': ['parcel', 'time'],
                'description': 'Test stock component'
            }
        )
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Correct Component Click Test")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title_label)
        
        # Component info
        comp_info = QLabel(f"Component: {self.test_component.name} ({self.test_component.component_type})")
        layout.addWidget(comp_info)
        
        # Test button
        test_btn = QPushButton("Test Spreadsheet Editor Opening")
        test_btn.clicked.connect(self.test_editor_opening)
        layout.addWidget(test_btn)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(200)
        layout.addWidget(self.log_area)
        
        self.log("Ready to test with correct ModelComponent...")
        
    def log(self, message):
        """Add a message to the log area."""
        self.log_area.append(message)
        print(message)
        
    def test_editor_opening(self):
        """Test opening the spreadsheet editor."""
        
        self.log("🚀 Testing spreadsheet editor opening...")
        
        try:
            self.log("1. Importing SpreadsheetDataEditor...")
            from inspector.spreadsheet_editor import SpreadsheetDataEditor
            self.log("   ✅ Import successful")
            
            self.log("2. Creating mock model...")
            # Create a mock model with dimensions
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
            
            mock_model = MockModel()
            self.log("   ✅ Mock model created")
            
            self.log("3. Creating SpreadsheetDataEditor...")
            editor = SpreadsheetDataEditor([self.test_component], mock_model, parent=self)
            self.log("   ✅ Editor created successfully")
            
            self.log("4. Showing editor window...")
            editor.show()
            self.log("   ✅ Editor window shown")
            
            self.log("🎉 SUCCESS: Spreadsheet editor opened successfully!")
            self.log("The component clicking should now work in the main GUI.")
            
            # Connect to modification signal
            editor.component_modified.connect(self.on_component_modified)
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            import traceback
            error_details = traceback.format_exc()
            self.log(f"Error details:\n{error_details}")
            
    def on_component_modified(self, component):
        """Handle component modification."""
        self.log(f"📝 Component {component.name} was modified!")

def main():
    """Main test function."""
    
    print("Correct Component Click Test")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = CorrectComponentTestWindow()
    test_window.show()
    
    print("Test window opened. Click the button to test editor opening.")
    print("This uses the correct ModelComponent from yaml_integration.yaml_loader")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
