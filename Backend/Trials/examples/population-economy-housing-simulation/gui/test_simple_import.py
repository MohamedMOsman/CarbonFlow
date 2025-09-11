#!/usr/bin/env python3
"""
Simple test to check if imports work without recursion.
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

def test_imports():
    """Test basic imports."""
    
    print("Testing imports...")
    
    try:
        print("1. Testing PyQt6 import...")
        from PyQt6.QtWidgets import QApplication
        print("   ✅ PyQt6 imported")
        
        print("2. Testing dimension management import...")
        from inspector.dimension_management import DropZone
        print("   ✅ DropZone imported")
        
        print("3. Testing spreadsheet editor import...")
        from inspector.spreadsheet_editor import EnhancedDimensionSelector
        print("   ✅ EnhancedDimensionSelector imported")
        
        print("4. Creating QApplication...")
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = QApplication([])
        print("   ✅ QApplication created")
        
        print("5. Creating DropZone...")
        zone = DropZone("test", "Test Zone")
        print("   ✅ DropZone created")
        
        print("6. Creating EnhancedDimensionSelector...")
        selector = EnhancedDimensionSelector()
        print("   ✅ EnhancedDimensionSelector created")
        
        print("\n✅ ALL IMPORTS AND BASIC CREATION SUCCESSFUL")
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


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
