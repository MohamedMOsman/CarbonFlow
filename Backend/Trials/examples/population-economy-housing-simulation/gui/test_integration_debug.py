#!/usr/bin/env python3
"""
Comprehensive integration test to debug component clicking issues.
"""

import sys
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QHBoxLayout
from PyQt6.QtCore import Qt

def test_all_integrations():
    """Test all integration points."""
    
    print("Integration Debug Test")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Import sd_toolkit
    print("1. Testing sd_toolkit import...")
    try:
        from sd_toolkit.models.model_component import ModelComponent
        results['sd_toolkit'] = True
        print("   ✅ sd_toolkit imported successfully")
    except ImportError as e:
        results['sd_toolkit'] = False
        print(f"   ❌ sd_toolkit import failed: {e}")
        # Create mock
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
    
    # Test 2: Import graphics items
    print("2. Testing graphics items import...")
    try:
        from canvas.graphics_items import StockItem, FlowItem
        results['graphics_items'] = True
        print("   ✅ Graphics items imported successfully")
    except ImportError as e:
        results['graphics_items'] = False
        print(f"   ❌ Graphics items import failed: {e}")
    
    # Test 3: Import spreadsheet editor
    print("3. Testing spreadsheet editor import...")
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        results['spreadsheet_editor'] = True
        print("   ✅ Spreadsheet editor imported successfully")
    except ImportError as e:
        results['spreadsheet_editor'] = False
        print(f"   ❌ Spreadsheet editor import failed: {e}")
    
    # Test 4: Import component inspector
    print("4. Testing component inspector import...")
    try:
        from inspector.component_inspector import ComponentInspector
        results['component_inspector'] = True
        print("   ✅ Component inspector imported successfully")
    except ImportError as e:
        results['component_inspector'] = False
        print(f"   ❌ Component inspector import failed: {e}")
    
    # Test 5: Create component and test editor
    print("5. Testing component creation and editor...")
    try:
        component = ModelComponent("test_stock", "stock")
        
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
        
        if results['spreadsheet_editor']:
            editor = SpreadsheetDataEditor([component], mock_model)
            results['editor_creation'] = True
            print("   ✅ Editor created successfully")
        else:
            results['editor_creation'] = False
            print("   ❌ Cannot test editor creation - import failed")
            
    except Exception as e:
        results['editor_creation'] = False
        print(f"   ❌ Editor creation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Test graphics item creation
    print("6. Testing graphics item creation...")
    try:
        if results['graphics_items']:
            component = ModelComponent("test_stock", "stock")
            stock_item = StockItem(component)
            results['graphics_item_creation'] = True
            print("   ✅ Graphics item created successfully")
        else:
            results['graphics_item_creation'] = False
            print("   ❌ Cannot test graphics item - import failed")
    except Exception as e:
        results['graphics_item_creation'] = False
        print(f"   ❌ Graphics item creation failed: {e}")
    
    print("\n" + "=" * 50)
    print("INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("The integration should work correctly.")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("This may explain why component clicking doesn't work.")
    
    return results

class IntegrationTestWindow(QMainWindow):
    """Test window for integration debugging."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Integration Debug Test")
        self.setGeometry(100, 100, 600, 500)
        
        self.test_results = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Integration Debug Test")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title_label)
        
        # Test button
        test_btn = QPushButton("Run Integration Tests")
        test_btn.clicked.connect(self.run_tests)
        layout.addWidget(test_btn)
        
        # Results area
        self.results_area = QTextEdit()
        layout.addWidget(self.results_area)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.editor_test_btn = QPushButton("Test Editor Directly")
        self.editor_test_btn.clicked.connect(self.test_editor_directly)
        self.editor_test_btn.setEnabled(False)
        button_layout.addWidget(self.editor_test_btn)
        
        self.graphics_test_btn = QPushButton("Test Graphics Item")
        self.graphics_test_btn.clicked.connect(self.test_graphics_item)
        self.graphics_test_btn.setEnabled(False)
        button_layout.addWidget(self.graphics_test_btn)
        
        layout.addLayout(button_layout)
        
        self.log("Click 'Run Integration Tests' to start debugging...")
        
    def log(self, message):
        """Add a message to the results area."""
        self.results_area.append(message)
        print(message)
        
    def run_tests(self):
        """Run the integration tests."""
        self.results_area.clear()
        self.log("Running integration tests...")
        self.log("=" * 50)
        
        # Capture test results
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.test_results = test_all_integrations()
        
        output = f.getvalue()
        self.log(output)
        
        # Enable buttons based on results
        if self.test_results.get('spreadsheet_editor', False):
            self.editor_test_btn.setEnabled(True)
            
        if self.test_results.get('graphics_items', False):
            self.graphics_test_btn.setEnabled(True)
    
    def test_editor_directly(self):
        """Test the editor directly."""
        self.log("\n🚀 Testing editor directly...")
        
        try:
            from inspector.spreadsheet_editor import SpreadsheetDataEditor
            from sd_toolkit.models.model_component import ModelComponent
            
            component = ModelComponent("direct_test", "stock")
            
            class MockModel:
                def __init__(self):
                    self.dimensions = {
                        'parcel': {'labels': ['1001', '1002'], 'description': 'Parcels', 'type': 'categorical', 'size': 2},
                        'time': {'labels': ['2020', '2021'], 'description': 'Time', 'type': 'temporal', 'size': 2}
                    }
            
            editor = SpreadsheetDataEditor([component], MockModel(), parent=self)
            editor.show()
            
            self.log("✅ Editor opened successfully!")
            
        except Exception as e:
            self.log(f"❌ Editor test failed: {e}")
            import traceback
            self.log(traceback.format_exc())
    
    def test_graphics_item(self):
        """Test graphics item creation."""
        self.log("\n🎨 Testing graphics item...")
        
        try:
            from canvas.graphics_items import StockItem
            from sd_toolkit.models.model_component import ModelComponent
            
            component = ModelComponent("graphics_test", "stock")
            item = StockItem(component)
            
            self.log("✅ Graphics item created successfully!")
            self.log("Try double-clicking components in the main GUI now.")
            
        except Exception as e:
            self.log(f"❌ Graphics item test failed: {e}")

def main():
    """Main function."""
    
    app = QApplication(sys.argv)
    
    # Run console tests first
    test_all_integrations()
    
    # Show GUI for interactive testing
    test_window = IntegrationTestWindow()
    test_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
