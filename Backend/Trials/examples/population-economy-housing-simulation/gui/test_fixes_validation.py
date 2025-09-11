#!/usr/bin/env python3
"""
Test script to validate the fixes for temporal dimension handling and data persistence
in the multidimensional spreadsheet data editor.

This script tests:
1. Temporal dimension detection and handling
2. Data persistence when switching between dimension combinations
3. Data preservation when changing dimension filters
"""

import sys
import os
from pathlib import Path

# Add the necessary directories to the path
gui_dir = Path(__file__).parent
project_root = gui_dir.parent.parent.parent  # Go up to ScenaAdaptPy root
sd_toolkit_dir = project_root / "sd_toolkit"

sys.path.insert(0, str(gui_dir))
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(sd_toolkit_dir))

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
    from PyQt6.QtCore import Qt, QTimer
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False

if PYQT6_AVAILABLE:
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        EDITOR_AVAILABLE = True
    except ImportError as e:
        EDITOR_AVAILABLE = False
        IMPORT_ERROR = str(e)
else:
    EDITOR_AVAILABLE = False
    IMPORT_ERROR = "PyQt6 not available"


class TestValidationWindow(QMainWindow):
    """Main test window for validating the fixes."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spreadsheet Editor Fixes Validation")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Spreadsheet Editor Fixes Validation")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Test results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        
        # Test buttons
        self.test1_btn = QPushButton("Test 1: Temporal Dimension Detection")
        self.test1_btn.clicked.connect(self.test_temporal_dimension_detection)
        layout.addWidget(self.test1_btn)
        
        self.test2_btn = QPushButton("Test 2: Data Persistence - Dimension Switching")
        self.test2_btn.clicked.connect(self.test_data_persistence_dimension_switching)
        layout.addWidget(self.test2_btn)
        
        self.test3_btn = QPushButton("Test 3: Data Persistence - Filter Changes")
        self.test3_btn.clicked.connect(self.test_data_persistence_filter_changes)
        layout.addWidget(self.test3_btn)
        
        self.test4_btn = QPushButton("Test 4: Integration Test - All Features")
        self.test4_btn.clicked.connect(self.test_integration_all_features)
        layout.addWidget(self.test4_btn)
        
        # Initialize test results
        self.log("=== Spreadsheet Editor Fixes Validation ===\n")
        self.log("This test suite validates the fixes for:")
        self.log("1. Temporal dimension handling issues")
        self.log("2. Data persistence when switching dimensions")
        self.log("3. Data preservation during filter changes\n")
        
        if not EDITOR_AVAILABLE:
            self.log(f"❌ ERROR: Spreadsheet editor not available: {IMPORT_ERROR}")
            return
            
        self.log("✅ Spreadsheet editor is available")
        self.log("Click the test buttons to run individual tests.\n")
        
    def log(self, message):
        """Add a message to the results display."""
        self.results_text.append(message)
        self.results_text.ensureCursorVisible()
        QApplication.processEvents()
        
    def create_mock_model_with_temporal_dimensions(self):
        """Create a mock model with various temporal dimension patterns."""
        
        class MockModel:
            def __init__(self):
                self.dimensions = {
                    # Test case 1: Explicit temporal type
                    'time': {
                        'labels': ['2020', '2021', '2022', '2023', '2024'],
                        'description': 'Annual time steps',
                        'type': 'temporal',
                        'size': 5
                    },
                    # Test case 2: Year labels (should be detected as temporal)
                    'year': {
                        'labels': ['2020', '2021', '2022', '2023', '2024'],
                        'description': 'Year dimension',
                        'size': 5
                    },
                    # Test case 3: Time periods with special naming
                    'time_10yr': {
                        'labels': ['2020_10yr', '2030_10yr', '2040_10yr'],
                        'description': 'Decadal time periods',
                        'size': 3
                    },
                    # Test case 4: Regular categorical dimension
                    'parcel': {
                        'labels': ['1001', '1002', '1003'],
                        'description': 'Property parcel identifiers',
                        'type': 'categorical',
                        'size': 3
                    },
                    # Test case 5: Numerical dimension
                    'income_level': {
                        'labels': ['30000', '60000', '120000'],
                        'description': 'Income levels in USD',
                        'size': 3
                    }
                }
        
        return MockModel()
        
    def create_test_components(self):
        """Create test components for validation."""
        
        components = [
            ModelComponent(
                name="test_stock",
                component_type="stock",
                properties={
                    'initial_value': 1000,
                    'units': 'units',
                    'spatial_dims': ['parcel', 'time', 'year'],
                    'description': 'Test stock component'
                }
            ),
            ModelComponent(
                name="test_flow",
                component_type="flow",
                properties={
                    'rate': 0.1,
                    'units': 'units/year',
                    'spatial_dims': ['parcel', 'time_10yr'],
                    'description': 'Test flow component'
                }
            )
        ]
        
        return components
        
    def test_temporal_dimension_detection(self):
        """Test that temporal dimensions are correctly detected and handled."""
        
        self.log("\n🧪 TEST 1: Temporal Dimension Detection")
        self.log("=" * 50)
        
        try:
            # Create mock model and components
            mock_model = self.create_mock_model_with_temporal_dimensions()
            components = self.create_test_components()
            
            # Create editor
            editor = SpreadsheetDataEditor(components, mock_model, parent=self)
            
            # Check dimension detection
            available_dims = editor.dimension_selector.available_dimensions
            
            self.log("Checking temporal dimension detection:")
            
            temporal_dims_found = []
            for dim_name, dim_data in available_dims.items():
                dim_type = dim_data.get('type', 'unknown')
                self.log(f"  - {dim_name}: type='{dim_type}', labels={dim_data.get('labels', [])}")
                
                if dim_type == 'temporal':
                    temporal_dims_found.append(dim_name)
            
            # Validate results
            expected_temporal = ['time', 'year', 'time_10yr']  # These should be detected as temporal
            
            success = True
            for expected in expected_temporal:
                if expected in temporal_dims_found:
                    self.log(f"  ✅ {expected} correctly detected as temporal")
                else:
                    self.log(f"  ❌ {expected} NOT detected as temporal")
                    success = False
            
            # Check that non-temporal dimensions are not marked as temporal
            non_temporal = ['parcel', 'income_level']
            for dim_name in non_temporal:
                if dim_name in available_dims:
                    dim_type = available_dims[dim_name].get('type', 'unknown')
                    if dim_type != 'temporal':
                        self.log(f"  ✅ {dim_name} correctly NOT marked as temporal (type: {dim_type})")
                    else:
                        self.log(f"  ❌ {dim_name} incorrectly marked as temporal")
                        success = False
            
            if success:
                self.log("\n✅ TEST 1 PASSED: Temporal dimension detection working correctly")
            else:
                self.log("\n❌ TEST 1 FAILED: Issues with temporal dimension detection")
                
            editor.close()
            
        except Exception as e:
            self.log(f"\n❌ TEST 1 ERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())

    def test_data_persistence_dimension_switching(self):
        """Test that data persists when switching between dimension combinations."""

        self.log("\n🧪 TEST 2: Data Persistence - Dimension Switching")
        self.log("=" * 50)

        try:
            # Create mock model and components
            mock_model = self.create_mock_model_with_temporal_dimensions()
            components = self.create_test_components()

            # Create editor
            editor = SpreadsheetDataEditor(components, mock_model, parent=self)

            # Set initial dimensions
            available_dims = list(editor.dimension_selector.available_dimensions.keys())
            if len(available_dims) >= 2:
                dim1, dim2 = available_dims[0], available_dims[1]
                editor.dimension_selector.set_selected_dimensions(dim1, dim2)

                self.log(f"Set initial dimensions: {dim1} × {dim2}")

                # Add some test data
                table_model = editor.table_model
                test_data = {
                    (components[0].name, 'test_coord1', 'test_coord2'): 123.45,
                    (components[1].name, 'test_coord1', 'test_coord2'): 678.90
                }

                # Manually add data to the model
                for key, value in test_data.items():
                    table_model.data_matrix[key] = value

                self.log(f"Added test data: {len(test_data)} entries")

                # Switch to different dimensions
                if len(available_dims) >= 4:
                    dim3, dim4 = available_dims[2], available_dims[3]
                    editor.dimension_selector.set_selected_dimensions(dim3, dim4)
                    self.log(f"Switched to dimensions: {dim3} × {dim4}")

                    # Switch back to original dimensions
                    editor.dimension_selector.set_selected_dimensions(dim1, dim2)
                    self.log(f"Switched back to dimensions: {dim1} × {dim2}")

                    # Check if data is still there
                    preserved_data = 0
                    for key, expected_value in test_data.items():
                        if key in table_model.data_matrix and table_model.data_matrix[key] == expected_value:
                            preserved_data += 1

                    if preserved_data == len(test_data):
                        self.log(f"✅ All {len(test_data)} data entries preserved after dimension switching")
                        self.log("\n✅ TEST 2 PASSED: Data persistence working correctly")
                    else:
                        self.log(f"❌ Only {preserved_data}/{len(test_data)} data entries preserved")
                        self.log("\n❌ TEST 2 FAILED: Data not properly preserved")
                else:
                    self.log("⚠️  Not enough dimensions for full switching test")
                    self.log("\n⚠️  TEST 2 SKIPPED: Insufficient dimensions")
            else:
                self.log("❌ Not enough dimensions available for test")
                self.log("\n❌ TEST 2 FAILED: Insufficient dimensions")

            editor.close()

        except Exception as e:
            self.log(f"\n❌ TEST 2 ERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())

    def test_data_persistence_filter_changes(self):
        """Test that data persists when changing dimension filters."""

        self.log("\n🧪 TEST 3: Data Persistence - Filter Changes")
        self.log("=" * 50)

        try:
            # Create mock model with more dimensions for filtering
            mock_model = self.create_mock_model_with_temporal_dimensions()
            components = self.create_test_components()

            # Create editor
            editor = SpreadsheetDataEditor(components, mock_model, parent=self)

            # Set dimensions that will leave some for filtering
            available_dims = list(editor.dimension_selector.available_dimensions.keys())
            if len(available_dims) >= 3:
                dim1, dim2 = available_dims[0], available_dims[1]
                editor.dimension_selector.set_selected_dimensions(dim1, dim2)

                self.log(f"Set dimensions: {dim1} × {dim2}")

                # Check if there are filter dimensions available
                filter_widget = editor.dimension_filters
                current_filters = filter_widget.get_current_filters()

                if current_filters:
                    self.log(f"Available filters: {list(current_filters.keys())}")

                    # Add test data
                    table_model = editor.table_model
                    test_key = table_model._create_data_key(components[0].name, 'coord1', 'coord2')
                    test_value = 999.99
                    table_model.data_matrix[test_key] = test_value

                    self.log(f"Added test data with key: {test_key}")

                    # Change a filter value (simulate user changing dropdown)
                    filter_name = list(current_filters.keys())[0]
                    available_filter_values = editor.dimension_selector.available_dimensions[filter_name]['labels']

                    if len(available_filter_values) > 1:
                        # Change to a different filter value
                        new_filter_value = available_filter_values[1]
                        filter_widget.current_filters[filter_name] = new_filter_value
                        editor.on_dimension_filters_changed(filter_widget.current_filters)

                        self.log(f"Changed filter {filter_name} to: {new_filter_value}")

                        # Change back to original filter value
                        original_filter_value = available_filter_values[0]
                        filter_widget.current_filters[filter_name] = original_filter_value
                        editor.on_dimension_filters_changed(filter_widget.current_filters)

                        self.log(f"Changed filter {filter_name} back to: {original_filter_value}")

                        # Check if data is preserved
                        restored_key = table_model._create_data_key(components[0].name, 'coord1', 'coord2')
                        if restored_key in table_model.data_matrix and table_model.data_matrix[restored_key] == test_value:
                            self.log("✅ Data preserved after filter changes")
                            self.log("\n✅ TEST 3 PASSED: Filter change data persistence working")
                        else:
                            self.log(f"❌ Data not preserved. Expected key: {restored_key}")
                            self.log(f"Available keys: {list(table_model.data_matrix.keys())}")
                            self.log("\n❌ TEST 3 FAILED: Data not preserved during filter changes")
                    else:
                        self.log("⚠️  Not enough filter values for test")
                        self.log("\n⚠️  TEST 3 SKIPPED: Insufficient filter values")
                else:
                    self.log("⚠️  No filter dimensions available")
                    self.log("\n⚠️  TEST 3 SKIPPED: No filter dimensions")
            else:
                self.log("❌ Not enough dimensions for filter test")
                self.log("\n❌ TEST 3 FAILED: Insufficient dimensions")

            editor.close()

        except Exception as e:
            self.log(f"\n❌ TEST 3 ERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())

    def test_integration_all_features(self):
        """Integration test combining all features."""

        self.log("\n🧪 TEST 4: Integration Test - All Features")
        self.log("=" * 50)

        try:
            # Create comprehensive test scenario
            mock_model = self.create_mock_model_with_temporal_dimensions()
            components = self.create_test_components()

            # Create editor
            editor = SpreadsheetDataEditor(components, mock_model, parent=self)

            self.log("Testing complete workflow:")

            # Step 1: Verify temporal dimensions are detected
            available_dims = editor.dimension_selector.available_dimensions
            temporal_dims = [name for name, data in available_dims.items() if data.get('type') == 'temporal']
            self.log(f"1. Temporal dimensions detected: {temporal_dims}")

            # Step 2: Set initial dimensions including a temporal one
            if temporal_dims and len(available_dims) >= 2:
                temporal_dim = temporal_dims[0]
                other_dims = [name for name in available_dims.keys() if name != temporal_dim]
                other_dim = other_dims[0] if other_dims else list(available_dims.keys())[1]

                editor.dimension_selector.set_selected_dimensions(temporal_dim, other_dim)
                self.log(f"2. Set dimensions: {temporal_dim} (temporal) × {other_dim}")

                # Step 3: Add test data
                table_model = editor.table_model
                test_entries = []
                for i, component in enumerate(components):
                    for j, coord1 in enumerate(available_dims[temporal_dim]['labels'][:2]):  # Use first 2 temporal coords
                        for k, coord2 in enumerate(available_dims[other_dim]['labels'][:2]):  # Use first 2 other coords
                            key = table_model._create_data_key(component.name, coord1, coord2)
                            value = 100 + i * 10 + j + k
                            table_model.data_matrix[key] = value
                            test_entries.append((key, value))

                self.log(f"3. Added {len(test_entries)} test data entries")

                # Step 4: Switch dimensions and verify data persistence
                if len(other_dims) >= 2:
                    new_other_dim = other_dims[1]
                    editor.dimension_selector.set_selected_dimensions(temporal_dim, new_other_dim)
                    self.log(f"4. Switched to: {temporal_dim} × {new_other_dim}")

                    # Switch back
                    editor.dimension_selector.set_selected_dimensions(temporal_dim, other_dim)
                    self.log(f"5. Switched back to: {temporal_dim} × {other_dim}")

                    # Verify data persistence
                    preserved_count = 0
                    for key, expected_value in test_entries:
                        if key in table_model.data_matrix and table_model.data_matrix[key] == expected_value:
                            preserved_count += 1

                    self.log(f"6. Data preservation: {preserved_count}/{len(test_entries)} entries preserved")

                    # Step 5: Test filter changes if available
                    filter_widget = editor.dimension_filters
                    current_filters = filter_widget.get_current_filters()

                    if current_filters:
                        filter_name = list(current_filters.keys())[0]
                        filter_labels = available_dims[filter_name]['labels']

                        if len(filter_labels) > 1:
                            # Change filter
                            original_value = current_filters[filter_name]
                            new_value = filter_labels[1] if filter_labels[1] != original_value else filter_labels[0]

                            filter_widget.current_filters[filter_name] = new_value
                            editor.on_dimension_filters_changed(filter_widget.current_filters)
                            self.log(f"7. Changed filter {filter_name}: {original_value} → {new_value}")

                            # Change back
                            filter_widget.current_filters[filter_name] = original_value
                            editor.on_dimension_filters_changed(filter_widget.current_filters)
                            self.log(f"8. Changed filter back: {new_value} → {original_value}")

                            # Final verification
                            final_preserved = 0
                            for key, expected_value in test_entries:
                                if key in table_model.data_matrix and table_model.data_matrix[key] == expected_value:
                                    final_preserved += 1

                            self.log(f"9. Final data check: {final_preserved}/{len(test_entries)} entries preserved")

                            # Determine overall success
                            if (len(temporal_dims) > 0 and
                                preserved_count == len(test_entries) and
                                final_preserved == len(test_entries)):
                                self.log("\n✅ INTEGRATION TEST PASSED: All features working correctly!")
                            else:
                                self.log("\n❌ INTEGRATION TEST FAILED: Some features not working properly")
                        else:
                            self.log("7. Skipping filter test - not enough filter values")
                            if len(temporal_dims) > 0 and preserved_count == len(test_entries):
                                self.log("\n✅ INTEGRATION TEST PASSED: Core features working correctly!")
                            else:
                                self.log("\n❌ INTEGRATION TEST FAILED: Core features not working properly")
                    else:
                        self.log("7. No filters available for testing")
                        if len(temporal_dims) > 0 and preserved_count == len(test_entries):
                            self.log("\n✅ INTEGRATION TEST PASSED: Core features working correctly!")
                        else:
                            self.log("\n❌ INTEGRATION TEST FAILED: Core features not working properly")
                else:
                    self.log("4. Not enough dimensions for full switching test")
                    if len(temporal_dims) > 0:
                        self.log("\n⚠️  INTEGRATION TEST PARTIAL: Temporal detection working, limited dimension testing")
                    else:
                        self.log("\n❌ INTEGRATION TEST FAILED: Temporal detection not working")
            else:
                self.log("❌ No temporal dimensions detected or insufficient dimensions")
                self.log("\n❌ INTEGRATION TEST FAILED: Basic requirements not met")

            editor.close()

        except Exception as e:
            self.log(f"\n❌ INTEGRATION TEST ERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())


def main():
    """Main function to run the validation tests."""

    if not PYQT6_AVAILABLE:
        print("❌ PyQt6 is not available. Please install it with: pip install PyQt6")
        return

    if not EDITOR_AVAILABLE:
        print(f"❌ Spreadsheet editor is not available: {IMPORT_ERROR}")
        return

    app = QApplication(sys.argv)

    # Create and show the test window
    test_window = TestValidationWindow()
    test_window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
