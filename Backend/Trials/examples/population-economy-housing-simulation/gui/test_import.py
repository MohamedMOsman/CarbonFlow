#!/usr/bin/env python3
"""Test if the enhanced main window can be imported."""

import sys
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

print("🧪 Testing enhanced main window import...")

try:
    from main_window import SystemDynamicsMainWindow, PROJECT_MANAGEMENT_AVAILABLE
    print(f"✅ SystemDynamicsMainWindow imported successfully")
    print(f"📊 PROJECT_MANAGEMENT_AVAILABLE: {PROJECT_MANAGEMENT_AVAILABLE}")
    
    if PROJECT_MANAGEMENT_AVAILABLE:
        print("✅ Enhanced features should be available in the GUI")
    else:
        print("⚠️  Running in legacy mode - enhanced features not available")
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("✅ Import test complete!")
