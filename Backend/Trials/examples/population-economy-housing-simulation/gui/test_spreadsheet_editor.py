"""
Test script for the Spreadsheet-Style Component Data Editor

This script demonstrates and tests the comprehensive Excel-like interface
for editing multidimensional system dynamics data.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt

# Import the spreadsheet editor
try:
    from inspector.spreadsheet_editor import SpreadsheetDataEditor
    from inspector.climate_adaptation_features import ClimateAdaptationTemplates
    EDITOR_AVAILABLE = True
except ImportError as e:
    print(f"Could not import spreadsheet editor: {e}")
    EDITOR_AVAILABLE = False

# Mock component class for testing
class MockComponent:
    """Mock component for testing the spreadsheet editor."""
    
    def __init__(self, name, component_type, spatial_dims=None):
        self.name = name
        self.component_type = component_type
        self.properties = {
            'spatial_dims': spatial_dims or ['parcel', 'time'],
            'description': f'Mock {component_type} component for testing',
            'units': 'units',
            'initial_value': 0
        }
        
    def __str__(self):
        return f"{self.component_type}({self.name})"


class MockModel:
    """Mock model for testing the spreadsheet editor."""
    
    def __init__(self):
        self.dimensions = {
            'parcel': {
                'labels': ['1001', '1002', '1003'],
                'description': 'Property parcel identifiers',
                'type': 'categorical',
                'size': 3
            },
            'time': {
                'labels': [str(year) for year in range(2020, 2031)],
                'description': 'Annual time steps',
                'type': 'temporal',
                'size': 11
            },
            'building_type': {
                'labels': ['single_family', 'multi_family', 'commercial'],
                'description': 'Building type categories',
                'type': 'categorical',
                'size': 3
            },
            'year_built_cohort': {
                'labels': ['pre_1950', '1950_1970', '1970_1990', '1990_2010', 'post_2010'],
                'description': 'Construction era cohorts',
                'type': 'categorical',
                'size': 5
            }
        }


class SpreadsheetEditorTestWindow(QMainWindow):
    """Main test window for the spreadsheet editor."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Spreadsheet Editor Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create mock data
        self.mock_model = MockModel()
        self.mock_components = [
            MockComponent("basement_height_improvement_rate", "flow", ['building_type', 'year_built_cohort', 'parcel']),
            MockComponent("offset_improvement_rate", "flow", ['building_type', 'year_built_cohort', 'parcel']),
            MockComponent("structureBsmtHeight", "stock", ['parcel', 'time']),
            MockComponent("structureOffsetFromGrnd", "stock", ['parcel', 'time']),
            MockComponent("albedoChange", "parameter", ['parcel', 'time']),
            MockComponent("albedoTempInt", "parameter", ['parcel', 'time']),
            MockComponent("population", "stock", ['parcel', 'time']),
            MockComponent("housing_units", "stock", ['parcel', 'time'])
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Test buttons
        if EDITOR_AVAILABLE:
            # Basic spreadsheet editor test
            basic_test_btn = QPushButton("Test Basic Spreadsheet Editor")
            basic_test_btn.clicked.connect(self.test_basic_editor)
            layout.addWidget(basic_test_btn)
            
            # Climate adaptation test
            climate_test_btn = QPushButton("Test Climate Adaptation Features")
            climate_test_btn.clicked.connect(self.test_climate_features)
            layout.addWidget(climate_test_btn)
            
            # Flood protection scenario test
            flood_test_btn = QPushButton("Test Flood Protection Scenario")
            flood_test_btn.clicked.connect(self.test_flood_protection)
            layout.addWidget(flood_test_btn)
            
            # Albedo changes scenario test
            albedo_test_btn = QPushButton("Test Albedo Changes Scenario")
            albedo_test_btn.clicked.connect(self.test_albedo_changes)
            layout.addWidget(albedo_test_btn)
            
            # Multi-component test
            multi_test_btn = QPushButton("Test Multi-Component Editor")
            multi_test_btn.clicked.connect(self.test_multi_component)
            layout.addWidget(multi_test_btn)
            
        else:
            error_label = QPushButton("Spreadsheet Editor Not Available")
            error_label.setEnabled(False)
            layout.addWidget(error_label)
            
    def test_basic_editor(self):
        """Test the basic spreadsheet editor functionality."""
        
        # Create editor with a single component
        component = self.mock_components[0]  # basement_height_improvement_rate
        
        editor = SpreadsheetDataEditor([component], self.mock_model)
        editor.show()
        
        print(f"Opened basic editor for component: {component.name}")
        print(f"Available dimensions: {list(self.mock_model.dimensions.keys())}")
        
    def test_climate_features(self):
        """Test climate adaptation specific features."""
        
        # Create editor with climate-related components
        climate_components = [
            comp for comp in self.mock_components 
            if comp.name in ['structureBsmtHeight', 'structureOffsetFromGrnd', 'albedoChange']
        ]
        
        editor = SpreadsheetDataEditor(climate_components, self.mock_model)
        editor.show()
        
        print(f"Opened climate features editor with {len(climate_components)} components")
        print("Climate templates available:", list(ClimateAdaptationTemplates.get_dimension_combinations().keys()))
        
    def test_flood_protection(self):
        """Test flood protection scenario with specific components."""
        
        # Components for flood protection
        flood_components = [
            comp for comp in self.mock_components 
            if comp.name in ['basement_height_improvement_rate', 'offset_improvement_rate', 
                           'structureBsmtHeight', 'structureOffsetFromGrnd']
        ]
        
        editor = SpreadsheetDataEditor(flood_components, self.mock_model)
        editor.show()
        
        print(f"Opened flood protection scenario with {len(flood_components)} components")
        print("Flood protection components:", [comp.name for comp in flood_components])
        
    def test_albedo_changes(self):
        """Test albedo changes scenario."""
        
        # Components for albedo changes
        albedo_components = [
            comp for comp in self.mock_components 
            if comp.name in ['albedoChange', 'albedoTempInt']
        ]
        
        editor = SpreadsheetDataEditor(albedo_components, self.mock_model)
        editor.show()
        
        print(f"Opened albedo changes scenario with {len(albedo_components)} components")
        print("Albedo components:", [comp.name for comp in albedo_components])
        
    def test_multi_component(self):
        """Test editor with all components."""
        
        editor = SpreadsheetDataEditor(self.mock_components, self.mock_model)
        editor.show()
        
        print(f"Opened multi-component editor with {len(self.mock_components)} components")
        print("All components:", [comp.name for comp in self.mock_components])


def run_spreadsheet_editor_tests():
    """Run the spreadsheet editor tests."""
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Spreadsheet Editor Test")
    app.setApplicationVersion("1.0")
    
    # Create and show test window
    test_window = SpreadsheetEditorTestWindow()
    test_window.show()
    
    print("Spreadsheet Editor Test Application Started")
    print("=" * 50)
    
    if EDITOR_AVAILABLE:
        print("✓ Spreadsheet editor is available")
        print("✓ Climate adaptation features are available")
        print("\nTest Options:")
        print("1. Basic Editor - Test core spreadsheet functionality")
        print("2. Climate Features - Test climate adaptation templates")
        print("3. Flood Protection - Test flood protection scenario")
        print("4. Albedo Changes - Test albedo modification scenario")
        print("5. Multi-Component - Test with all components")
        print("\nClick the buttons in the test window to run different tests.")
    else:
        print("✗ Spreadsheet editor is not available")
        print("Please ensure all dependencies are installed:")
        print("  pip install PyQt6 PyYAML numpy")
        
    print("=" * 50)
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    run_spreadsheet_editor_tests()
