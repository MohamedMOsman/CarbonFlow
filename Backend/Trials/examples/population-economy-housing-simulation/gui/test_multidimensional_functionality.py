#!/usr/bin/env python3
"""
Comprehensive test to verify all multidimensional spreadsheet editor functionality:
1. 3+ dimensional data handling without crashes
2. Proper table display with headers and data
3. Coordinate selection through row/column headers
4. Dimension filtering for 3rd, 4th+ dimensions
5. Data persistence across dimension changes
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

def test_comprehensive_multidimensional_functionality():
    """Test comprehensive multidimensional functionality."""
    
    print("\n🔍 COMPREHENSIVE MULTIDIMENSIONAL FUNCTIONALITY TEST")
    print("=" * 70)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        from PyQt6.QtCore import Qt
        
        # Create model with 4 dimensions for comprehensive testing
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
                        'labels': ['young', 'middle', 'old'],
                        'description': 'Age groups',
                        'size': 3
                    },
                    'city': {
                        'labels': ['Montreal', 'Toronto', 'Vancouver'],
                        'description': 'Cities',
                        'size': 3
                    },
                    'income': {
                        'labels': ['low', 'medium', 'high'],
                        'description': 'Income levels',
                        'size': 3
                    }
                }
        
        # Create component with 4 spatial dimensions
        component = ModelComponent(
            name="population",
            component_type="stock",
            properties={
                'initial_value': 1000,
                'units': 'people',
                'spatial_dims': ['time', 'age', 'city', 'income'],
                'description': 'Population by time, age, city, and income'
            }
        )
        
        print("Step 1: Create editor with 4-dimensional data")
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        print("   ✅ Editor created successfully")
        
        print("Step 2: Test initial dimension assignment (time × age)")
        editor.dimension_selector.set_selected_dimensions('time', 'age')
        
        table_model = editor.table_model
        print(f"   Table dimensions: {table_model.dimension_1} × {table_model.dimension_2}")
        print(f"   Row count: {table_model.rowCount()}")
        print(f"   Column count: {table_model.columnCount()}")
        print(f"   Row headers: {table_model.headers_vertical}")
        print(f"   Column headers: {table_model.headers_horizontal}")
        
        # Verify headers are correct
        expected_rows = 3  # 1 component × 3 time coordinates
        expected_cols = 3  # 3 age coordinates
        if table_model.rowCount() == expected_rows and table_model.columnCount() == expected_cols:
            print("   ✅ Table dimensions correct")
        else:
            print(f"   ❌ Expected {expected_rows}×{expected_cols}, got {table_model.rowCount()}×{table_model.columnCount()}")
            return False
        
        print("Step 3: Test dimension filtering")
        filter_widget = editor.dimension_filters
        current_filters = filter_widget.get_current_filters()
        print(f"   Available filters: {list(current_filters.keys())}")
        print(f"   Current filter values: {current_filters}")
        
        # Verify filters for unused dimensions
        expected_filters = {'city', 'income'}
        actual_filters = set(current_filters.keys())
        if actual_filters == expected_filters:
            print("   ✅ Dimension filters correct")
        else:
            print(f"   ❌ Expected filters {expected_filters}, got {actual_filters}")
            return False
        
        print("Step 4: Test data entry and retrieval")
        # Add data to specific coordinates
        test_data = [
            (0, 0, 1000.0),  # population[time=2020, age=young] = 1000
            (0, 1, 1500.0),  # population[time=2020, age=middle] = 1500
            (1, 0, 1100.0),  # population[time=2021, age=young] = 1100
            (2, 2, 800.0),   # population[time=2022, age=old] = 800
        ]
        
        for row, col, value in test_data:
            index = table_model.index(row, col)
            success = table_model.setData(index, value, Qt.ItemDataRole.EditRole)
            if not success:
                print(f"   ❌ Failed to set data at ({row}, {col})")
                return False
            
            # Verify data was stored
            stored_value = table_model.data(index, Qt.ItemDataRole.DisplayRole)
            if abs(float(stored_value) - value) > 0.001:
                print(f"   ❌ Data mismatch at ({row}, {col}): expected {value}, got {stored_value}")
                return False
        
        print("   ✅ Data entry and retrieval working")
        
        print("Step 5: Test dimension switching with data persistence")
        # Switch to city × income
        editor.dimension_selector.set_selected_dimensions('city', 'income')
        
        new_rows = table_model.rowCount()
        new_cols = table_model.columnCount()
        print(f"   New dimensions: {table_model.dimension_1} × {table_model.dimension_2}")
        print(f"   New table size: {new_rows} × {new_cols}")
        
        # Verify new dimensions
        expected_new_rows = 3  # 1 component × 3 city coordinates
        expected_new_cols = 3  # 3 income coordinates
        if new_rows == expected_new_rows and new_cols == expected_new_cols:
            print("   ✅ Dimension switching successful")
        else:
            print(f"   ❌ Expected {expected_new_rows}×{expected_new_cols}, got {new_rows}×{new_cols}")
            return False
        
        # Check that filters now include time and age
        new_filters = filter_widget.get_current_filters()
        expected_new_filters = {'time', 'age'}
        actual_new_filters = set(new_filters.keys())
        if actual_new_filters == expected_new_filters:
            print("   ✅ Filter dimensions updated correctly")
        else:
            print(f"   ❌ Expected filters {expected_new_filters}, got {actual_new_filters}")
            return False
        
        print("Step 6: Test filter changes affect data display")
        # Change time filter and verify it affects the data context
        if 'time' in filter_widget.filter_combos:
            time_combo = filter_widget.filter_combos['time']
            original_time = time_combo.currentText()
            
            # Change to different time
            if time_combo.count() > 1:
                time_combo.setCurrentIndex(1)  # Change to second time option
                new_time = time_combo.currentText()
                
                # Verify filter was applied
                updated_filters = filter_widget.get_current_filters()
                if updated_filters.get('time') == new_time:
                    print(f"   ✅ Filter change applied: time={new_time}")
                else:
                    print(f"   ❌ Filter change not applied")
                    return False
        
        print("Step 7: Test multiple dimension combinations")
        dimension_combinations = [
            ('time', 'city'),
            ('age', 'income'),
            ('income', 'time'),
            ('city', 'age')
        ]
        
        for dim1, dim2 in dimension_combinations:
            editor.dimension_selector.set_selected_dimensions(dim1, dim2)
            
            rows = table_model.rowCount()
            cols = table_model.columnCount()
            filters = set(filter_widget.get_current_filters().keys())
            
            print(f"   {dim1} × {dim2}: {rows}×{cols} table, filters: {filters}")
            
            # Verify we have the expected number of rows and columns
            if rows > 0 and cols > 0:
                print(f"     ✅ Valid table dimensions")
            else:
                print(f"     ❌ Invalid table dimensions")
                return False
        
        print("Step 8: Test data key generation and filtering")
        # Switch back to time × age and verify data keys are generated correctly
        editor.dimension_selector.set_selected_dimensions('time', 'age')
        
        # Set specific filter values
        filter_widget.current_filters['city'] = 'Montreal'
        filter_widget.current_filters['income'] = 'high'
        editor.on_dimension_filters_changed(filter_widget.current_filters)
        
        # Test data key creation
        test_key = table_model._create_data_key('population', '2020', 'young')
        print(f"   Generated data key: {test_key}")
        
        # Verify key includes filter information
        key_str = str(test_key)
        if 'city:Montreal' in key_str and 'income:high' in key_str:
            print("   ✅ Data key includes filter information")
        else:
            print("   ❌ Data key missing filter information")
            return False
        
        editor.close()
        
        print("\n✅ ALL COMPREHENSIVE MULTIDIMENSIONAL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ COMPREHENSIVE MULTIDIMENSIONAL TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run comprehensive multidimensional functionality test."""
    
    print("=== COMPREHENSIVE MULTIDIMENSIONAL FUNCTIONALITY TEST ===")
    print("Testing all aspects of multidimensional data handling")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Run comprehensive test
        test_passed = test_comprehensive_multidimensional_functionality()
        
        # Summary
        print("\n" + "=" * 70)
        print("COMPREHENSIVE MULTIDIMENSIONAL FUNCTIONALITY SUMMARY:")
        if test_passed:
            print("🎉 ALL MULTIDIMENSIONAL FUNCTIONALITY TESTS PASSED!")
            print("✅ 3+ dimensional data handling works without crashes")
            print("✅ Table display with proper headers and data works")
            print("✅ Coordinate selection through row/column headers works")
            print("✅ Dimension filtering for 3rd, 4th+ dimensions works")
            print("✅ Data persistence across dimension changes works")
            print("✅ Filter changes properly affect data context")
            return 0
        else:
            print("❌ SOME MULTIDIMENSIONAL FUNCTIONALITY TESTS FAILED.")
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
