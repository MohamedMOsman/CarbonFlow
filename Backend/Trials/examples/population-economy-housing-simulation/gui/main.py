#!/usr/bin/env python3
"""
System Dynamics GUI Application
Main entry point for the desktop GUI application for system dynamics modeling.

This application provides a visual interface for:
- Loading and editing YAML-based system dynamics models
- Visual model design with drag-and-drop components
- Simulation execution and results visualization
- Multidimensional data inspection and debugging
"""

import sys
import os
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from main_window import SystemDynamicsMainWindow, PROJECT_MANAGEMENT_AVAILABLE


class SystemDynamicsApp(QApplication):
    """Main application class for the System Dynamics GUI."""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application properties
        app_name = "System Dynamics Modeler"
        if PROJECT_MANAGEMENT_AVAILABLE:
            app_name += " - Enhanced"

        self.setApplicationName(app_name)
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("System Dynamics Toolkit")
        
        # Set application style
        self.setStyle('Fusion')  # Modern cross-platform style
        
        # Initialize main window
        self.main_window = None
        
    def initialize(self):
        """Initialize the application and show main window."""
        try:
            # Print startup info
            print(f"🚀 Starting System Dynamics Modeler...")
            print(f"📊 Project Management: {'✅ Available' if PROJECT_MANAGEMENT_AVAILABLE else '❌ Not Available (Legacy Mode)'}")

            # Create and show main window
            self.main_window = SystemDynamicsMainWindow()
            self.main_window.show()

            # Show startup message if project management is available
            if PROJECT_MANAGEMENT_AVAILABLE:
                QMessageBox.information(
                    self.main_window,
                    "Enhanced Features Available",
                    "🎉 Enhanced System Dynamics Modeler loaded successfully!\n\n"
                    "New features available:\n"
                    "• Hierarchical project organization (File → New Project)\n"
                    "• Multi-system support\n"
                    "• Enhanced component management\n"
                    "• Project tree view (left sidebar)\n"
                    "• Informants data management\n\n"
                    "All existing functionality is preserved.\n"
                    "Try creating a new project to explore the new features!"
                )
            
            # Center window on screen
            self.main_window.center_on_screen()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                None,
                "Application Error",
                f"Failed to initialize application:\n{str(e)}"
            )
            return False


def main():
    """Main entry point for the application."""
    
    # High DPI scaling is enabled by default in PyQt6
    # No need to set AA_EnableHighDpiScaling or AA_UseHighDpiPixmaps
    
    # Create application
    app = SystemDynamicsApp(sys.argv)
    
    # Initialize and run
    if app.initialize():
        sys.exit(app.exec())
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
