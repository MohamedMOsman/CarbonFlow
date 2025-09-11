#!/usr/bin/env python3
"""
Test the complete data restoration process for multidimensional data persistence.
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

def test_restoration_process():
    """Test the complete data restoration process."""
    
    print("\n🧪 DATA RESTORATION PROCESS TEST")
    print("=" * 50)
    
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
        
        print("Step 1: Set initial configuration Time × Age, City=Montreal")
        table_model = editor.table_model
        table_model.dimension_1 = 'time'
        table_model.dimension_2 = 'age'
        table_model.dimension_filters = {'city': 'Montreal'}
        table_model.set_available_dimensions(mock_model.dimensions)
        
        print(f"   Dimensions: {table_model.dimension_1} × {table_model.dimension_2}")
        print(f"   Filters: {table_model.dimension_filters}")
        
        print("\nStep 2: Add test data")
        # Add multiple data points
        test_data = [
            ('2020', '10', 100),  # Time=2020, Age=10, City=Montreal -> 100
            ('2020', '20', 200),  # Time=2020, Age=20, City=Montreal -> 200
            ('2021', '10', 150),  # Time=2021, Age=10, City=Montreal -> 150
        ]
        
        original_keys = []
        for time_val, age_val, value in test_data:
            key = table_model._create_data_key('population', time_val, age_val)
            table_model.data_matrix[key] = value
            original_keys.append(key)
            print(f"   Added: Time={time_val}, Age={age_val} -> {value}")
            print(f"     Key: {key}")
        
        print(f"\nStep 3: Save current data matrix")
        saved_data = table_model.get_data_matrix()
        print(f"   Saved {len(saved_data)} entries")
        
        print("\nStep 4: Switch to City × Age, Time=2020")
        # Change dimensions
        table_model.dimension_1 = 'city'
        table_model.dimension_2 = 'age'
        table_model.dimension_filters = {'time': '2020'}
        
        # Clear data matrix to simulate dimension change
        table_model.data_matrix = {}
        
        print(f"   New dimensions: {table_model.dimension_1} × {table_model.dimension_2}")
        print(f"   New filters: {table_model.dimension_filters}")
        print(f"   Data matrix cleared: {len(table_model.data_matrix)} entries")
        
        print("\nStep 5: Restore data using restore_data_matrix")
        table_model.restore_data_matrix(saved_data)
        
        print(f"   Data matrix after restoration: {len(table_model.data_matrix)} entries")
        for key, value in table_model.data_matrix.items():
            print(f"     {key}: {value}")
        
        print("\nStep 6: Verify expected data")
        # For Time=2020 filter, we should see:
        # - Montreal, Age=10 -> 100
        # - Montreal, Age=20 -> 200
        
        expected_results = [
            ('Montreal', '10', 100),
            ('Montreal', '20', 200),
        ]
        
        success = True
        for city_val, age_val, expected_value in expected_results:
            key = table_model._create_data_key('population', city_val, age_val)
            actual_value = table_model.data_matrix.get(key, 'NOT_FOUND')
            
            if actual_value == expected_value:
                print(f"   ✅ {city_val}, Age={age_val}: Expected {expected_value}, Found {actual_value}")
            else:
                print(f"   ❌ {city_val}, Age={age_val}: Expected {expected_value}, Found {actual_value}")
                success = False
        
        print("\nStep 7: Test another filter value")
        # Change filter to Time=2021
        table_model.dimension_filters = {'time': '2021'}
        
        # Clear and restore again
        table_model.data_matrix = {}
        table_model.restore_data_matrix(saved_data)
        
        print(f"   Changed filter to Time=2021")
        print(f"   Data matrix after restoration: {len(table_model.data_matrix)} entries")
        
        # For Time=2021 filter, we should see:
        # - Montreal, Age=10 -> 150
        
        key = table_model._create_data_key('population', 'Montreal', '10')
        actual_value = table_model.data_matrix.get(key, 'NOT_FOUND')
        expected_value = 150
        
        if actual_value == expected_value:
            print(f"   ✅ Montreal, Age=10 with Time=2021: Expected {expected_value}, Found {actual_value}")
        else:
            print(f"   ❌ Montreal, Age=10 with Time=2021: Expected {expected_value}, Found {actual_value}")
            success = False
        
        editor.close()
        
        if success:
            print(f"\n✅ DATA RESTORATION TEST PASSED!")
            print("   All data was correctly restored across dimension switches.")
            return True
        else:
            print(f"\n❌ DATA RESTORATION TEST FAILED!")
            print("   Some data was not properly restored.")
            return False
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the restoration test."""
    
    print("=== DATA RESTORATION PROCESS TEST ===")
    print("Testing the complete data restoration workflow")
    print("for multidimensional data persistence.")
    
    # Suppress Qt warnings for headless testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        success = test_restoration_process()
        
        if success:
            print("\n🎉 ALL RESTORATION TESTS PASSED!")
            print("The multidimensional data persistence fix is working correctly.")
            return 0
        else:
            print("\n❌ RESTORATION TESTS FAILED!")
            print("There are still issues with the data persistence implementation.")
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
