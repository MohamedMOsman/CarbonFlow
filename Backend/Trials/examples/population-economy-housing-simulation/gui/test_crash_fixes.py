#!/usr/bin/env python3
"""
Test script to validate the fixes for temporal dimension crashes
and dimension selector display issues.
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

def test_temporal_dimension_robustness():
    """Test temporal dimension handling with various edge cases."""
    
    print("\n🔍 TEMPORAL DIMENSION ROBUSTNESS TEST")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Test cases with various edge cases
        test_cases = [
            {
                'name': 'normal_temporal',
                'dimensions': {
                    'time': {
                        'labels': ['2020', '2021', '2022'],
                        'description': 'Normal temporal dimension',
                        'type': 'temporal',
                        'size': 3
                    }
                }
            },
            {
                'name': 'empty_temporal',
                'dimensions': {
                    'empty_time': {
                        'labels': [],
                        'description': 'Empty temporal dimension',
                        'type': 'temporal',
                        'size': 0
                    }
                }
            },
            {
                'name': 'none_values',
                'dimensions': {
                    'none_time': {
                        'labels': None,
                        'description': None,
                        'type': 'temporal',
                        'size': None
                    }
                }
            },
            {
                'name': 'mixed_labels',
                'dimensions': {
                    'mixed_time': {
                        'labels': ['2020', 'not_a_year', '2022', None, 123],
                        'description': 'Mixed temporal labels',
                        'type': 'temporal',
                        'size': 5
                    }
                }
            },
            {
                'name': 'auto_detect_temporal',
                'dimensions': {
                    'year_auto': {
                        'labels': ['2020', '2021', '2022'],
                        'description': 'Auto-detected temporal',
                        # No explicit type - should be auto-detected
                        'size': 3
                    },
                    'time_10yr_auto': {
                        'labels': ['2020_10yr', '2030_10yr'],
                        'description': 'Auto-detected decadal',
                        'size': 2
                    }
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest Case {i+1}: {test_case['name']}")
            
            try:
                # Create mock model
                class MockModel:
                    def __init__(self, dimensions):
                        self.dimensions = dimensions
                
                # Create component
                spatial_dims = list(test_case['dimensions'].keys())
                component = ModelComponent(
                    name=f"test_{test_case['name']}",
                    component_type="stock",
                    properties={
                        'initial_value': 1000,
                        'units': 'units',
                        'spatial_dims': spatial_dims,
                        'description': f'Test component for {test_case["name"]}'
                    }
                )
                
                # Create editor
                mock_model = MockModel(test_case['dimensions'])
                editor = SpreadsheetDataEditor([component], mock_model, parent=None)
                
                print(f"   ✅ Editor created successfully")
                
                # Check dimension conversion
                available_dims = editor.dimension_selector.available_dimensions
                print(f"   Available dimensions: {len(available_dims)}")
                
                for dim_name, dim_data in available_dims.items():
                    dim_type = dim_data.get('type', 'unknown')
                    labels = dim_data.get('labels', [])
                    print(f"     {dim_name}: type='{dim_type}', labels={len(labels)} items")
                
                # Test dimension assignment if we have at least one dimension
                if len(available_dims) >= 1:
                    dim_names = list(available_dims.keys())
                    if len(dim_names) >= 2:
                        editor.dimension_selector.set_selected_dimensions(dim_names[0], dim_names[1])
                    else:
                        # Create a dummy dimension for testing
                        editor.dimension_selector.available_dimensions['dummy'] = {
                            'labels': ['a', 'b'],
                            'type': 'categorical',
                            'size': 2,
                            'description': 'Dummy dimension'
                        }
                        editor.dimension_selector.set_selected_dimensions(dim_names[0], 'dummy')
                    
                    # Check display
                    x_display = editor.dimension_selector.x_axis_zone.dimension_display.text()
                    y_display = editor.dimension_selector.y_axis_zone.dimension_display.text()
                    print(f"   Display: Y='{y_display}', X='{x_display}'")
                
                editor.close()
                print(f"   ✅ Test case {test_case['name']} passed")
                
            except Exception as e:
                print(f"   ❌ Test case {test_case['name']} failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        
        print(f"\n✅ ALL TEMPORAL DIMENSION ROBUSTNESS TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ TEMPORAL DIMENSION ROBUSTNESS TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dimension_addition_workflow():
    """Test the complete dimension addition workflow."""
    
    print("\n🔍 DIMENSION ADDITION WORKFLOW TEST")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create basic model
        class MockModel:
            def __init__(self):
                self.dimensions = {
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
                'spatial_dims': ['age'],
                'description': 'Test stock'
            }
        )
        
        print("Step 1: Create editor with basic model")
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        initial_dims = len(editor.dimension_selector.available_dimensions)
        print(f"   Initial dimensions: {initial_dims}")
        
        print("Step 2: Add new temporal dimension programmatically")
        # Simulate adding a new temporal dimension
        new_temporal_dim = {
            'name': 'test_time',
            'type': 'temporal',
            'description': 'Test temporal dimension',
            'labels': ['2020', '2021', '2022'],
            'size': 3,
            'metadata': {
                'user_created': True,
                'creation_method': 'manual'
            }
        }
        
        # Add to available dimensions
        editor.dimension_selector.available_dimensions['test_time'] = {
            'labels': new_temporal_dim['labels'],
            'description': new_temporal_dim['description'],
            'type': new_temporal_dim['type'],
            'size': new_temporal_dim['size'],
            'metadata': new_temporal_dim['metadata']
        }
        
        # Update UI
        editor.dimension_selector.update_dimensions_panel()
        
        # Trigger dimension added signal
        editor.on_dimension_added(new_temporal_dim)
        
        final_dims = len(editor.dimension_selector.available_dimensions)
        print(f"   Final dimensions: {final_dims}")
        
        if final_dims > initial_dims:
            print("   ✅ Dimension added successfully")
        else:
            print("   ❌ Dimension not added")
            return False
        
        print("Step 3: Test dimension assignment with new temporal dimension")
        editor.dimension_selector.set_selected_dimensions('test_time', 'age')
        
        x_display = editor.dimension_selector.x_axis_zone.dimension_display.text()
        y_display = editor.dimension_selector.y_axis_zone.dimension_display.text()
        print(f"   Display after assignment: Y='{y_display}', X='{x_display}'")
        
        if y_display == 'test_time' and x_display == 'age':
            print("   ✅ Dimension assignment and display working correctly")
        else:
            print("   ❌ Dimension assignment or display not working")
            return False
        
        print("Step 4: Test multiple dimension switches")
        # Test rapid switching
        for i in range(3):
            if i % 2 == 0:
                editor.dimension_selector.set_selected_dimensions('age', 'test_time')
            else:
                editor.dimension_selector.set_selected_dimensions('test_time', 'age')
            
            x_display = editor.dimension_selector.x_axis_zone.dimension_display.text()
            y_display = editor.dimension_selector.y_axis_zone.dimension_display.text()
            print(f"   Switch {i+1}: Y='{y_display}', X='{x_display}'")
        
        print("   ✅ Multiple dimension switches completed")
        
        editor.close()
        
        print(f"\n✅ DIMENSION ADDITION WORKFLOW TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ DIMENSION ADDITION WORKFLOW TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_display_consistency():
    """Test that dimension display remains consistent."""
    
    print("\n🔍 DIMENSION DISPLAY CONSISTENCY TEST")
    print("=" * 60)
    
    try:
        from inspector.dimension_management import DropZone
        
        print("Step 1: Test DropZone display directly")
        
        # Test normal case
        zone1 = DropZone("test", "Test Zone")
        zone1.set_dimension("normal_dim")
        display1 = zone1.dimension_display.text()
        print(f"   Normal dimension: '{display1}'")
        
        # Test None case
        zone2 = DropZone("test2", "Test Zone 2")
        zone2.set_dimension(None)
        display2 = zone2.dimension_display.text()
        print(f"   None dimension: '{display2}'")
        
        # Test empty string case
        zone3 = DropZone("test3", "Test Zone 3")
        zone3.set_dimension("")
        display3 = zone3.dimension_display.text()
        print(f"   Empty dimension: '{display3}'")
        
        # Test with special characters
        zone4 = DropZone("test4", "Test Zone 4")
        zone4.set_dimension("time_10yr")
        display4 = zone4.dimension_display.text()
        print(f"   Special chars dimension: '{display4}'")
        
        # Verify expected results
        if (display1 == "normal_dim" and 
            display2 == "Drop dimension here" and 
            display3 == "Drop dimension here" and 
            display4 == "time_10yr"):
            print("   ✅ All DropZone display tests passed")
            return True
        else:
            print("   ❌ Some DropZone display tests failed")
            return False
        
    except Exception as e:
        print(f"\n❌ DIMENSION DISPLAY CONSISTENCY TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all crash and display fix validation tests."""
    
    print("=== CRASH AND DISPLAY FIXES VALIDATION ===")
    print("Testing fixes for temporal dimension crashes and display issues")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Run tests
        robustness_passed = test_temporal_dimension_robustness()
        workflow_passed = test_dimension_addition_workflow()
        display_passed = test_display_consistency()
        
        # Summary
        print("\n" + "=" * 60)
        print("CRASH AND DISPLAY FIXES VALIDATION SUMMARY:")
        print(f"  Temporal Dimension Robustness: {'✅ PASSED' if robustness_passed else '❌ FAILED'}")
        print(f"  Dimension Addition Workflow: {'✅ PASSED' if workflow_passed else '❌ FAILED'}")
        print(f"  Display Consistency: {'✅ PASSED' if display_passed else '❌ FAILED'}")
        
        if robustness_passed and workflow_passed and display_passed:
            print("\n🎉 ALL CRASH AND DISPLAY FIX TESTS PASSED!")
            print("The temporal dimension crashes and display issues have been resolved.")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED.")
            print("There may still be issues with the fixes.")
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
