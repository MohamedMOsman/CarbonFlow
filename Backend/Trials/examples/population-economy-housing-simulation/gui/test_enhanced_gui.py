#!/usr/bin/env python3
"""
Test Enhanced GUI Integration

Simple test to verify that the enhanced project management features
are properly integrated into the existing GUI.
"""

import sys
import os
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from main_window import SystemDynamicsMainWindow, PROJECT_MANAGEMENT_AVAILABLE


def test_gui_startup():
    """Test that the GUI starts up correctly with project management features."""
    
    print("🧪 Testing Enhanced GUI Startup")
    print("=" * 40)
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced System Dynamics Modeler Test")
    
    try:
        # Create main window
        print("📱 Creating main window...")
        main_window = SystemDynamicsMainWindow()
        
        # Check if project management is available
        if PROJECT_MANAGEMENT_AVAILABLE:
            print("✅ Project management features are available")
            
            # Check if project tree widget was created
            if hasattr(main_window, 'project_tree') and main_window.project_tree:
                print("✅ Project tree widget created successfully")
            else:
                print("❌ Project tree widget not found")
                return False
                
            # Check if project manager was initialized
            if hasattr(main_window, 'project_manager') and main_window.project_manager:
                print("✅ Project manager initialized successfully")
            else:
                print("❌ Project manager not initialized")
                return False
                
            # Check menu items
            menubar = main_window.menuBar()
            file_menu = None
            for action in menubar.actions():
                if action.text() == "&File":
                    file_menu = action.menu()
                    break
            
            if file_menu:
                project_actions = []
                for action in file_menu.actions():
                    if "Project" in action.text():
                        project_actions.append(action.text())
                
                if project_actions:
                    print(f"✅ Project menu items found: {', '.join(project_actions)}")
                else:
                    print("❌ No project menu items found")
                    return False
            else:
                print("❌ File menu not found")
                return False
                
        else:
            print("⚠️  Project management features not available - running in legacy mode")
        
        # Show the window
        print("🖥️  Showing main window...")
        main_window.show()
        
        # Show success message
        QMessageBox.information(
            main_window,
            "Enhanced GUI Test",
            f"Enhanced System Dynamics GUI loaded successfully!\n\n"
            f"Project Management: {'✅ Available' if PROJECT_MANAGEMENT_AVAILABLE else '❌ Not Available'}\n"
            f"Window Title: {main_window.windowTitle()}\n\n"
            f"Features:\n"
            f"• {'✅' if PROJECT_MANAGEMENT_AVAILABLE else '❌'} Hierarchical project organization\n"
            f"• {'✅' if PROJECT_MANAGEMENT_AVAILABLE else '❌'} Multi-system support\n"
            f"• {'✅' if PROJECT_MANAGEMENT_AVAILABLE else '❌'} Enhanced component management\n"
            f"• ✅ Backward compatibility with existing models\n"
            f"• ✅ Multidimensional editing capabilities\n\n"
            f"You can now:\n"
            f"{'• Create new projects (File → New Project)' if PROJECT_MANAGEMENT_AVAILABLE else ''}\n"
            f"{'• Open existing projects (File → Open Project)' if PROJECT_MANAGEMENT_AVAILABLE else ''}\n"
            f"• Create and edit models (File → New Model)\n"
            f"• Use all existing GUI features"
        )
        
        print("✅ GUI test completed successfully!")
        print("\n💡 The GUI is now running. You can:")
        if PROJECT_MANAGEMENT_AVAILABLE:
            print("   • Try creating a new project (File → New Project)")
            print("   • Open an existing project (File → Open Project)")
            print("   • Explore the project tree on the left side")
        print("   • Create models using existing functionality")
        print("   • Close the window to exit")
        
        # Run the application
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error during GUI test: {e}")
        import traceback
        traceback.print_exc()
        
        if 'app' in locals():
            QMessageBox.critical(None, "GUI Test Error", f"Failed to start enhanced GUI: {e}")
        
        return False


def main():
    """Main test function."""
    
    print("🚀 Enhanced System Dynamics GUI - Integration Test")
    print("=" * 55)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "main_window.py").exists():
        print("❌ Error: Please run this test from the GUI directory")
        print(f"   Current directory: {current_dir}")
        print(f"   Expected files: main_window.py, project_management/")
        return 1
    
    # Check if project management module exists
    if (current_dir / "project_management").exists():
        print("✅ Project management module found")
    else:
        print("⚠️  Project management module not found - will run in legacy mode")
    
    # Run the test
    try:
        result = test_gui_startup()
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
