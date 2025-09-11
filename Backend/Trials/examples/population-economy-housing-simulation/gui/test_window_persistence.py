#!/usr/bin/env python3
"""
Test to verify that the spreadsheet editor window stays open.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

# Import the correct classes
from yaml_integration.yaml_loader import ModelComponent

class WindowPersistenceTest(QMainWindow):
    """Test window to verify editor persistence."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Window Persistence Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Store editor reference to prevent garbage collection
        self.editor = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Window Persistence Test")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel("""
This test verifies that the spreadsheet editor window stays open.

The key fix is storing the editor as an instance variable
to prevent garbage collection.
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Test button
        test_btn = QPushButton("Open Spreadsheet Editor (Should Stay Open)")
        test_btn.clicked.connect(self.open_persistent_editor)
        layout.addWidget(test_btn)
        
    def open_persistent_editor(self):
        """Open the spreadsheet editor with proper reference storage."""
        
        print("🚀 Opening persistent spreadsheet editor...")
        
        try:
            from inspector.spreadsheet_editor import SpreadsheetDataEditor
            
            # Create test component
            component = ModelComponent(
                name="persistent_test",
                component_type="stock",
                properties={
                    'initial_value': 100,
                    'units': 'units',
                    'spatial_dims': ['parcel', 'time'],
                    'description': 'Test component for persistence'
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
                            'labels': ['2020', '2021', '2022'],
                            'description': 'Time periods',
                            'type': 'temporal',
                            'size': 3
                        }
                    }
            
            mock_model = MockModel()
            
            # IMPORTANT: Store as instance variable to prevent garbage collection
            self.editor = SpreadsheetDataEditor([component], mock_model, parent=self)
            self.editor.show()
            
            print("✅ Editor created and shown with persistent reference")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main test function."""
    
    print("Window Persistence Test")
    print("=" * 30)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = WindowPersistenceTest()
    test_window.show()
    
    print("Test window opened. Click the button to test editor persistence.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
