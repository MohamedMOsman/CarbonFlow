#!/usr/bin/env python3
"""
Test script to reproduce and investigate drag-and-drop crashes
when dragging dimensions to coordinate zones.
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

def test_drag_drop_crash():
    """Test drag-and-drop functionality to identify crash causes."""
    
    print("\n🔍 TESTING DRAG-AND-DROP CRASH")
    print("=" * 60)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        from inspector.dimension_management import DraggableDimensionItem, DropZone
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt, QMimeData
        from PyQt6.QtGui import QDrag
        
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
        
        print("Step 1: Create editor and check initial state")
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        print("   ✅ Editor created successfully")
        
        # Check dimension selector components
        dimension_selector = editor.dimension_selector
        print(f"   Available dimensions: {len(dimension_selector.available_dimensions)}")
        
        print("Step 2: Test DraggableDimensionItem creation")
        # Test creating draggable items directly
        for dim_name, dim_info in dimension_selector.available_dimensions.items():
            try:
                item = DraggableDimensionItem(dim_name, dim_info)
                print(f"   ✅ Created draggable item for {dim_name}")
                
                # Test basic properties
                print(f"     Dimension name: {item.dimension_name}")
                print(f"     Dimension info keys: {list(item.dimension_info.keys())}")
                
            except Exception as e:
                print(f"   ❌ Failed to create draggable item for {dim_name}: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        
        print("Step 3: Test DropZone creation and basic functionality")
        try:
            # Test drop zones
            x_zone = dimension_selector.x_axis_zone
            y_zone = dimension_selector.y_axis_zone
            
            print(f"   X-axis zone: {x_zone.zone_name}")
            print(f"   Y-axis zone: {y_zone.zone_name}")
            
            # Test setting dimensions programmatically
            x_zone.set_dimension("time")
            y_zone.set_dimension("age")
            
            print(f"   X-axis dimension: {x_zone.current_dimension}")
            print(f"   Y-axis dimension: {y_zone.current_dimension}")
            
            print("   ✅ Drop zones working correctly")
            
        except Exception as e:
            print(f"   ❌ Drop zone test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("Step 4: Test drag-and-drop signal connections")
        try:
            # Check signal connections
            x_zone_connected = x_zone.dimension_dropped.receivers() > 0
            y_zone_connected = y_zone.dimension_dropped.receivers() > 0
            
            print(f"   X-axis zone signal connected: {x_zone_connected}")
            print(f"   Y-axis zone signal connected: {y_zone_connected}")
            
            if not (x_zone_connected and y_zone_connected):
                print("   ❌ Signal connections missing")
                return False
            
            print("   ✅ Signal connections working")
            
        except Exception as e:
            print(f"   ❌ Signal connection test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("Step 5: Test simulated drag-and-drop operation")
        try:
            # Simulate a drop event
            from PyQt6.QtGui import QDropEvent
            from PyQt6.QtCore import QPoint
            
            # Create mime data as if from a drag operation
            mime_data = QMimeData()
            mime_data.setText("time")
            mime_data.setData("application/x-dimension", "time".encode())
            
            # Test drop event handling
            print("   Testing drop event handling...")
            
            # Check if drop zone accepts the mime data
            accepts_drop = x_zone.dragEnterEvent.__func__(x_zone, type('MockEvent', (), {
                'mimeData': lambda: mime_data,
                'acceptProposedAction': lambda: None
            })())
            
            print("   ✅ Drop event simulation completed")
            
        except Exception as e:
            print(f"   ❌ Simulated drag-and-drop failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("Step 6: Test dimension change handling")
        try:
            # Test the dimension change handler
            dimension_selector.on_dimension_dropped("x_axis", "time")
            dimension_selector.on_dimension_dropped("y_axis", "age")
            
            # Check if dimensions were set correctly
            x_dim = dimension_selector.x_axis_zone.current_dimension
            y_dim = dimension_selector.y_axis_zone.current_dimension
            
            print(f"   Final dimensions: Y={y_dim}, X={x_dim}")
            
            if x_dim == "time" and y_dim == "age":
                print("   ✅ Dimension change handling working")
            else:
                print("   ❌ Dimension change handling failed")
                return False
            
        except Exception as e:
            print(f"   ❌ Dimension change handling failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("Step 7: Test error conditions")
        try:
            # Test with invalid dimension name
            dimension_selector.on_dimension_dropped("x_axis", "invalid_dimension")
            print("   ✅ Invalid dimension handled gracefully")
            
            # Test with None dimension
            dimension_selector.on_dimension_dropped("y_axis", None)
            print("   ✅ None dimension handled gracefully")
            
            # Test with empty string
            dimension_selector.on_dimension_dropped("x_axis", "")
            print("   ✅ Empty dimension handled gracefully")
            
        except Exception as e:
            print(f"   ❌ Error condition test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        editor.close()
        
        print("\n✅ ALL DRAG-AND-DROP TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ DRAG-AND-DROP TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run drag-and-drop crash investigation."""
    
    print("=== DRAG-AND-DROP CRASH INVESTIGATION ===")
    print("Testing drag-and-drop functionality to identify crash causes")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Run test
        test_passed = test_drag_drop_crash()
        
        # Summary
        print("\n" + "=" * 60)
        print("DRAG-AND-DROP CRASH INVESTIGATION SUMMARY:")
        if test_passed:
            print("🎉 ALL DRAG-AND-DROP TESTS PASSED!")
            print("No crashes detected in drag-and-drop functionality.")
            print("The issue might be environment-specific or require actual GUI interaction.")
        else:
            print("❌ DRAG-AND-DROP TESTS FAILED.")
            print("Critical issues detected in drag-and-drop functionality.")
        
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
