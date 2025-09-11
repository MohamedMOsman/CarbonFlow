#!/usr/bin/env python3
"""
Basic GUI Test Script

This script tests the basic GUI setup and ensures all dependencies are working.
Run this before proceeding with full GUI development.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        # Test PyQt6 imports
        from PyQt6.QtWidgets import QApplication, QMainWindow
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QIcon
        print("✅ PyQt6 imports successful")
        
        # Test scientific computing imports
        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        print("✅ Scientific computing imports successful")
        
        # Test YAML import
        import yaml
        print("✅ YAML import successful")
        
        # Test sd_toolkit imports
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))
        from sd_toolkit.config import YAMLSystemBuilder
        from sd_toolkit.engine.system import SystemModel
        from sd_toolkit.analysis.plotting import SystemPlotter
        print("✅ sd_toolkit imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_gui_creation():
    """Test basic GUI window creation."""
    print("\nTesting GUI creation...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
        from PyQt6.QtCore import Qt
        
        # Create application (required for any Qt widgets)
        app = QApplication(sys.argv)
        
        # Create a simple test window
        window = QMainWindow()
        window.setWindowTitle("GUI Test")
        window.setGeometry(100, 100, 400, 300)
        
        # Add a label
        label = QLabel("GUI Test Successful!", window)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window.setCentralWidget(label)
        
        print("✅ Basic GUI window created successfully")
        
        # Don't show the window in test mode, just verify creation
        # window.show()
        # app.exec()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI creation error: {e}")
        return False

def test_yaml_loading():
    """Test loading the existing YAML model."""
    print("\nTesting YAML model loading...")
    
    try:
        import yaml
        
        # Try to load the integrated model structure
        model_path = Path(__file__).parent.parent / "integrated_model_structure.yaml"
        
        if not model_path.exists():
            print(f"⚠️ Model file not found: {model_path}")
            return False
            
        with open(model_path, 'r') as file:
            model_data = yaml.safe_load(file)
            
        print(f"✅ YAML model loaded: {model_data['model']['name']}")
        print(f"   - Dimensions: {len(model_data.get('dimensions', {}))}")
        print(f"   - Elements: {len(model_data.get('elements', {}).get('stocks', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ YAML loading error: {e}")
        return False

def main():
    """Run all tests."""
    print("System Dynamics GUI - Basic Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_gui_creation,
        test_yaml_loading
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All tests passed! GUI setup is ready.")
        print("\nNext steps:")
        print("1. Run 'python main.py' to start the GUI application")
        print("2. Continue with YAML integration implementation")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        print("\nTroubleshooting:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Ensure sd_toolkit is in the correct location")
        print("3. Check that PyQt6 is properly installed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
