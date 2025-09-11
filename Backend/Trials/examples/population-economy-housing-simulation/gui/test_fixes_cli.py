#!/usr/bin/env python3
"""
Command-line test script to validate the fixes for temporal dimension handling 
and data persistence in the multidimensional spreadsheet data editor.

This script runs automated tests without requiring GUI interaction.
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

def test_temporal_dimension_detection():
    """Test temporal dimension detection logic."""
    
    print("\n🧪 TEST 1: Temporal Dimension Detection")
    print("=" * 50)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create mock model with various dimension types
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
        
        # Create test component
        component = ModelComponent(
            name="test_stock",
            component_type="stock",
            properties={
                'initial_value': 1000,
                'units': 'units',
                'spatial_dims': ['parcel', 'time', 'year', 'time_10yr', 'income_level'],
                'description': 'Test stock component'
            }
        )
        
        # Create editor (without showing GUI)
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        # Check dimension detection
        available_dims = editor.dimension_selector.available_dimensions
        
        print("Checking temporal dimension detection:")
        
        temporal_dims_found = []
        for dim_name, dim_data in available_dims.items():
            dim_type = dim_data.get('type', 'unknown')
            labels = dim_data.get('labels', [])
            print(f"  - {dim_name}: type='{dim_type}', labels={labels}")

            # Debug: Show why time_10yr might not be detected
            if dim_name == 'time_10yr':
                print(f"    DEBUG time_10yr: name='{dim_name}', labels={labels}")
                print(f"    Contains '_10yr': {'_10yr' in dim_name.lower()}")
                print(f"    Labels contain time patterns: {any('_10yr' in str(label).lower() for label in labels)}")

            if dim_type == 'temporal':
                temporal_dims_found.append(dim_name)
        
        # Validate results
        expected_temporal = ['time', 'year', 'time_10yr']  # These should be detected as temporal
        
        success = True
        for expected in expected_temporal:
            if expected in temporal_dims_found:
                print(f"  ✅ {expected} correctly detected as temporal")
            else:
                print(f"  ❌ {expected} NOT detected as temporal")
                success = False
        
        # Check that non-temporal dimensions are not marked as temporal
        non_temporal = ['parcel', 'income_level']
        for dim_name in non_temporal:
            if dim_name in available_dims:
                dim_type = available_dims[dim_name].get('type', 'unknown')
                if dim_type != 'temporal':
                    print(f"  ✅ {dim_name} correctly NOT marked as temporal (type: {dim_type})")
                else:
                    print(f"  ❌ {dim_name} incorrectly marked as temporal")
                    success = False
        
        # Clean up
        editor.close()
        
        if success:
            print("\n✅ TEST 1 PASSED: Temporal dimension detection working correctly")
            return True
        else:
            print("\n❌ TEST 1 FAILED: Issues with temporal dimension detection")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 1 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_data_persistence():
    """Test data persistence during dimension changes."""
    
    print("\n🧪 TEST 2: Data Persistence")
    print("=" * 50)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
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
                    },
                    'building_type': {
                        'labels': ['residential', 'commercial'],
                        'description': 'Building types',
                        'type': 'categorical',
                        'size': 2
                    },
                    'income': {
                        'labels': ['low', 'medium', 'high'],
                        'description': 'Income levels',
                        'type': 'categorical',
                        'size': 3
                    }
                }
        
        # Create test components
        components = [
            ModelComponent(
                name="test_stock",
                component_type="stock",
                properties={
                    'initial_value': 1000,
                    'units': 'units',
                    'spatial_dims': ['parcel', 'time', 'building_type', 'income'],
                    'description': 'Test stock component'
                }
            )
        ]
        
        # Create editor
        mock_model = MockModel()
        editor = SpreadsheetDataEditor(components, mock_model, parent=None)
        
        # Set initial dimensions
        editor.dimension_selector.set_selected_dimensions('parcel', 'time')
        print("Set initial dimensions: parcel × time")
        
        # Add test data directly to the model
        table_model = editor.table_model
        test_data = {}
        
        # Create test data entries
        for parcel in ['1001', '1002']:
            for time_val in ['2020', '2021']:
                key = table_model._create_data_key('test_stock', parcel, time_val)
                value = float(f"{parcel[-1]}{time_val[-1]}")  # e.g., 10 for parcel 1001, year 2020
                table_model.data_matrix[key] = value
                test_data[key] = value
        
        print(f"Added {len(test_data)} test data entries")
        
        # Switch dimensions
        editor.dimension_selector.set_selected_dimensions('building_type', 'income')
        print("Switched dimensions to: building_type × income")
        
        # Switch back
        editor.dimension_selector.set_selected_dimensions('parcel', 'time')
        print("Switched back to: parcel × time")
        
        # Check data persistence
        preserved_count = 0
        for key, expected_value in test_data.items():
            if key in table_model.data_matrix and table_model.data_matrix[key] == expected_value:
                preserved_count += 1
            else:
                print(f"  Missing or changed: {key} (expected: {expected_value})")
        
        print(f"Data preservation: {preserved_count}/{len(test_data)} entries preserved")
        
        # Clean up
        editor.close()
        
        if preserved_count == len(test_data):
            print("\n✅ TEST 2 PASSED: Data persistence working correctly")
            return True
        else:
            print("\n❌ TEST 2 FAILED: Data not properly preserved")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 2 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    
    print("=== Spreadsheet Editor Fixes Validation (CLI) ===")
    print("Testing fixes for:")
    print("1. Temporal dimension handling issues")
    print("2. Data persistence when switching dimensions")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Run tests
        test1_passed = test_temporal_dimension_detection()
        test2_passed = test_data_persistence()
        
        # Summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY:")
        print(f"  Temporal Dimension Detection: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
        print(f"  Data Persistence: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL TESTS PASSED! Fixes are working correctly.")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED. Please review the issues above.")
            return 1
            
    except ImportError as e:
        print(f"❌ Required dependencies not available: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
