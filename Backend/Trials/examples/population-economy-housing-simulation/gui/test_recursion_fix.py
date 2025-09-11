#!/usr/bin/env python3
"""
Test script to verify the recursion fix for drag-and-drop functionality.
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

def test_recursion_fix():
    """Test that the recursion fix prevents infinite loops."""
    
    print("\n🔍 TESTING RECURSION FIX")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create model with multiple dimensions
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
                    }
                }
        
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
        
        print("Step 1: Create editor")
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        print("   ✅ Editor created successfully")
        
        dimension_selector = editor.dimension_selector
        
        print("Step 2: Test dimension dropping (should not cause recursion)")
        try:
            # Test dimension dropping - this previously caused recursion
            dimension_selector.on_dimension_dropped("x_axis", "time")
            print("   ✅ First dimension drop completed without recursion")
            
            dimension_selector.on_dimension_dropped("y_axis", "age")
            print("   ✅ Second dimension drop completed without recursion")
            
            # Verify dimensions were set correctly
            x_dim = dimension_selector.x_axis_zone.current_dimension
            y_dim = dimension_selector.y_axis_zone.current_dimension
            
            print(f"   Final dimensions: X={x_dim}, Y={y_dim}")
            
            if x_dim == "time" and y_dim == "age":
                print("   ✅ Dimensions set correctly")
            else:
                print("   ❌ Dimensions not set correctly")
                return False
                
        except RecursionError as e:
            print(f"   ❌ Recursion error still occurs: {str(e)}")
            return False
        except Exception as e:
            print(f"   ❌ Other error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("Step 3: Test programmatic dimension setting")
        try:
            # Test set_selected_dimensions - this also previously caused recursion
            dimension_selector.set_selected_dimensions("city", "time")
            print("   ✅ Programmatic dimension setting completed without recursion")
            
            # Verify dimensions were set correctly
            x_dim = dimension_selector.x_axis_zone.current_dimension
            y_dim = dimension_selector.y_axis_zone.current_dimension
            
            print(f"   Final dimensions: X={x_dim}, Y={y_dim}")
            
            if x_dim == "time" and y_dim == "city":
                print("   ✅ Programmatic dimensions set correctly")
            else:
                print("   ❌ Programmatic dimensions not set correctly")
                return False
                
        except RecursionError as e:
            print(f"   ❌ Recursion error still occurs in programmatic setting: {str(e)}")
            return False
        except Exception as e:
            print(f"   ❌ Other error occurred in programmatic setting: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("Step 4: Test multiple rapid dimension changes")
        try:
            # Test rapid dimension changes that could trigger recursion
            for i in range(5):
                dim1 = ['time', 'age', 'city'][i % 3]
                dim2 = ['city', 'time', 'age'][i % 3]
                
                if dim1 != dim2:  # Avoid setting same dimension to both axes
                    dimension_selector.on_dimension_dropped("x_axis", dim1)
                    dimension_selector.on_dimension_dropped("y_axis", dim2)
                    print(f"   ✅ Rapid change {i+1}: {dim1} × {dim2}")
            
            print("   ✅ Multiple rapid changes completed without recursion")
            
        except RecursionError as e:
            print(f"   ❌ Recursion error in rapid changes: {str(e)}")
            return False
        except Exception as e:
            print(f"   ❌ Other error in rapid changes: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("Step 5: Test recursion flag state")
        try:
            # Verify the recursion flag is properly reset
            if hasattr(dimension_selector, '_updating_dimensions'):
                if dimension_selector._updating_dimensions:
                    print("   ❌ Recursion flag not properly reset")
                    return False
                else:
                    print("   ✅ Recursion flag properly reset")
            else:
                print("   ❌ Recursion flag not found")
                return False
                
        except Exception as e:
            print(f"   ❌ Error checking recursion flag: {str(e)}")
            return False
        
        editor.close()
        
        print("\n✅ ALL RECURSION FIX TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ RECURSION FIX TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run recursion fix test."""
    
    print("=== DRAG-AND-DROP RECURSION FIX TEST ===")
    print("Testing that the recursion fix prevents infinite loops")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Run test
        test_passed = test_recursion_fix()
        
        # Summary
        print("\n" + "=" * 60)
        print("RECURSION FIX TEST SUMMARY:")
        if test_passed:
            print("🎉 RECURSION FIX SUCCESSFUL!")
            print("✅ Drag-and-drop no longer causes infinite recursion")
            print("✅ Dimension changes work correctly")
            print("✅ Recursion prevention flag works properly")
        else:
            print("❌ RECURSION FIX FAILED.")
            print("There are still recursion issues in the drag-and-drop system.")
        
        return 0 if test_passed else 1
            
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
