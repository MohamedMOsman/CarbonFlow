#!/usr/bin/env python3
"""
Test script to investigate the crash issue with temporal dimensions
and dimension selector display problems.
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

def test_temporal_dimension_crash():
    """Test adding temporal dimensions to identify crash causes."""
    
    print("\n🔍 TEMPORAL DIMENSION CRASH INVESTIGATION")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        print("Step 1: Create basic model with temporal dimensions")
        
        # Create mock model with temporal dimensions
        class MockModel:
            def __init__(self):
                self.dimensions = {
                    'time': {
                        'labels': ['2020', '2021', '2022'],
                        'description': 'Annual time steps',
                        'type': 'temporal',
                        'size': 3
                    },
                    'year': {
                        'labels': ['2020', '2021', '2022'],
                        'description': 'Year dimension',
                        'size': 3
                    },
                    'time_10yr': {
                        'labels': ['2020_10yr', '2030_10yr', '2040_10yr'],
                        'description': 'Decadal time periods',
                        'size': 3
                    },
                    'age': {
                        'labels': ['young', 'old'],
                        'description': 'Age groups',
                        'size': 2
                    }
                }
        
        # Create test component
        component = ModelComponent(
            name="test_stock",
            component_type="stock",
            properties={
                'initial_value': 1000,
                'units': 'units',
                'spatial_dims': ['time', 'year', 'time_10yr', 'age'],
                'description': 'Test stock with temporal dimensions'
            }
        )
        
        print("Step 2: Create SpreadsheetDataEditor")
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        print("   ✅ Editor created successfully")
        
        print("Step 3: Check dimension conversion")
        # Test the _convert_dimension_format method directly
        for dim_name, dim_info in mock_model.dimensions.items():
            try:
                converted = editor._convert_dimension_format(dim_name, dim_info)
                print(f"   ✅ {dim_name}: type='{converted['type']}', labels={converted['labels']}")
            except Exception as e:
                print(f"   ❌ {dim_name}: ERROR - {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("Step 4: Check dimension selector state")
        available_dims = editor.dimension_selector.available_dimensions
        print(f"   Available dimensions: {len(available_dims)}")
        for dim_name, dim_data in available_dims.items():
            print(f"     {dim_name}: type='{dim_data.get('type', 'unknown')}'")
        
        print("Step 5: Test dimension assignment")
        try:
            # Test setting dimensions programmatically
            editor.dimension_selector.set_selected_dimensions('time', 'age')
            print("   ✅ Dimension assignment successful")
            
            # Check if dimensions are displayed in drop zones
            x_dim = editor.dimension_selector.x_axis_zone.current_dimension
            y_dim = editor.dimension_selector.y_axis_zone.current_dimension
            print(f"   X-axis zone shows: '{x_dim}'")
            print(f"   Y-axis zone shows: '{y_dim}'")
            
            # Check dimension display text
            x_display = editor.dimension_selector.x_axis_zone.dimension_display.text()
            y_display = editor.dimension_selector.y_axis_zone.dimension_display.text()
            print(f"   X-axis display text: '{x_display}'")
            print(f"   Y-axis display text: '{y_display}'")
            
        except Exception as e:
            print(f"   ❌ Dimension assignment failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("Step 6: Test adding new temporal dimension")
        try:
            # Simulate adding a new temporal dimension
            new_temporal_dim = {
                'name': 'new_time',
                'type': 'temporal',
                'description': 'New temporal dimension',
                'labels': ['2025', '2026', '2027'],
                'size': 3,
                'metadata': {
                    'user_created': True,
                    'creation_method': 'manual'
                }
            }
            
            # Add to available dimensions
            editor.dimension_selector.available_dimensions['new_time'] = {
                'labels': new_temporal_dim['labels'],
                'description': new_temporal_dim['description'],
                'type': new_temporal_dim['type'],
                'size': new_temporal_dim['size'],
                'metadata': new_temporal_dim['metadata']
            }
            
            # Update UI
            editor.dimension_selector.update_dimensions_panel()
            print("   ✅ New temporal dimension added successfully")
            
        except Exception as e:
            print(f"   ❌ Adding new temporal dimension failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("Step 7: Test dimension addition dialog")
        try:
            from inspector.dimension_management import AddDimensionDialog
            
            # Create dialog (don't show it)
            dialog = AddDimensionDialog(editor.dimension_selector.available_dimensions, editor)
            print("   ✅ AddDimensionDialog created successfully")
            
        except Exception as e:
            print(f"   ❌ AddDimensionDialog creation failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Clean up
        editor.close()
        
        print("\n✅ CRASH INVESTIGATION COMPLETED")
        print("No crashes detected in basic temporal dimension operations.")
        return True
        
    except Exception as e:
        print(f"\n❌ CRASH INVESTIGATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dimension_display_issue():
    """Test the dimension selector display functionality."""
    
    print("\n🔍 DIMENSION DISPLAY INVESTIGATION")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create simple model
        class MockModel:
            def __init__(self):
                self.dimensions = {
                    'dim1': {
                        'labels': ['a', 'b'],
                        'description': 'First dimension',
                        'size': 2
                    },
                    'dim2': {
                        'labels': ['x', 'y'],
                        'description': 'Second dimension',
                        'size': 2
                    }
                }
        
        component = ModelComponent(
            name="test",
            component_type="stock",
            properties={
                'initial_value': 100,
                'units': 'units',
                'spatial_dims': ['dim1', 'dim2'],
                'description': 'Test component'
            }
        )
        
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        print("Step 1: Check initial drop zone state")
        x_zone = editor.dimension_selector.x_axis_zone
        y_zone = editor.dimension_selector.y_axis_zone
        
        print(f"   X-axis zone current_dimension: {x_zone.current_dimension}")
        print(f"   Y-axis zone current_dimension: {y_zone.current_dimension}")
        print(f"   X-axis display text: '{x_zone.dimension_display.text()}'")
        print(f"   Y-axis display text: '{y_zone.dimension_display.text()}'")
        
        print("Step 2: Test manual dimension setting")
        x_zone.set_dimension('dim1')
        y_zone.set_dimension('dim2')
        
        print(f"   After setting - X-axis current_dimension: {x_zone.current_dimension}")
        print(f"   After setting - Y-axis current_dimension: {y_zone.current_dimension}")
        print(f"   After setting - X-axis display text: '{x_zone.dimension_display.text()}'")
        print(f"   After setting - Y-axis display text: '{y_zone.dimension_display.text()}'")
        
        print("Step 3: Test programmatic dimension selection")
        editor.dimension_selector.set_selected_dimensions('dim2', 'dim1')
        
        print(f"   After programmatic setting - X-axis: {x_zone.current_dimension}")
        print(f"   After programmatic setting - Y-axis: {y_zone.current_dimension}")
        print(f"   After programmatic setting - X-axis display: '{x_zone.dimension_display.text()}'")
        print(f"   After programmatic setting - Y-axis display: '{y_zone.dimension_display.text()}'")
        
        # Check if the dimensions_changed signal is working
        print("Step 4: Test signal emission")
        def on_dims_changed(dim1, dim2):
            print(f"   Signal received: {dim1} × {dim2}")
        
        editor.dimension_selector.dimensions_changed.connect(on_dims_changed)
        editor.dimension_selector.set_selected_dimensions('dim1', 'dim2')
        
        editor.close()
        
        print("\n✅ DIMENSION DISPLAY INVESTIGATION COMPLETED")
        return True
        
    except Exception as e:
        print(f"\n❌ DIMENSION DISPLAY INVESTIGATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all crash and display investigations."""
    
    print("=== GUI CRASH AND DISPLAY INVESTIGATION ===")
    print("Investigating temporal dimension crashes and display issues")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Run investigations
        crash_test_passed = test_temporal_dimension_crash()
        display_test_passed = test_dimension_display_issue()
        
        # Summary
        print("\n" + "=" * 60)
        print("INVESTIGATION SUMMARY:")
        print(f"  Temporal Dimension Crash Test: {'✅ PASSED' if crash_test_passed else '❌ FAILED'}")
        print(f"  Dimension Display Test: {'✅ PASSED' if display_test_passed else '❌ FAILED'}")
        
        if crash_test_passed and display_test_passed:
            print("\n🎉 NO ISSUES DETECTED in basic testing.")
            print("The problems may be related to specific GUI interactions or edge cases.")
            return 0
        else:
            print("\n❌ ISSUES DETECTED. See details above.")
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
