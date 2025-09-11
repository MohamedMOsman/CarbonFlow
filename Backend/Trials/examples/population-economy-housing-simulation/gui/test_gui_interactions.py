#!/usr/bin/env python3
"""
Test script to investigate GUI interaction issues that might cause crashes
when working with temporal dimensions and dimension selector display.
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

def test_dimension_addition_dialog():
    """Test the dimension addition dialog with temporal dimensions."""
    
    print("\n🔍 DIMENSION ADDITION DIALOG TEST")
    print("=" * 50)
    
    try:
        from inspector.dimension_management import AddDimensionDialog
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create existing dimensions
        existing_dims = {
            'age': {
                'labels': ['young', 'old'],
                'description': 'Age groups',
                'type': 'categorical',
                'size': 2
            }
        }
        
        print("Step 1: Create AddDimensionDialog")
        dialog = AddDimensionDialog(existing_dims, None)
        print("   ✅ Dialog created successfully")
        
        print("Step 2: Test temporal dimension creation")
        # Simulate creating a temporal dimension
        dialog.name_edit.setText("test_time")
        dialog.description_edit.setPlainText("Test temporal dimension")
        
        # Set type to temporal
        temporal_index = dialog.type_combo.findText("temporal")
        if temporal_index >= 0:
            dialog.type_combo.setCurrentIndex(temporal_index)
            print("   ✅ Temporal type selected")
        else:
            print("   ❌ Temporal type not found in combo box")
            return False
        
        # Set manual entry mode
        dialog.manual_radio.setChecked(True)
        
        # Add some temporal labels
        dialog.labels_list.clear()
        temporal_labels = ['2020', '2021', '2022', '2023']
        for label in temporal_labels:
            dialog.add_label_item(label)
        
        print(f"   ✅ Added {len(temporal_labels)} temporal labels")
        
        print("Step 3: Test validation")
        # Test validation
        if dialog.validate_name():
            print("   ✅ Name validation passed")
        else:
            print("   ❌ Name validation failed")
            return False
        
        labels = dialog.get_labels()
        if labels:
            print(f"   ✅ Labels retrieved: {labels}")
        else:
            print("   ❌ No labels retrieved")
            return False
        
        print("Step 4: Test get_dimension_data")
        dimension_data = dialog.get_dimension_data()
        if dimension_data:
            print("   ✅ Dimension data created successfully")
            print(f"     Name: {dimension_data['name']}")
            print(f"     Type: {dimension_data['type']}")
            print(f"     Labels: {dimension_data['labels']}")
            print(f"     Size: {dimension_data['size']}")
        else:
            print("   ❌ Failed to create dimension data")
            return False
        
        print("Step 5: Test range generation for temporal")
        # Test range generation
        dialog.range_radio.setChecked(True)
        dialog.range_start_edit.setText("2020")
        dialog.range_end_edit.setText("2025")
        dialog.range_step_edit.setText("1")
        
        try:
            range_labels = dialog.generate_range_labels()
            print(f"   ✅ Range generation successful: {range_labels}")
        except Exception as e:
            print(f"   ❌ Range generation failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ DIMENSION ADDITION DIALOG TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dimension_selector_updates():
    """Test dimension selector updates and display refresh."""
    
    print("\n🔍 DIMENSION SELECTOR UPDATE TEST")
    print("=" * 50)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create model with temporal dimensions
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
                        'size': 2
                    }
                }
        
        component = ModelComponent(
            name="test_stock",
            component_type="stock",
            properties={
                'initial_value': 1000,
                'units': 'units',
                'spatial_dims': ['time', 'age'],
                'description': 'Test stock'
            }
        )
        
        print("Step 1: Create editor and check initial state")
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        selector = editor.dimension_selector
        print(f"   Initial available dimensions: {len(selector.available_dimensions)}")
        
        print("Step 2: Test dimension panel update")
        # Force update of dimensions panel
        selector.update_dimensions_panel()
        print("   ✅ Dimensions panel updated")
        
        print("Step 3: Test adding dimension through selector")
        # Simulate adding a new temporal dimension
        new_dim_data = {
            'name': 'new_temporal',
            'type': 'temporal',
            'description': 'New temporal dimension',
            'labels': ['2025', '2026'],
            'size': 2,
            'metadata': {
                'user_created': True,
                'creation_method': 'manual'
            }
        }
        
        # Add to available dimensions
        selector.available_dimensions['new_temporal'] = {
            'labels': new_dim_data['labels'],
            'description': new_dim_data['description'],
            'type': new_dim_data['type'],
            'size': new_dim_data['size'],
            'metadata': new_dim_data['metadata']
        }
        
        # Update UI
        selector.update_dimensions_panel()
        print("   ✅ New temporal dimension added to selector")
        
        # Emit dimension added signal
        selector.dimension_added.emit(new_dim_data)
        print("   ✅ Dimension added signal emitted")
        
        print("Step 4: Test dimension assignment with new temporal dimension")
        # Test assigning the new temporal dimension
        selector.set_selected_dimensions('new_temporal', 'age')
        
        x_dim = selector.x_axis_zone.current_dimension
        y_dim = selector.y_axis_zone.current_dimension
        print(f"   Assigned dimensions: Y={y_dim}, X={x_dim}")
        
        # Check display
        x_display = selector.x_axis_zone.dimension_display.text()
        y_display = selector.y_axis_zone.dimension_display.text()
        print(f"   Display texts: Y='{y_display}', X='{x_display}'")
        
        if x_display == 'age' and y_display == 'new_temporal':
            print("   ✅ Dimension display working correctly")
        else:
            print("   ❌ Dimension display not working correctly")
            return False
        
        print("Step 5: Test multiple dimension switches")
        # Test rapid dimension switching
        for i in range(3):
            if i % 2 == 0:
                selector.set_selected_dimensions('time', 'age')
            else:
                selector.set_selected_dimensions('new_temporal', 'time')
            
            x_display = selector.x_axis_zone.dimension_display.text()
            y_display = selector.y_axis_zone.dimension_display.text()
            print(f"   Switch {i+1}: Y='{y_display}', X='{x_display}'")
        
        print("   ✅ Multiple dimension switches completed")
        
        editor.close()
        return True
        
    except Exception as e:
        print(f"\n❌ DIMENSION SELECTOR UPDATE TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases that might cause crashes."""
    
    print("\n🔍 EDGE CASES TEST")
    print("=" * 50)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        print("Step 1: Test with empty temporal dimension")
        class MockModel1:
            def __init__(self):
                self.dimensions = {
                    'empty_time': {
                        'labels': [],
                        'description': 'Empty temporal dimension',
                        'type': 'temporal',
                        'size': 0
                    }
                }
        
        component1 = ModelComponent(
            name="test1",
            component_type="stock",
            properties={
                'initial_value': 100,
                'units': 'units',
                'spatial_dims': ['empty_time'],
                'description': 'Test with empty temporal'
            }
        )
        
        try:
            editor1 = SpreadsheetDataEditor([component1], MockModel1(), parent=None)
            print("   ✅ Empty temporal dimension handled")
            editor1.close()
        except Exception as e:
            print(f"   ❌ Empty temporal dimension failed: {str(e)}")
            return False
        
        print("Step 2: Test with malformed temporal labels")
        class MockModel2:
            def __init__(self):
                self.dimensions = {
                    'bad_time': {
                        'labels': ['not_a_year', 'also_not_year', '2020'],
                        'description': 'Mixed temporal labels',
                        'type': 'temporal',
                        'size': 3
                    }
                }
        
        component2 = ModelComponent(
            name="test2",
            component_type="stock",
            properties={
                'initial_value': 100,
                'units': 'units',
                'spatial_dims': ['bad_time'],
                'description': 'Test with mixed temporal labels'
            }
        )
        
        try:
            editor2 = SpreadsheetDataEditor([component2], MockModel2(), parent=None)
            print("   ✅ Mixed temporal labels handled")
            editor2.close()
        except Exception as e:
            print(f"   ❌ Mixed temporal labels failed: {str(e)}")
            return False
        
        print("Step 3: Test with None values")
        class MockModel3:
            def __init__(self):
                self.dimensions = {
                    'none_time': {
                        'labels': None,
                        'description': None,
                        'type': 'temporal',
                        'size': None
                    }
                }
        
        component3 = ModelComponent(
            name="test3",
            component_type="stock",
            properties={
                'initial_value': 100,
                'units': 'units',
                'spatial_dims': ['none_time'],
                'description': 'Test with None values'
            }
        )
        
        try:
            editor3 = SpreadsheetDataEditor([component3], MockModel3(), parent=None)
            print("   ✅ None values handled")
            editor3.close()
        except Exception as e:
            print(f"   ❌ None values failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ EDGE CASES TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all GUI interaction tests."""
    
    print("=== GUI INTERACTION CRASH INVESTIGATION ===")
    print("Testing specific GUI interactions that might cause crashes")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Run tests
        dialog_test_passed = test_dimension_addition_dialog()
        selector_test_passed = test_dimension_selector_updates()
        edge_cases_passed = test_edge_cases()
        
        # Summary
        print("\n" + "=" * 50)
        print("GUI INTERACTION TEST SUMMARY:")
        print(f"  Dimension Addition Dialog: {'✅ PASSED' if dialog_test_passed else '❌ FAILED'}")
        print(f"  Dimension Selector Updates: {'✅ PASSED' if selector_test_passed else '❌ FAILED'}")
        print(f"  Edge Cases: {'✅ PASSED' if edge_cases_passed else '❌ FAILED'}")
        
        if dialog_test_passed and selector_test_passed and edge_cases_passed:
            print("\n🎉 ALL GUI INTERACTION TESTS PASSED!")
            print("No crashes detected in GUI interactions.")
            return 0
        else:
            print("\n❌ SOME GUI INTERACTION TESTS FAILED.")
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
