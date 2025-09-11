#!/usr/bin/env python3
"""
Direct test of the spreadsheet editor opening functionality.
"""

import sys
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import Qt

# Import sd_toolkit components
try:
    from sd_toolkit.models.model_component import ModelComponent
    SD_TOOLKIT_AVAILABLE = True
    print("✅ sd_toolkit available")
except ImportError as e:
    print(f"❌ sd_toolkit not available: {e}")
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

class DirectEditorTestWindow(QMainWindow):
    """Test window to directly test editor opening."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Direct Editor Test")
        self.setGeometry(100, 100, 500, 400)
        
        # Create test component
        self.test_component = ModelComponent("test_stock", "stock")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Info
        info_label = QLabel("Direct Spreadsheet Editor Test")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(info_label)
        
        # Component info
        comp_info = QLabel(f"Test Component: {self.test_component.name} ({self.test_component.component_type})")
        layout.addWidget(comp_info)
        
        # Test button
        test_btn = QPushButton("Open Spreadsheet Editor")
        test_btn.clicked.connect(self.open_editor_directly)
        layout.addWidget(test_btn)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(200)
        layout.addWidget(self.log_area)
        
        self.log("Ready to test direct editor opening...")
        
    def log(self, message):
        """Add a message to the log area."""
        self.log_area.append(message)
        print(message)  # Also print to console
        
    def open_editor_directly(self):
        """Directly open the spreadsheet editor."""
        
        self.log("🚀 Starting direct editor test...")
        
        try:
            self.log("1. Importing SpreadsheetDataEditor...")
            from inspector.spreadsheet_editor import SpreadsheetDataEditor
            self.log("   ✅ Import successful")
            
            self.log("2. Creating mock model...")
            # Create a simple mock model
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
            
            # Connect to modification signal
            editor.component_modified.connect(self.on_component_modified)
            
        except ImportError as e:
            self.log(f"❌ Import Error: {e}")
            
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
    
    print("Direct Editor Test")
    print("=" * 30)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = DirectEditorTestWindow()
    test_window.show()
    
    print("Test window opened. Click the button to test direct editor opening.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
