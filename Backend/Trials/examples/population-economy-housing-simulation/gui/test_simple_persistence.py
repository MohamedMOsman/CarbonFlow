#!/usr/bin/env python3
"""
Simplified test for multidimensional data persistence issue.
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

def test_simple_persistence():
    """Simple test for data persistence."""
    
    print("\n🧪 SIMPLE PERSISTENCE TEST")
    print("=" * 40)
    
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        from yaml_integration.yaml_loader import ModelComponent
        
        # Create mock model with 3 dimensions
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
                        'labels': ['10', '20'],
                        'description': 'Age groups',
                        'type': 'numerical',
                        'size': 2
                    },
                    'city': {
                        'labels': ['Montreal', 'Toronto'],
                        'description': 'Cities',
                        'type': 'categorical',
                        'size': 2
                    }
                }
        
        # Create test component
        component = ModelComponent(
            name="population",
            component_type="stock",
            properties={
                'initial_value': 1000,
                'units': 'people',
                'spatial_dims': ['time', 'age', 'city'],
                'description': 'Population data'
            }
        )
        
        # Create editor
        mock_model = MockModel()
        editor = SpreadsheetDataEditor([component], mock_model, parent=None)
        
        print("Step 1: Set initial dimensions Time × Age")
        editor.dimension_selector.set_selected_dimensions('time', 'age')
        
        # Check current state
        table_model = editor.table_model
        print(f"   Dimensions: {table_model.dimension_1} × {table_model.dimension_2}")
        print(f"   Filters: {table_model.dimension_filters}")
        
        print("\nStep 2: Add test data")
        # Manually set city filter to Montreal
        table_model.dimension_filters['city'] = 'Montreal'
        
        # Add data: Time=2020, Age=10, City=Montreal -> value 100
        key1 = table_model._create_data_key('population', '2020', '10')
        table_model.data_matrix[key1] = 100
        print(f"   Added: Time=2020, Age=10 -> 100")
        print(f"   Key: {key1}")
        
        print("\nStep 3: Switch to City × Age")
        # Manually switch dimensions without using the GUI
        table_model.dimension_1 = 'city'
        table_model.dimension_2 = 'age'
        table_model.dimension_filters = {'time': '2020'}  # Time becomes filter
        
        print(f"   New dimensions: {table_model.dimension_1} × {table_model.dimension_2}")
        print(f"   New filters: {table_model.dimension_filters}")
        
        print("\nStep 4: Check if data can be found")
        # Try to find our data with new key structure
        key2 = table_model._create_data_key('population', 'Montreal', '10')
        value = table_model.data_matrix.get(key2, 'NOT_FOUND')
        print(f"   Looking for: City=Montreal, Age=10 -> {value}")
        print(f"   Key: {key2}")
        
        print("\nStep 5: Test data restoration")
        # Simulate the restoration process
        old_data = {key1: 100}  # Our original data
        
        # Parse the old key
        parsed = table_model._parse_data_key(key1)
        print(f"   Parsed old key: {parsed}")
        
        if parsed:
            # Try to reconstruct
            new_key = table_model._reconstruct_data_key(parsed['component'], parsed['coordinates'])
            print(f"   Reconstructed key: {new_key}")
            
            if new_key == key2:
                print("   ✅ Key reconstruction successful!")
                return True
            else:
                print("   ❌ Key reconstruction failed!")
                return False
        else:
            print("   ❌ Failed to parse old key!")
            return False
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the simple test."""
    
    print("=== SIMPLE MULTIDIMENSIONAL PERSISTENCE TEST ===")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        success = test_simple_persistence()
        
        if success:
            print("\n✅ SIMPLE TEST PASSED!")
            return 0
        else:
            print("\n❌ SIMPLE TEST FAILED!")
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
