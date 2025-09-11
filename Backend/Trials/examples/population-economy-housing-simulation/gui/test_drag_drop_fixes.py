#!/usr/bin/env python3
"""
Test script to verify drag-and-drop fixes work correctly without crashes.
This tests the error handling and robustness improvements made to the drag-and-drop system.
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

def test_drag_drop_error_handling():
    """Test drag-and-drop error handling and robustness."""
    
    print("\n🔍 TESTING DRAG-AND-DROP ERROR HANDLING")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        from inspector.dimension_management import DraggableDimensionItem, DropZone
        
        # Create model with dimensions
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
            name="population",
            component_type="stock",
            properties={
                'initial_value': 1000,
                'units': 'people',
                'spatial_dims': ['time', 'age', 'city'],
                'description': 'Population by time, age, and city'
            }
        )
        
        print("Step 1: Create editor and test normal operation")
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        print("   ✅ Editor created successfully")
        
        dimension_selector = editor.dimension_selector
        
        print("Step 2: Test normal dimension dropping")
        try:
            # Test normal dimension assignment
            dimension_selector.on_dimension_dropped("x_axis", "time")
            dimension_selector.on_dimension_dropped("y_axis", "age")
            
            x_dim = dimension_selector.x_axis_zone.current_dimension
            y_dim = dimension_selector.y_axis_zone.current_dimension
            
            print(f"   Normal assignment: X={x_dim}, Y={y_dim}")
            
            if x_dim == "time" and y_dim == "age":
                print("   ✅ Normal dimension dropping works")
            else:
                print("   ❌ Normal dimension dropping failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Normal dimension dropping failed: {str(e)}")
            return False
        
        print("Step 3: Test error conditions")
        
        # Test with None dimension name
        try:
            dimension_selector.on_dimension_dropped("x_axis", None)
            print("   ✅ None dimension name handled gracefully")
        except Exception as e:
            print(f"   ❌ None dimension name caused crash: {str(e)}")
            return False
        
        # Test with empty string dimension name
        try:
            dimension_selector.on_dimension_dropped("y_axis", "")
            print("   ✅ Empty dimension name handled gracefully")
        except Exception as e:
            print(f"   ❌ Empty dimension name caused crash: {str(e)}")
            return False
        
        # Test with invalid dimension name
        try:
            dimension_selector.on_dimension_dropped("x_axis", "invalid_dimension")
            print("   ✅ Invalid dimension name handled gracefully")
        except Exception as e:
            print(f"   ❌ Invalid dimension name caused crash: {str(e)}")
            return False
        
        # Test with invalid zone name
        try:
            dimension_selector.on_dimension_dropped("invalid_zone", "time")
            print("   ✅ Invalid zone name handled gracefully")
        except Exception as e:
            print(f"   ❌ Invalid zone name caused crash: {str(e)}")
            return False
        
        # Test with None zone name
        try:
            dimension_selector.on_dimension_dropped(None, "time")
            print("   ✅ None zone name handled gracefully")
        except Exception as e:
            print(f"   ❌ None zone name caused crash: {str(e)}")
            return False
        
        print("Step 4: Test DropZone error handling")
        
        # Test drop zone with invalid dimension
        try:
            drop_zone = DropZone("test_zone", "Test Zone")
            drop_zone.set_dimension(None)
            drop_zone.set_dimension("")
            drop_zone.set_dimension("invalid_dimension")
            print("   ✅ DropZone error handling works")
        except Exception as e:
            print(f"   ❌ DropZone error handling failed: {str(e)}")
            return False
        
        print("Step 5: Test dimension change with problematic data")
        
        # Test dimension change with empty coordinates
        try:
            # Create a dimension with empty labels
            dimension_selector.available_dimensions['empty_dim'] = {
                'labels': [],
                'description': 'Empty dimension',
                'size': 0
            }
            
            # Try to use the empty dimension
            dimension_selector.on_dimension_dropped("x_axis", "empty_dim")
            print("   ✅ Empty dimension coordinates handled gracefully")
            
        except Exception as e:
            print(f"   ❌ Empty dimension coordinates caused crash: {str(e)}")
            return False
        
        # Test dimension change with None labels
        try:
            dimension_selector.available_dimensions['none_labels'] = {
                'labels': None,
                'description': 'None labels dimension',
                'size': 0
            }
            
            dimension_selector.on_dimension_dropped("y_axis", "none_labels")
            print("   ✅ None labels handled gracefully")
            
        except Exception as e:
            print(f"   ❌ None labels caused crash: {str(e)}")
            return False
        
        print("Step 6: Test table model updates with problematic data")
        
        try:
            # Force a dimension change that might cause issues
            editor._apply_dimension_change("empty_dim", "none_labels")
            print("   ✅ Problematic dimension change handled gracefully")
            
        except Exception as e:
            print(f"   ❌ Problematic dimension change caused crash: {str(e)}")
            return False
        
        editor.close()
        
        print("\n✅ ALL DRAG-AND-DROP ERROR HANDLING TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ DRAG-AND-DROP ERROR HANDLING TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run drag-and-drop robustness tests."""
    
    print("=== DRAG-AND-DROP ROBUSTNESS TESTING ===")
    print("Testing error handling and crash prevention in drag-and-drop functionality")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Run test
        test_passed = test_drag_drop_error_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("DRAG-AND-DROP ROBUSTNESS TEST SUMMARY:")
        if test_passed:
            print("🎉 ALL DRAG-AND-DROP ROBUSTNESS TESTS PASSED!")
            print("✅ Error handling prevents crashes")
            print("✅ Invalid inputs handled gracefully")
            print("✅ Edge cases managed properly")
            print("✅ Drag-and-drop system is robust")
        else:
            print("❌ SOME DRAG-AND-DROP ROBUSTNESS TESTS FAILED.")
            print("There may still be crash conditions in the drag-and-drop system.")
        
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
