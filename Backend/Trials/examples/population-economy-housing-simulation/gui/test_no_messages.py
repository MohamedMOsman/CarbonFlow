#!/usr/bin/env python3
"""
Test script to verify that component and connection creation doesn't show message boxes.
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QPointF

from canvas.model_canvas import ModelCanvas
from yaml_integration.yaml_loader import GuiModel, ModelComponent


class TestNoMessages(unittest.TestCase):
    """Test that component creation and connections don't show message boxes."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = QApplication.instance() or QApplication([])
        self.canvas = ModelCanvas()
        
        # Create a test model
        self.gui_model = GuiModel("Test Model", "A test model")
        self.canvas.load_model(self.gui_model)
        
    def test_component_creation_no_message(self):
        """Test that creating a component doesn't show a message box."""
        
        with patch.object(QMessageBox, 'information') as mock_info:
            # Create a stock component
            self.canvas.create_new_component('stock', QPointF(100, 100))
            
            # Verify no information message was shown
            mock_info.assert_not_called()
            
            # Verify component was actually created
            self.assertEqual(len(self.gui_model.components), 1)
            
    def test_connection_creation_no_success_message(self):
        """Test that creating a valid connection doesn't show a success message."""
        
        # Create two components first
        self.canvas.create_new_component('flow', QPointF(50, 50))
        self.canvas.create_new_component('stock', QPointF(150, 50))
        
        # Get the component items
        flow_item = list(self.canvas.component_items.values())[0]
        stock_item = list(self.canvas.component_items.values())[1]
        
        with patch.object(QMessageBox, 'information') as mock_info:
            # Create a connection
            self.canvas.create_connection(flow_item, stock_item)
            
            # Verify no success message was shown
            mock_info.assert_not_called()
            
            # Verify connection was actually created
            self.assertEqual(len(self.gui_model.connections), 1)
            
    def test_invalid_connection_still_shows_warning(self):
        """Test that invalid connections still show warning messages."""
        
        # Create two incompatible components
        self.canvas.create_new_component('stock', QPointF(50, 50))
        self.canvas.create_new_component('stock', QPointF(150, 50))
        
        # Get the component items
        stock1_item = list(self.canvas.component_items.values())[0]
        stock2_item = list(self.canvas.component_items.values())[1]
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            # Try to create an invalid connection
            self.canvas.create_connection(stock1_item, stock2_item)
            
            # Verify warning was shown for invalid connection
            mock_warning.assert_called_once()
            
            # Verify no connection was created
            self.assertEqual(len(self.gui_model.connections), 0)
            
    def test_duplicate_connection_shows_info(self):
        """Test that duplicate connections still show info messages."""
        
        # Create two components
        self.canvas.create_new_component('flow', QPointF(50, 50))
        self.canvas.create_new_component('stock', QPointF(150, 50))
        
        # Get the component items
        flow_item = list(self.canvas.component_items.values())[0]
        stock_item = list(self.canvas.component_items.values())[1]
        
        # Create first connection (should be silent)
        with patch.object(QMessageBox, 'information') as mock_info:
            self.canvas.create_connection(flow_item, stock_item)
            mock_info.assert_not_called()
            
        # Try to create duplicate connection (should show info)
        with patch.object(QMessageBox, 'information') as mock_info:
            self.canvas.create_connection(flow_item, stock_item)
            mock_info.assert_called_once()
            
            # Verify only one connection exists
            self.assertEqual(len(self.gui_model.connections), 1)


def main():
    """Run the tests."""
    print("🧪 Testing No Messages Functionality")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n✅ All tests completed!")
    print("\nTo manually test:")
    print("1. Run the GUI with: python main.py")
    print("2. Create a new model or load an existing one")
    print("3. Drag components from palette to canvas")
    print("4. Verify no message appears when components are added")
    print("5. Hold Ctrl and drag between components to create connections")
    print("6. Verify no success message appears for valid connections")
    print("7. Verify warning messages still appear for invalid connections")


if __name__ == "__main__":
    main() 