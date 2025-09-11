#!/usr/bin/env python3
"""
Test the integration between main GUI and enhanced spreadsheet editor.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import Qt

# Import the correct classes
from yaml_integration.yaml_loader import ModelComponent, GuiModel, YAMLModelLoader

class MainGuiIntegrationTest(QMainWindow):
    """Test window for main GUI integration."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Main GUI Integration Test")
        self.setGeometry(100, 100, 700, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the test UI."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Main GUI Integration Test")
        title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Test buttons
        test1_btn = QPushButton("🔍 Test 1: Load Real YAML Model")
        test1_btn.clicked.connect(self.test_load_yaml_model)
        layout.addWidget(test1_btn)
        
        test2_btn = QPushButton("🎯 Test 2: Create Component with Real Model")
        test2_btn.clicked.connect(self.test_component_with_real_model)
        layout.addWidget(test2_btn)
        
        test3_btn = QPushButton("🚀 Test 3: Open Enhanced Editor with Real Data")
        test3_btn.clicked.connect(self.test_enhanced_editor_with_real_data)
        layout.addWidget(test3_btn)
        
        test4_btn = QPushButton("🔧 Test 4: Simulate Component Double-Click")
        test4_btn.clicked.connect(self.test_simulate_component_double_click)
        layout.addWidget(test4_btn)
        
        # Log area
        self.log_area = QTextEdit()
        layout.addWidget(self.log_area)
        
        self.log("Ready to test main GUI integration...")
        
    def log(self, message):
        """Add a message to the log area."""
        self.log_area.append(message)
        print(message)
        
    def test_load_yaml_model(self):
        """Test loading a real YAML model."""
        
        self.log("🔍 Testing YAML model loading...")
        
        try:
            # Try to load the population dynamics model
            model_path = "../population-dynamics/model_structure.yaml"
            scenario_path = "../population-dynamics/scenario_parameters.yaml"
            
            self.log(f"Loading model from: {model_path}")

            loader = YAMLModelLoader()
            gui_model, sd_model = loader.load_model_from_file(model_path, scenario_path)
            
            self.log(f"✅ Model loaded successfully!")
            self.log(f"   Name: {gui_model.name}")
            self.log(f"   Components: {len(gui_model.components)}")
            self.log(f"   Dimensions: {len(gui_model.dimensions)}")
            
            # Check dimensions
            for dim_name, dim_info in gui_model.dimensions.items():
                labels = dim_info.get('labels', [])
                self.log(f"   - {dim_name}: {len(labels)} labels ({', '.join(labels[:3])}{'...' if len(labels) > 3 else ''})")
                
            # Store for other tests
            self.gui_model = gui_model
            
        except Exception as e:
            self.log(f"❌ Error loading YAML model: {e}")
            import traceback
            self.log(traceback.format_exc())
            
    def test_component_with_real_model(self):
        """Test creating a component with real model data."""
        
        self.log("🎯 Testing component creation with real model...")
        
        try:
            if not hasattr(self, 'gui_model'):
                self.log("❌ No model loaded. Run Test 1 first.")
                return
                
            # Get a real component from the model
            if self.gui_model.components:
                component_name = list(self.gui_model.components.keys())[0]
                component = self.gui_model.components[component_name]
                
                self.log(f"✅ Found component: {component.name}")
                self.log(f"   Type: {component.component_type}")
                self.log(f"   Properties: {list(component.properties.keys())}")
                
                # Check spatial dimensions
                spatial_dims = component.properties.get('spatial_dims', [])
                self.log(f"   Spatial dimensions: {spatial_dims}")
                
                # Verify dimensions exist in model
                for dim in spatial_dims:
                    if dim in self.gui_model.dimensions:
                        dim_info = self.gui_model.dimensions[dim]
                        labels = dim_info.get('labels', [])
                        self.log(f"     - {dim}: {len(labels)} values")
                    else:
                        self.log(f"     - {dim}: ❌ NOT FOUND in model dimensions")
                        
                # Store for other tests
                self.test_component = component
                
            else:
                self.log("❌ No components found in model")
                
        except Exception as e:
            self.log(f"❌ Error testing component: {e}")
            import traceback
            self.log(traceback.format_exc())
            
    def test_enhanced_editor_with_real_data(self):
        """Test opening enhanced editor with real data."""
        
        self.log("🚀 Testing enhanced editor with real data...")
        
        try:
            if not hasattr(self, 'gui_model') or not hasattr(self, 'test_component'):
                self.log("❌ No model/component loaded. Run Tests 1 and 2 first.")
                return
                
            from inspector.spreadsheet_editor import SpreadsheetDataEditor
            
            self.log("✅ Importing SpreadsheetDataEditor...")
            
            # Create editor with real data
            self.log("✅ Creating editor with real model and component...")
            editor = SpreadsheetDataEditor([self.test_component], self.gui_model, parent=self)
            
            self.log("✅ Showing editor...")
            editor.show()
            
            self.log("✅ Enhanced editor opened successfully with real data!")
            
            # Store reference
            self.real_editor = editor
            
        except Exception as e:
            self.log(f"❌ Error opening enhanced editor: {e}")
            import traceback
            self.log(traceback.format_exc())
            
    def test_simulate_component_double_click(self):
        """Test simulating component double-click from main GUI."""
        
        self.log("🔧 Testing component double-click simulation...")
        
        try:
            if not hasattr(self, 'gui_model') or not hasattr(self, 'test_component'):
                self.log("❌ No model/component loaded. Run Tests 1 and 2 first.")
                return
                
            # Import graphics items
            from canvas.graphics_items import StockItem
            from PyQt6.QtWidgets import QGraphicsScene
            
            self.log("✅ Creating graphics item...")
            
            # Create graphics item
            stock_item = StockItem(self.test_component)
            
            # Create scene with gui_model
            scene = QGraphicsScene()
            scene.gui_model = self.gui_model
            scene.addItem(stock_item)
            
            self.log("✅ Simulating double-click...")
            
            # Simulate double-click
            stock_item.open_multidimensional_editor()
            
            self.log("✅ Component double-click simulation completed!")
            
        except Exception as e:
            self.log(f"❌ Error simulating component double-click: {e}")
            import traceback
            self.log(traceback.format_exc())

def main():
    """Main test function."""
    
    print("Main GUI Integration Test")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create test window
    test_window = MainGuiIntegrationTest()
    test_window.show()
    
    print("Test window opened. Run tests in order to check integration.")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
