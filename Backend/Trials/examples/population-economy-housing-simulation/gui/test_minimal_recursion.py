#!/usr/bin/env python3
"""
Minimal test to isolate the recursion issue in drag-and-drop functionality.
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

def test_minimal_dimension_selector():
    """Test just the dimension selector without the full editor."""
    
    print("\n🔍 TESTING MINIMAL DIMENSION SELECTOR")
    print("=" * 60)
    
    try:
        # Suppress Qt warnings for headless testing
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        from inspector.spreadsheet_editor import EnhancedDimensionSelector
        
        print("Step 1: Create dimension selector")
        selector = EnhancedDimensionSelector()
        print("   ✅ Dimension selector created")
        
        print("Step 2: Set up test dimensions")
        selector.available_dimensions = {
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
            }
        }
        print("   ✅ Test dimensions set up")
        
        print("Step 3: Update dimensions panel")
        selector.update_dimensions_panel()
        print("   ✅ Dimensions panel updated")
        
        print("Step 4: Test dimension dropping")
        
        # Test signal connection
        signal_received = []
        def on_signal(dim1, dim2):
            signal_received.append((dim1, dim2))
            print(f"   Signal received: {dim1} × {dim2}")
        
        selector.dimensions_changed.connect(on_signal)
        
        # Test dimension dropping
        print("   Testing on_dimension_dropped...")
        selector.on_dimension_dropped("x_axis", "time")
        print("   ✅ First dimension drop completed")
        
        selector.on_dimension_dropped("y_axis", "age")
        print("   ✅ Second dimension drop completed")
        
        print(f"   Signals received: {len(signal_received)}")
        
        print("Step 5: Test programmatic setting")
        selector.set_selected_dimensions("age", "time")
        print("   ✅ Programmatic setting completed")
        
        print(f"   Total signals received: {len(signal_received)}")
        
        print("\n✅ MINIMAL DIMENSION SELECTOR TEST PASSED")
        return True
        
    except RecursionError as e:
        print(f"\n❌ RECURSION ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ OTHER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_drop_zone_only():
    """Test just the drop zone functionality."""
    
    print("\n🔍 TESTING DROP ZONE ONLY")
    print("=" * 60)
    
    try:
        # Suppress Qt warnings for headless testing
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        from inspector.dimension_management import DropZone
        
        print("Step 1: Create drop zones")
        x_zone = DropZone("x_axis", "X-Axis")
        y_zone = DropZone("y_axis", "Y-Axis")
        print("   ✅ Drop zones created")
        
        print("Step 2: Test setting dimensions")
        x_zone.set_dimension("time")
        y_zone.set_dimension("age")
        print("   ✅ Dimensions set")
        
        print("Step 3: Test signal emission")
        signals_received = []
        def on_drop(zone, dim):
            signals_received.append((zone, dim))
            print(f"   Drop signal: {zone} <- {dim}")
        
        x_zone.dimension_dropped.connect(on_drop)
        y_zone.dimension_dropped.connect(on_drop)
        
        # Simulate drop events
        x_zone.dimension_dropped.emit("x_axis", "time")
        y_zone.dimension_dropped.emit("y_axis", "age")
        
        print(f"   Signals received: {len(signals_received)}")
        
        print("\n✅ DROP ZONE TEST PASSED")
        return True
        
    except RecursionError as e:
        print(f"\n❌ RECURSION ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ OTHER ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run minimal recursion tests."""
    
    print("=== MINIMAL RECURSION TESTING ===")
    print("Testing individual components to isolate recursion issues")
    
    try:
        # Test 1: Drop zone only
        test1_passed = test_drop_zone_only()
        
        # Test 2: Dimension selector only
        test2_passed = test_minimal_dimension_selector()
        
        # Summary
        print("\n" + "=" * 60)
        print("MINIMAL RECURSION TEST SUMMARY:")
        if test1_passed and test2_passed:
            print("🎉 ALL MINIMAL TESTS PASSED!")
            print("✅ Drop zones work correctly")
            print("✅ Dimension selector works correctly")
            print("The recursion issue might be in the full editor integration")
        else:
            print("❌ SOME MINIMAL TESTS FAILED.")
            if not test1_passed:
                print("❌ Drop zone test failed")
            if not test2_passed:
                print("❌ Dimension selector test failed")
        
        return 0 if (test1_passed and test2_passed) else 1
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
