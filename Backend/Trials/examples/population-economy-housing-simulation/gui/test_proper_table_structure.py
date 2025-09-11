#!/usr/bin/env python3
"""
Test the proper table structure with rows, columns, and dimension filters.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

# Import the correct classes
from yaml_integration.yaml_loader import ModelComponent

class ProperTableStructureTest(QMainWindow):
    """Test window for proper table structure."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Proper Table Structure Test")
        self.setGeometry(100, 100, 600, 500)
        
        # Store editor reference
        self.editor = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Proper Table Structure Test")
        title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Expected structure explanation
        structure_label = QLabel("""
🎯 Expected Table Structure:

✅ ROWS: Component × Dimension1 combinations
   • Each row represents one component for one value of the row dimension
   • Example: "population (Age 0-18)", "population (Age 19-35)", etc.

✅ COLUMNS: Dimension2 values
   • Each column represents one value of the column dimension
   • Example: "Low Income", "Medium Income", "High Income"

✅ ADDITIONAL DIMENSIONS: Dropdown filters
   • Dimensions not used as rows/columns appear as dropdown menus
   • Changing filter values updates the entire table
   • Example: Time Period dropdown, Building Type dropdown

✅ DATA CELLS: Values for specific combinations
   • Each cell contains the value for: Component + Row Dim + Col Dim + Filters
   • Example: Population for Age 0-18, Low Income, in Year 2020
        """)
        structure_label.setStyleSheet("background-color: #e8f4fd; padding: 15px; border: 1px solid #bee5eb; border-radius: 5px;")
        structure_label.setWordWrap(True)
        layout.addWidget(structure_label)
        
        # Test button
        test_btn = QPushButton("🧪 Test Proper Table Structure")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        test_btn.clicked.connect(self.test_proper_structure)
        layout.addWidget(test_btn)
        
        # Instructions
        instructions = QLabel("""
📋 Test Instructions:

1. Click the button to open the spreadsheet editor
2. Drag "age_group" to Y-Axis (Rows) and "income_level" to X-Axis (Columns)
3. Observe that:
   • Rows show: "population (0-18)", "population (19-35)", etc.
   • Columns show: "Low", "Medium-Low", "Medium", etc.
   • Additional dimensions appear as dropdown filters above the table
4. Change filter values and see the table update
5. Enter data in cells and verify it's stored correctly
        """)
        instructions.setStyleSheet("color: #6c757d; font-style: italic; margin-top: 10px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
    def test_proper_structure(self):
        """Test the proper table structure."""
        
        try:
            from inspector.spreadsheet_editor import SpreadsheetDataEditor
            
            # Create test components with multiple spatial dimensions
            components = [
                ModelComponent(
                    name="population",
                    component_type="stock",
                    properties={
                        'initial_value': 10000,
                        'units': 'people',
                        'spatial_dims': ['age_group', 'income_level', 'time_period', 'zone'],
                        'description': 'Population by demographics, time, and location'
                    }
                ),
                ModelComponent(
                    name="housing_units",
                    component_type="stock",
                    properties={
                        'initial_value': 5000,
                        'units': 'units',
                        'spatial_dims': ['building_type', 'age_group', 'zone'],
                        'description': 'Housing units by type, age, and location'
                    }
                ),
                ModelComponent(
                    name="employment",
                    component_type="stock",
                    properties={
                        'initial_value': 8000,
                        'units': 'jobs',
                        'spatial_dims': ['income_level', 'sector', 'zone'],
                        'description': 'Employment by income, sector, and location'
                    }
                )
            ]
            
            # Create comprehensive mock model with many dimensions
            class ProperStructureMockModel:
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
                        'time_period': {
                            'labels': [str(year) for year in range(2020, 2031)],
                            'description': 'Annual time periods',
                            'type': 'temporal',
                            'size': 11
                        },
                        'zone': {
                            'labels': ['Urban-Core', 'Urban-Edge', 'Suburban', 'Rural'],
                            'description': 'Geographic zones',
                            'type': 'categorical',
                            'size': 4
                        },
                        'building_type': {
                            'labels': ['Single-Family', 'Multi-Family', 'Condo', 'Apartment'],
                            'description': 'Housing building types',
                            'type': 'categorical',
                            'size': 4
                        },
                        'sector': {
                            'labels': ['Manufacturing', 'Services', 'Technology', 'Healthcare', 'Education'],
                            'description': 'Employment sectors',
                            'type': 'categorical',
                            'size': 5
                        }
                    }
            
            # Create and show the editor
            self.editor = SpreadsheetDataEditor(components, ProperStructureMockModel(), parent=self)
            self.editor.show()
            
            print("🎉 Proper Table Structure Test opened successfully!")
            print("=" * 70)
            print("✅ Expected Structure:")
            print("   • ROWS: Component × Row Dimension combinations")
            print("   • COLUMNS: Column Dimension values")
            print("   • FILTERS: Additional dimensions as dropdowns")
            print("=" * 70)
            print("📋 Test Steps:")
            print("   1. Drag 'age_group' to Y-Axis (Rows)")
            print("   2. Drag 'income_level' to X-Axis (Columns)")
            print("   3. Check that other dimensions appear as filters")
            print("   4. Verify table structure matches expectations")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Error opening proper structure test: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main test function."""
    
    print("Proper Table Structure Test")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = ProperTableStructureTest()
    test_window.show()
    
    print("Test window opened. Click the button to test proper table structure.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
