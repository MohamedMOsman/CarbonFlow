#!/usr/bin/env python3
"""
Test the enhanced dimension management features in the spreadsheet editor.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

# Import the correct classes
from yaml_integration.yaml_loader import ModelComponent

class EnhancedDimensionManagementTest(QMainWindow):
    """Test window for enhanced dimension management features."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Enhanced Dimension Management Test")
        self.setGeometry(100, 100, 500, 400)
        
        # Store editor reference
        self.editor = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Enhanced Dimension Management Test")
        title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Features list
        features_label = QLabel("""
🎯 Enhanced Features to Test:

✅ Drag-and-Drop Dimension Assignment
   • Drag dimensions from the available panel to X/Y axis zones
   • Visual feedback during drag operations
   • Automatic table rebuilding

✅ Add New Dimensions
   • Click "+ Add Dimension" button
   • Create custom dimensions with labels
   • Support for categorical, temporal, numerical, ordinal types
   • Range generation for numerical sequences

✅ Dynamic Table Regeneration
   • Loading indicators for large datasets
   • Data preservation across dimension changes
   • Real-time table updates

✅ Undo/Redo Support
   • Ctrl+Z to undo dimension changes
   • Ctrl+Y to redo dimension changes
   • Command history tracking

✅ Enhanced User Experience
   • Tooltips with dimension metadata
   • Visual drop zone highlighting
   • Dimension size and type information
        """)
        features_label.setStyleSheet("background-color: #f8f9fa; padding: 15px; border: 1px solid #dee2e6; border-radius: 5px;")
        features_label.setWordWrap(True)
        layout.addWidget(features_label)
        
        # Test button
        test_btn = QPushButton("🚀 Open Enhanced Spreadsheet Editor")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        test_btn.clicked.connect(self.open_enhanced_editor)
        layout.addWidget(test_btn)
        
        # Instructions
        instructions = QLabel("""
📋 Test Instructions:

1. Click the button above to open the enhanced spreadsheet editor
2. Try dragging dimensions between the available panel and axis zones
3. Click "+ Add Dimension" to create new dimensions
4. Test undo/redo with Ctrl+Z and Ctrl+Y
5. Observe loading indicators and visual feedback
        """)
        instructions.setStyleSheet("color: #7f8c8d; font-style: italic; margin-top: 10px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
    def open_enhanced_editor(self):
        """Open the enhanced spreadsheet editor."""
        
        try:
            from inspector.spreadsheet_editor import SpreadsheetDataEditor
            
            # Create test components with different spatial dimensions
            components = [
                ModelComponent(
                    name="population",
                    component_type="stock",
                    properties={
                        'initial_value': 10000,
                        'units': 'people',
                        'spatial_dims': ['age_group', 'income_level'],
                        'description': 'Population by demographics'
                    }
                ),
                ModelComponent(
                    name="flood_protection",
                    component_type="stock",
                    properties={
                        'initial_value': 0,
                        'units': 'measures',
                        'spatial_dims': ['parcel', 'building_type'],
                        'description': 'Flood protection measures'
                    }
                ),
                ModelComponent(
                    name="albedo_changes",
                    component_type="stock",
                    properties={
                        'initial_value': 0.3,
                        'units': 'albedo_units',
                        'spatial_dims': ['zone', 'time_period'],
                        'description': 'Albedo modification measures'
                    }
                )
            ]
            
            # Create comprehensive mock model with multiple dimensions
            class EnhancedMockModel:
                def __init__(self):
                    self.dimensions = {
                        'age_group': {
                            'labels': ['0-18', '19-35', '36-55', '56-70', '70+'],
                            'description': 'Age demographic groups',
                            'type': 'categorical',
                            'size': 5
                        },
                        'income_level': {
                            'labels': ['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'],
                            'description': 'Household income categories',
                            'type': 'ordinal',
                            'size': 5
                        },
                        'parcel': {
                            'labels': ['1001', '1002', '1003', '1004', '1005'],
                            'description': 'Property parcel identifiers',
                            'type': 'categorical',
                            'size': 5
                        },
                        'building_type': {
                            'labels': ['Residential', 'Commercial', 'Industrial', 'Mixed-Use'],
                            'description': 'Building use classifications',
                            'type': 'categorical',
                            'size': 4
                        },
                        'zone': {
                            'labels': ['Urban-Core', 'Urban-Edge', 'Suburban', 'Rural'],
                            'description': 'Geographic zones',
                            'type': 'categorical',
                            'size': 4
                        },
                        'time_period': {
                            'labels': [str(year) for year in range(2020, 2031)],
                            'description': 'Annual time periods',
                            'type': 'temporal',
                            'size': 11
                        }
                    }
            
            # Create and show the enhanced editor
            self.editor = SpreadsheetDataEditor(components, EnhancedMockModel(), parent=self)
            self.editor.show()
            
            print("🎉 Enhanced Spreadsheet Editor opened successfully!")
            print("=" * 60)
            print("✅ Features available:")
            print("   • Drag-and-drop dimension assignment")
            print("   • Add new dimensions with '+ Add Dimension' button")
            print("   • Undo/redo support (Ctrl+Z, Ctrl+Y)")
            print("   • Loading indicators for large datasets")
            print("   • Enhanced visual feedback and tooltips")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error opening enhanced editor: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main test function."""
    
    print("Enhanced Dimension Management Test")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = EnhancedDimensionManagementTest()
    test_window.show()
    
    print("Test window opened. Click the button to test enhanced features.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
