#!/usr/bin/env python3
"""
Simple test script to validate that all imports are working correctly.
"""

def test_imports():
    """Test all the imports for the spreadsheet editor."""
    
    print("Testing Spreadsheet Editor Imports")
    print("=" * 40)
    
    try:
        print("1. Testing PyQt6 imports...")
        from PyQt6.QtWidgets import QApplication, QMainWindow
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QUndoStack
        print("   ✅ PyQt6 imports successful")
    except ImportError as e:
        print(f"   ❌ PyQt6 import failed: {e}")
        return False
    
    try:
        print("2. Testing numpy imports...")
        import numpy as np
        print("   ✅ numpy imports successful")
    except ImportError as e:
        print(f"   ❌ numpy import failed: {e}")
        return False
    
    try:
        print("3. Testing spreadsheet editor imports...")
        from inspector.spreadsheet_editor import SpreadsheetDataEditor
        print("   ✅ SpreadsheetDataEditor import successful")
    except ImportError as e:
        print(f"   ❌ SpreadsheetDataEditor import failed: {e}")
        return False
    
    try:
        print("4. Testing climate adaptation features...")
        from inspector.climate_adaptation_features import ClimateAdaptationTemplates
        print("   ✅ Climate adaptation features import successful")
    except ImportError as e:
        print(f"   ❌ Climate adaptation features import failed: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 ALL IMPORTS SUCCESSFUL!")
    print("=" * 40)
    
    print("\nYou can now:")
    print("• Run the test GUI: python test_spreadsheet_editor.py")
    print("• Try the demo notebook: jupyter notebook Spreadsheet_Editor_Demo.ipynb")
    print("• Use the spreadsheet editor in your applications")
    
    return True

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)
