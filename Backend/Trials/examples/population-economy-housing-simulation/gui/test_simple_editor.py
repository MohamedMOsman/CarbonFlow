#!/usr/bin/env python3
"""
Simple test for the spreadsheet editor to identify any remaining issues.
"""

import sys
from PyQt6.QtWidgets import QApplication

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
                'labels': ['2020', '2021', '2022'],
                'description': 'Time periods',
                'type': 'temporal',
                'size': 3
            }
        }

def test_editor():
    """Test the spreadsheet editor with minimal setup."""
    
    print("Testing Spreadsheet Editor...")
    
    try:
        # Create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Import the editor
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        
        # Create mock data
        component = MockComponent("test_stock", "stock")
        model = MockModel()
        
        print("✅ Creating editor...")
        
        # Create editor
        editor = SpreadsheetDataEditor([component], model)
        
        print("✅ Editor created successfully!")
        print("✅ Showing editor window...")
        
        # Show editor
        editor.show()
        
        print("✅ Editor window shown!")
        print("✅ Test completed successfully!")
        
        # Don't start the event loop in test mode
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_editor()
    if success:
        print("\n🎉 Spreadsheet editor test passed!")
    else:
        print("\n❌ Spreadsheet editor test failed!")
    
    sys.exit(0 if success else 1)
