#!/usr/bin/env python3
"""
Debug test for connection functionality.
"""

import sys
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPointF

from canvas.model_canvas import ModelCanvas
from yaml_integration.yaml_loader import GuiModel, ModelComponent


class ConnectionDebugWindow(QMainWindow):
    """Debug window for testing connection functionality."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Connection Debug Test")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Instructions
        instructions = QLabel(
            "Debug Instructions:\n"
            "1. Click 'Setup Test Components' to create test components\n"
            "2. Hold Ctrl and click on a component (you should see 'Connection mode started')\n"
            "3. Drag to another component and release (you should see connection created)\n"
            "4. Watch the status messages below"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc; }")
        layout.addWidget(instructions)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        setup_button = QPushButton("Setup Test Components")
        setup_button.clicked.connect(self.setup_test_components)
        button_layout.addWidget(setup_button)
        
        clear_button = QPushButton("Clear Canvas")
        clear_button.clicked.connect(self.clear_canvas)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Create canvas
        self.canvas = ModelCanvas()
        layout.addWidget(self.canvas)
        
        # Connect canvas signals for debugging
        self.canvas.component_selected.connect(self.on_component_selected)
        self.canvas.connection_created.connect(self.on_connection_created)
        self.canvas.model_modified.connect(self.on_model_modified)
        
        # Status bar
        self.statusBar().showMessage("Ready - Click 'Setup Test Components' first")
        
        # Debug info
        self.debug_info = QLabel("Debug Info: None")
        self.debug_info.setStyleSheet("QLabel { background-color: #ffffcc; padding: 5px; }")
        layout.addWidget(self.debug_info)
        
        # Store model data
        self.gui_model = None
        
        # Override canvas methods for debugging
        self.setup_debug_methods()
        
    def setup_debug_methods(self):
        """Override canvas methods to add debug output."""
        
        # Store original methods
        original_start_connection = self.canvas.start_connection
        original_end_connection = self.canvas.end_connection
        original_create_connection = self.canvas.create_connection
        original_mouse_press = self.canvas.mousePressEvent
        original_mouse_move = self.canvas.mouseMoveEvent
        original_mouse_release = self.canvas.mouseReleaseEvent
        
        def debug_start_connection(from_item):
            self.debug_info.setText(f"🔵 Connection mode started from: {from_item.component.name}")
            self.statusBar().showMessage(f"Connection mode started from: {from_item.component.name}")
            return original_start_connection(from_item)
        
        def debug_end_connection():
            self.debug_info.setText("🔴 Connection mode ended")
            self.statusBar().showMessage("Connection mode ended")
            return original_end_connection()
        
        def debug_create_connection(from_item, to_item):
            self.debug_info.setText(f"✅ Creating connection: {from_item.component.name} → {to_item.component.name}")
            self.statusBar().showMessage(f"Creating connection: {from_item.component.name} → {to_item.component.name}")
            return original_create_connection(from_item, to_item)
        
        def debug_mouse_press(event):
            item = self.canvas.itemAt(event.position().toPoint())
            is_ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
            
            if item and hasattr(item, 'component') and is_ctrl:
                self.debug_info.setText(f"🖱️ Ctrl+Click on: {item.component.name}")
            elif item and hasattr(item, 'component'):
                self.debug_info.setText(f"🖱️ Click on: {item.component.name}")
            else:
                self.debug_info.setText("🖱️ Click on empty space")
                
            return original_mouse_press(event)
        
        def debug_mouse_move(event):
            if self.canvas.is_connecting:
                self.debug_info.setText("🔄 Mouse moving while connecting...")
            return original_mouse_move(event)
        
        def debug_mouse_release(event):
            if self.canvas.is_connecting:
                item = self.canvas.itemAt(event.position().toPoint())
                if item and hasattr(item, 'component'):
                    self.debug_info.setText(f"🎯 Released on: {item.component.name}")
                else:
                    self.debug_info.setText("🎯 Released on empty space")
            return original_mouse_release(event)
        
        # Replace methods
        self.canvas.start_connection = debug_start_connection
        self.canvas.end_connection = debug_end_connection
        self.canvas.create_connection = debug_create_connection
        self.canvas.mousePressEvent = debug_mouse_press
        self.canvas.mouseMoveEvent = debug_mouse_move
        self.canvas.mouseReleaseEvent = debug_mouse_release
        
    def setup_test_components(self):
        """Set up test components for connection testing."""
        
        # Create empty model
        self.gui_model = GuiModel("Debug Test Model", "A model for debugging connections")
        self.canvas.load_model(self.gui_model)
        
        # Create test components at specific positions
        components_to_create = [
            ('flow', QPointF(-100, 0), 'Test_Flow'),
            ('stock', QPointF(100, 0), 'Test_Stock'),
            ('calculator', QPointF(0, 100), 'Test_Calculator')
        ]
        
        for comp_type, position, name in components_to_create:
            # Create component using canvas method
            self.canvas.create_new_component(comp_type, position)
            
            # Rename the component for easier identification
            if self.gui_model.components:
                last_component_name = list(self.gui_model.components.keys())[-1]
                component = self.gui_model.components[last_component_name]
                # Update component name
                del self.gui_model.components[last_component_name]
                component.name = name
                self.gui_model.components[name] = component
                
                # Update visual item
                if last_component_name in self.canvas.component_items:
                    item = self.canvas.component_items[last_component_name]
                    del self.canvas.component_items[last_component_name]
                    self.canvas.component_items[name] = item
                    item.component = component
                    item.text_item.setPlainText(name)
                    item.update_text_position()
        
        self.statusBar().showMessage(f"✅ Created {len(self.gui_model.components)} test components")
        self.debug_info.setText("Components created. Now try Ctrl+Click and drag between them.")
        
    def clear_canvas(self):
        """Clear the canvas."""
        if self.canvas:
            self.canvas.clear_canvas()
            self.statusBar().showMessage("Canvas cleared")
            self.debug_info.setText("Canvas cleared")
            
    def on_component_selected(self, component):
        """Handle component selection."""
        self.statusBar().showMessage(f"Selected: {component.name}")
        
    def on_connection_created(self, from_name, to_name, conn_type):
        """Handle connection creation."""
        self.statusBar().showMessage(f"✅ Connection created: {from_name} → {to_name} ({conn_type})")
        self.debug_info.setText(f"✅ SUCCESS: {from_name} → {to_name} ({conn_type})")
        
    def on_model_modified(self):
        """Handle model modification."""
        component_count = len(self.gui_model.components) if self.gui_model else 0
        connection_count = len(self.gui_model.connections) if self.gui_model else 0
        self.statusBar().showMessage(f"Model modified - {component_count} components, {connection_count} connections")


def main():
    """Run connection debug test."""
    print("🔧 Connection Debug Test")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    window = ConnectionDebugWindow()
    window.show()
    
    print("Debug window opened. Follow the instructions in the window to test connections.")
    
    return app.exec()


if __name__ == "__main__":
    main() 