#!/usr/bin/env python3
"""
Test script to verify all imports work correctly for the multidimensional editor.
"""

import sys
from pathlib import Path

# Add the GUI directory to the Python path
gui_dir = Path(__file__).parent
sys.path.insert(0, str(gui_dir))

def test_imports():
    """Test that all required imports work."""
    
    print("Testing imports for multidimensional editor...")
    
    try:
        # Test basic PyQt6 imports
        print("  Testing PyQt6 imports...")
        from PyQt6.QtWidgets import (
            QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
            QDialog, QDialogButtonBox, QGroupBox, QFormLayout, QScrollArea,
            QSplitter, QTabWidget, QMessageBox, QInputDialog, QMenu, QApplication,
            QPushButton, QLabel, QHeaderView, QTextEdit, QLineEdit, QSpinBox,
            QComboBox
        )
        from PyQt6.QtCore import Qt, pyqtSignal, QTimer
        from PyQt6.QtGui import QFont, QAction, QKeySequence, QClipboard
        print("    ✓ PyQt6 imports successful")
        
        # Test our custom imports
        print("  Testing custom imports...")
        from yaml_integration.yaml_loader import ModelComponent, GuiModel
        print("    ✓ YAML loader imports successful")
        
        # Test the multidimensional editor import
        print("  Testing multidimensional editor import...")
        from inspector.multidimensional_editor import DimensionTableEditor, MultidimensionalEditorDialog
        print("    ✓ Multidimensional editor imports successful")
        
        print("✓ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_component_creation():
    """Test creating a component and editor dialog."""
    
    print("\nTesting component and dialog creation...")
    
    try:
        from yaml_integration.yaml_loader import ModelComponent, GuiModel
        from inspector.multidimensional_editor import MultidimensionalEditorDialog
        
        # Create test component
        component = ModelComponent(
            name="test_component",
            component_type="stock",
            properties={
                'initial_value': 100,
                'units': 'people',
                'spatial_dims': ['age', 'income'],
                'description': 'Test multidimensional component'
            }
        )
        print("  ✓ Component created successfully")
        
        # Create test model
        model = GuiModel("Test Model")
        model.dimensions = {
            'age': {
                'labels': ['young', 'middle', 'old'],
                'size': 3,
                'type': 'categorical',
                'description': 'Age groups'
            },
            'income': {
                'labels': ['low', 'medium', 'high'],
                'size': 3,
                'type': 'categorical',
                'description': 'Income levels'
            }
        }
        print("  ✓ Model created successfully")
        
        # Test dialog creation (without showing it)
        try:
            dialog = MultidimensionalEditorDialog(component, model, parent=None)
            print("  ✓ Dialog created successfully")
            
            # Test some basic dialog methods
            has_changes = dialog.has_changes()
            print(f"  ✓ Dialog methods work (has_changes: {has_changes})")
            
        except Exception as e:
            print(f"  ✗ Dialog creation failed: {e}")
            return False
            
        print("✓ Component and dialog creation successful!")
        return True
        
    except Exception as e:
        print(f"✗ Component creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dimension_table():
    """Test the dimension table editor."""
    
    print("\nTesting dimension table editor...")
    
    try:
        from inspector.multidimensional_editor import DimensionTableEditor
        
        # Create table editor
        table = DimensionTableEditor()
        print("  ✓ Table editor created successfully")
        
        # Test setting dimensional data
        test_dimensions = {
            'parcel': ['1001', '1002', '1003'],
            'building_type': ['residential', 'commercial']
        }
        
        test_metadata = {
            'parcel': {'description': 'Property parcels', 'type': 'categorical'},
            'building_type': {'description': 'Building types', 'type': 'categorical'}
        }
        
        table.set_dimensional_data(test_dimensions, test_metadata)
        print("  ✓ Dimensional data set successfully")
        
        # Test getting data back
        retrieved_dims, retrieved_meta = table.get_dimensional_data()
        print(f"  ✓ Data retrieval successful: {len(retrieved_dims)} dimensions")
        
        # Test validation
        validation_result = table.validate_data()
        print(f"  ✓ Validation successful: {validation_result['valid']}")
        
        print("✓ Dimension table editor tests successful!")
        return True
        
    except Exception as e:
        print(f"✗ Dimension table error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    
    print("=" * 60)
    print("MULTIDIMENSIONAL EDITOR IMPORT AND FUNCTIONALITY TESTS")
    print("=" * 60)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test component creation
    if not test_component_creation():
        success = False
        
    # Test dimension table
    if not test_dimension_table():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("ALL TESTS PASSED! ✓")
        print("The multidimensional editor is ready to use.")
        print("\nTo use in the GUI:")
        print("1. Run the main GUI application")
        print("2. Load or create a model with components")
        print("3. Double-click any component to open the editor")
        print("4. Or use the 'Edit Dimensions...' button in the inspector")
    else:
        print("SOME TESTS FAILED! ✗")
        print("Please check the error messages above.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
