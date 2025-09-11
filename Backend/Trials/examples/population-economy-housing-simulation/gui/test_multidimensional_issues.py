#!/usr/bin/env python3
"""
Test script to reproduce and investigate the multidimensional spreadsheet editor issues:
1. GUI crash with 3+ dimensional data
2. Spreadsheet display problems
3. Dimension coordinate selection not working
4. Dimension filtering not functional
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

def test_3d_data_crash():
    """Test GUI crash with 3+ dimensional data."""
    
    print("\n🔍 TESTING 3+ DIMENSIONAL DATA CRASH")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create model with 4 dimensions
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
        
        print("Step 2: Check available dimensions")
        available_dims = editor.dimension_selector.available_dimensions
        print(f"   Available dimensions: {len(available_dims)}")
        for dim_name, dim_data in available_dims.items():
            print(f"     {dim_name}: {len(dim_data.get('labels', []))} labels")
        
        print("Step 3: Test dimension assignment")
        editor.dimension_selector.set_selected_dimensions('time', 'age')
        print("   ✅ Dimension assignment successful")
        
        print("Step 4: Check table model state")
        table_model = editor.table_model
        print(f"   Table dimensions: {table_model.dimension_1} × {table_model.dimension_2}")
        print(f"   Row count: {table_model.rowCount()}")
        print(f"   Column count: {table_model.columnCount()}")
        
        print("Step 5: Check dimension filters")
        filter_widget = editor.dimension_filters
        current_filters = filter_widget.get_current_filters()
        print(f"   Available filters: {list(current_filters.keys())}")
        print(f"   Filter widget visible: {filter_widget.isVisible()}")
        
        print("Step 6: Check table view visibility")
        table_view = editor.table_view
        print(f"   Table view visible: {table_view.isVisible()}")
        print(f"   Table view size: {table_view.size()}")
        print(f"   Table model set: {table_view.model() is not None}")
        
        editor.close()
        
        print("\n✅ 3+ DIMENSIONAL DATA TEST COMPLETED")
        return True
        
    except Exception as e:
        print(f"\n❌ 3+ DIMENSIONAL DATA TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_spreadsheet_display():
    """Test spreadsheet display problems."""
    
    print("\n🔍 TESTING SPREADSHEET DISPLAY")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create simple 3D model
        class MockModel:
            def __init__(self):
                self.dimensions = {
                    'time': {
                        'labels': ['2020', '2021'],
                        'description': 'Time periods',
                        'size': 2
                    },
                    'age': {
                        'labels': ['young', 'old'],
                        'description': 'Age groups',
                        'size': 2
                    },
                    'city': {
                        'labels': ['Montreal', 'Toronto'],
                        'description': 'Cities',
                        'size': 2
                    }
                }
        
        component = ModelComponent(
            name="test_stock",
            component_type="stock",
            properties={
                'initial_value': 100,
                'units': 'units',
                'spatial_dims': ['time', 'age', 'city'],
                'description': 'Test stock with 3 dimensions'
            }
        )
        
        print("Step 1: Create editor")
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        print("Step 2: Set dimensions and check table")
        editor.dimension_selector.set_selected_dimensions('time', 'age')
        
        # Check table model
        table_model = editor.table_model
        print(f"   Table model components: {len(table_model.components)}")
        print(f"   Table model dimensions: {table_model.dimension_1} × {table_model.dimension_2}")
        print(f"   Row headers: {table_model.headers_vertical}")
        print(f"   Column headers: {table_model.headers_horizontal}")
        
        # Check table view
        table_view = editor.table_view
        print(f"   Table view model: {table_view.model() is not None}")
        print(f"   Table view visible: {table_view.isVisible()}")
        
        # Try to add some data
        print("Step 3: Test data entry")
        if table_model.rowCount() > 0 and table_model.columnCount() > 0:
            from PyQt6.QtCore import Qt
            index = table_model.index(0, 0)
            success = table_model.setData(index, 123.45, Qt.ItemDataRole.EditRole)
            print(f"   Data entry successful: {success}")

            # Check if data was stored
            stored_value = table_model.data(index, Qt.ItemDataRole.DisplayRole)
            print(f"   Stored value: {stored_value}")
        else:
            print("   ❌ Table has no rows or columns")
        
        editor.close()
        
        print("\n✅ SPREADSHEET DISPLAY TEST COMPLETED")
        return True
        
    except Exception as e:
        print(f"\n❌ SPREADSHEET DISPLAY TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dimension_filtering():
    """Test dimension filtering functionality."""
    
    print("\n🔍 TESTING DIMENSION FILTERING")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create 4D model for filtering test
        class MockModel:
            def __init__(self):
                self.dimensions = {
                    'time': {
                        'labels': ['2020', '2021'],
                        'description': 'Time periods',
                        'size': 2
                    },
                    'age': {
                        'labels': ['young', 'old'],
                        'description': 'Age groups',
                        'size': 2
                    },
                    'city': {
                        'labels': ['Montreal', 'Toronto'],
                        'description': 'Cities',
                        'size': 2
                    },
                    'income': {
                        'labels': ['low', 'high'],
                        'description': 'Income levels',
                        'size': 2
                    }
                }
        
        component = ModelComponent(
            name="population",
            component_type="stock",
            properties={
                'initial_value': 1000,
                'units': 'people',
                'spatial_dims': ['time', 'age', 'city', 'income'],
                'description': 'Population with 4 dimensions'
            }
        )
        
        print("Step 1: Create editor with 4D data")
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        print("Step 2: Set 2 dimensions for display")
        editor.dimension_selector.set_selected_dimensions('time', 'age')
        
        print("Step 3: Check dimension filters")
        filter_widget = editor.dimension_filters
        print(f"   Filter widget visible: {filter_widget.isVisible()}")
        print(f"   Filter combos: {len(filter_widget.filter_combos)}")
        
        current_filters = filter_widget.get_current_filters()
        print(f"   Current filters: {current_filters}")
        
        # Test filter changes
        print("Step 4: Test filter changes")
        if filter_widget.filter_combos:
            for dim_name, combo in filter_widget.filter_combos.items():
                print(f"   Filter {dim_name}: {combo.count()} items")
                if combo.count() > 1:
                    # Change filter value
                    combo.setCurrentIndex(1)
                    new_filters = filter_widget.get_current_filters()
                    print(f"   Changed {dim_name} filter to: {new_filters.get(dim_name)}")
        
        # Check if filter changes affect table
        print("Step 5: Check table after filter changes")
        table_model = editor.table_model
        filters = table_model.get_dimension_filters()
        print(f"   Table model filters: {filters}")
        
        editor.close()
        
        print("\n✅ DIMENSION FILTERING TEST COMPLETED")
        return True
        
    except Exception as e:
        print(f"\n❌ DIMENSION FILTERING TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all multidimensional issue tests."""
    
    print("=== MULTIDIMENSIONAL SPREADSHEET EDITOR ISSUES INVESTIGATION ===")
    print("Testing for crashes, display problems, and functionality issues")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        app = QApplication([])
        
        # Run tests
        crash_test_passed = test_3d_data_crash()
        display_test_passed = test_spreadsheet_display()
        filtering_test_passed = test_dimension_filtering()
        
        # Summary
        print("\n" + "=" * 60)
        print("MULTIDIMENSIONAL ISSUES INVESTIGATION SUMMARY:")
        print(f"  3+ Dimensional Data Crash Test: {'✅ PASSED' if crash_test_passed else '❌ FAILED'}")
        print(f"  Spreadsheet Display Test: {'✅ PASSED' if display_test_passed else '❌ FAILED'}")
        print(f"  Dimension Filtering Test: {'✅ PASSED' if filtering_test_passed else '❌ FAILED'}")
        
        if crash_test_passed and display_test_passed and filtering_test_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("No critical issues detected in basic testing.")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED.")
            print("Critical issues detected that need to be fixed.")
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
