#!/usr/bin/env python3
"""
Test script to validate the fix for multidimensional data persistence issue.

This script specifically tests the scenario described in the issue:
- 3+ dimensional data structure
- Data entry in one dimension combination
- Switching to different dimension combination
- Verifying data is preserved and displayed correctly
"""

import sys
import os
from pathlib import Path

# Add the necessary directories to the path
gui_dir = Path(__file__).parent
project_root = gui_dir.parent.parent.parent
sd_toolkit_dir = project_root / "sd_toolkit"

sys.path.insert(0, str(gui_dir))
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(sd_toolkit_dir))

def test_multidimensional_persistence():
    """Test the exact scenario described in the issue."""
    
    print("\n🧪 MULTIDIMENSIONAL DATA PERSISTENCE TEST")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create mock model with 3+ dimensions (Time, Age, City)
        class MockModel:
            def __init__(self):
                self.dimensions = {
                    'time': {
                        'labels': ['2020', '2021', '2022'],
                        'description': 'Time periods',
                        'type': 'temporal',
                        'size': 3
                    },
                    'age': {
                        'labels': ['10', '20', '30'],
                        'description': 'Age groups',
                        'type': 'numerical',
                        'size': 3
                    },
                    'city': {
                        'labels': ['Montreal', 'Toronto', 'Vancouver'],
                        'description': 'Cities',
                        'type': 'categorical',
                        'size': 3
                    }
                }
        
        # Create test component with all 3 dimensions
        component = ModelComponent(
            name="population",
            component_type="stock",
            properties={
                'initial_value': 1000,
                'units': 'people',
                'spatial_dims': ['time', 'age', 'city'],
                'description': 'Population by time, age, and city'
            }
        )
        
        # Create editor
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        print("Step 1: Initial Setup - Time (rows) × Age (columns), City filter = 'Montreal'")
        
        # Set initial dimensions: Time × Age
        editor.dimension_selector.set_selected_dimensions('time', 'age')
        
        # Set City filter to Montreal
        filter_widget = editor.dimension_filters
        current_filters = filter_widget.get_current_filters()
        if 'city' in current_filters:
            filter_widget.current_filters['city'] = 'Montreal'
            editor.on_dimension_filters_changed(filter_widget.current_filters)
        
        print(f"   Dimensions set: time × age")
        print(f"   City filter: {filter_widget.current_filters.get('city', 'N/A')}")
        
        print("\nStep 2: Data Entry")
        
        # Add test data: Time=2020, Age=10, City=Montreal -> value 1
        table_model = editor.table_model
        print(f"   Current dimensions: {table_model.dimension_1} × {table_model.dimension_2}")
        print(f"   Current filters: {table_model.dimension_filters}")

        key1 = table_model._create_data_key('population', '2020', '10')
        table_model.data_matrix[key1] = 1
        print(f"   Entered value 1 at Time=2020, Age=10 (City=Montreal)")
        print(f"   Key: {key1}")

        # Add test data: Time=2021, Age=20, City=Montreal -> value 22
        key2 = table_model._create_data_key('population', '2021', '20')
        table_model.data_matrix[key2] = 22
        print(f"   Entered value 22 at Time=2021, Age=20 (City=Montreal)")
        print(f"   Key: {key2}")
        
        print(f"\nStep 3: Dimension Switch - City (rows) × Age (columns), Time filter available")
        
        # Switch dimensions: City × Age
        editor.dimension_selector.set_selected_dimensions('city', 'age')
        
        # The Time filter should now be available and we can set it
        current_filters = filter_widget.get_current_filters()
        print(f"   New dimensions: city × age")
        print(f"   Available filters: {list(current_filters.keys())}")
        
        print("\nStep 4: Verification - Check if data is preserved and displayed correctly")
        
        # Check if the data is preserved in the new dimension configuration
        # Expected: Montreal, Age=10 should show value 1
        # Expected: Montreal, Age=20 should show value 22
        
        # Test different time filter values to see our data
        time_values = ['2020', '2021', '2022']
        found_data = {}
        
        for time_val in time_values:
            if 'time' in current_filters:
                # Set time filter
                filter_widget.current_filters['time'] = time_val
                editor.on_dimension_filters_changed(filter_widget.current_filters)
                
                # Check for our expected data points
                key_montreal_10 = table_model._create_data_key('population', 'Montreal', '10')
                key_montreal_20 = table_model._create_data_key('population', 'Montreal', '20')
                
                val_10 = table_model.data_matrix.get(key_montreal_10)
                val_20 = table_model.data_matrix.get(key_montreal_20)
                
                if val_10:
                    found_data[f'Montreal,Age=10,Time={time_val}'] = val_10
                if val_20:
                    found_data[f'Montreal,Age=20,Time={time_val}'] = val_20
        
        print(f"   Found data points: {len(found_data)}")
        for location, value in found_data.items():
            print(f"     {location}: {value}")
        
        # Verify expected results
        expected_results = {
            'Montreal,Age=10,Time=2020': 1,
            'Montreal,Age=20,Time=2021': 22
        }
        
        success = True
        for expected_key, expected_value in expected_results.items():
            if expected_key in found_data and found_data[expected_key] == expected_value:
                print(f"   ✅ {expected_key}: Expected {expected_value}, Found {found_data[expected_key]}")
            else:
                print(f"   ❌ {expected_key}: Expected {expected_value}, Found {found_data.get(expected_key, 'MISSING')}")
                success = False
        
        # Additional verification: Check the raw data matrix
        print(f"\nStep 5: Raw Data Matrix Analysis")
        print(f"   Total entries in data matrix: {len(table_model.data_matrix)}")
        
        # Show all non-zero entries
        non_zero_entries = {k: v for k, v in table_model.data_matrix.items() if v and v != 0}
        print(f"   Non-zero entries: {len(non_zero_entries)}")
        for key, value in non_zero_entries.items():
            print(f"     {key}: {value}")
        
        # Clean up
        editor.close()
        
        if success:
            print(f"\n✅ MULTIDIMENSIONAL PERSISTENCE TEST PASSED!")
            print("   Data was correctly preserved and displayed after dimension switching.")
            return True
        else:
            print(f"\n❌ MULTIDIMENSIONAL PERSISTENCE TEST FAILED!")
            print("   Data was not properly preserved during dimension switching.")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_complex_dimension_switching():
    """Test multiple dimension switches to ensure robustness."""
    
    print("\n🧪 COMPLEX DIMENSION SWITCHING TEST")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create mock model with 4 dimensions
        class MockModel:
            def __init__(self):
                self.dimensions = {
                    'time': {
                        'labels': ['2020', '2021'],
                        'description': 'Time periods',
                        'type': 'temporal',
                        'size': 2
                    },
                    'age': {
                        'labels': ['young', 'old'],
                        'description': 'Age groups',
                        'type': 'categorical',
                        'size': 2
                    },
                    'city': {
                        'labels': ['Montreal', 'Toronto'],
                        'description': 'Cities',
                        'type': 'categorical',
                        'size': 2
                    },
                    'income': {
                        'labels': ['low', 'high'],
                        'description': 'Income levels',
                        'type': 'categorical',
                        'size': 2
                    }
                }
        
        component = ModelComponent(
            name="test_data",
            component_type="stock",
            properties={
                'initial_value': 0,
                'units': 'units',
                'spatial_dims': ['time', 'age', 'city', 'income'],
                'description': 'Test data with 4 dimensions'
            }
        )
        
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        # Test sequence: multiple dimension switches with data entry
        test_sequence = [
            ('time', 'age', {'city': 'Montreal', 'income': 'low'}, [('2020', 'young', 100)]),
            ('city', 'income', {'time': '2020', 'age': 'young'}, [('Montreal', 'low', 100)]),  # Should find our data
            ('age', 'income', {'time': '2020', 'city': 'Montreal'}, [('young', 'low', 100)]),  # Should find our data
            ('time', 'city', {'age': 'young', 'income': 'low'}, [('2020', 'Montreal', 100)]),  # Should find our data
        ]
        
        all_passed = True
        
        for i, (dim1, dim2, filters, expected_data) in enumerate(test_sequence):
            print(f"\nSequence {i+1}: {dim1} × {dim2}, filters: {filters}")
            
            # Set dimensions
            editor.dimension_selector.set_selected_dimensions(dim1, dim2)
            
            # Set filters
            filter_widget = editor.dimension_filters
            for filter_dim, filter_val in filters.items():
                if filter_dim in filter_widget.current_filters:
                    filter_widget.current_filters[filter_dim] = filter_val
            editor.on_dimension_filters_changed(filter_widget.current_filters)
            
            # If this is the first sequence, add data
            if i == 0:
                table_model = editor.table_model
                for coord1, coord2, value in expected_data:
                    key = table_model._create_data_key('test_data', coord1, coord2)
                    table_model.data_matrix[key] = value
                    print(f"   Added data: {coord1}, {coord2} = {value}")
            
            # Check for expected data
            table_model = editor.table_model
            for coord1, coord2, expected_value in expected_data:
                key = table_model._create_data_key('test_data', coord1, coord2)
                actual_value = table_model.data_matrix.get(key, 0)
                
                if actual_value == expected_value:
                    print(f"   ✅ Found expected data: {coord1}, {coord2} = {actual_value}")
                else:
                    print(f"   ❌ Data mismatch: {coord1}, {coord2} = {actual_value} (expected {expected_value})")
                    all_passed = False
        
        editor.close()
        
        if all_passed:
            print(f"\n✅ COMPLEX DIMENSION SWITCHING TEST PASSED!")
            return True
        else:
            print(f"\n❌ COMPLEX DIMENSION SWITCHING TEST FAILED!")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all multidimensional persistence tests."""
    
    print("=== MULTIDIMENSIONAL DATA PERSISTENCE VALIDATION ===")
    print("Testing the fix for data persistence with 3+ dimensional data")
    print("when switching between different dimension combinations.")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Run tests
        test1_passed = test_multidimensional_persistence()
        test2_passed = test_complex_dimension_switching()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY:")
        print(f"  Multidimensional Persistence: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
        print(f"  Complex Dimension Switching: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL TESTS PASSED! Multidimensional data persistence is working correctly.")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED. The multidimensional persistence issue may not be fully resolved.")
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
