"""
Graphics Items for System Dynamics Components

This module provides visual representations for system dynamics components:
- StockItem: Rectangular boxes for stocks
- FlowItem: Arrow/pipe shapes for flows  
- CalculatorItem: Diamond shapes for calculators
- AuxiliaryItem: Circle shapes for auxiliaries
- ConnectionItem: Lines/arrows for connections
"""

from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, 
    QGraphicsTextItem, QGraphicsLineItem, QGraphicsPolygonItem,
    QStyleOptionGraphicsItem, QWidget
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QPainter, QFont, QPolygon, QPolygonF,
    QPainterPath, QLinearGradient, QMouseEvent
)
from typing import Optional
import math

from yaml_integration.yaml_loader import ModelComponent


class BaseComponentItem(QGraphicsItem):
    """Base class for all system dynamics component visual items."""
    
    def __init__(self, component: ModelComponent):
        super().__init__()
        
        self.component = component
        self.width = 120
        self.height = 60

        # Track connections for this component
        self.connected_lines = []  # List of ConnectionItem objects

        # Visual properties
        self.border_color = QColor(50, 50, 50)
        self.fill_color = QColor(200, 200, 200)
        self.selected_color = QColor(100, 150, 255)
        self.text_color = QColor(0, 0, 0)
        
        # Interaction properties
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        # Text item for component name
        self.text_item = QGraphicsTextItem(self.component.name, self)
        self.text_item.setDefaultTextColor(self.text_color)
        self.text_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        # Center text
        self.update_text_position()
        
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the item."""
        return QRectF(-self.width/2, -self.height/2, self.width, self.height)
        
    def update_text_position(self):
        """Center the text within the component."""
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(
            -text_rect.width() / 2,
            -text_rect.height() / 2
        )
        
    def get_connection_point(self, direction: str) -> QPointF:
        """Get connection point for the given direction (top, bottom, left, right)."""
        if direction == "top":
            return QPointF(0, -self.height/2)
        elif direction == "bottom":
            return QPointF(0, self.height/2)
        elif direction == "left":
            return QPointF(-self.width/2, 0)
        elif direction == "right":
            return QPointF(self.width/2, 0)
        else:
            return QPointF(0, 0)
            
    def add_connection(self, connection_item):
        """Add a connection line to this component."""
        if connection_item not in self.connected_lines:
            self.connected_lines.append(connection_item)

    def remove_connection(self, connection_item):
        """Remove a connection line from this component."""
        if connection_item in self.connected_lines:
            self.connected_lines.remove(connection_item)

    def update_connections(self):
        """Update all connected lines when this component moves."""
        for connection in self.connected_lines:
            connection.update_line()

    def itemChange(self, change, value):
        """Handle item changes (e.g., position changes)."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # Update component position in model
            new_pos = value
            self.component.position = (new_pos.x(), new_pos.y())

        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update connected lines after position has changed
            self.update_connections()

        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        """Handle mouse press events on the component."""
        # Check if Ctrl is pressed - if so, let the view handle connection creation
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Don't accept the event - let it bubble up to the view
            event.ignore()
            return
        
        # Normal click - handle selection and movement
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events on the component."""
        # Check if Ctrl is pressed - if so, let the view handle connection creation
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            event.ignore()
            return
            
        # Normal drag - handle movement
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release events on the component."""
        # Check if Ctrl is pressed - if so, let the view handle connection creation
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            event.ignore()
            return

        # Normal release
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events to open component properties dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_properties_dialog()
        else:
            super().mouseDoubleClickEvent(event)

    def open_multidimensional_editor(self):
        """Open the spreadsheet-style component data editor for this component."""
        try:
            from inspector.spreadsheet_editor import SpreadsheetDataEditor

            # Get the model from the scene if available
            model = None
            gui_model = None
            model_path = None
            scenario_path = None

            if hasattr(self.scene(), 'gui_model'):
                model = self.scene().gui_model
                gui_model = model
            elif hasattr(self.scene(), 'parent') and hasattr(self.scene().parent(), 'gui_model'):
                model = self.scene().parent().gui_model
                gui_model = model

            # Try to get model paths from parent window
            parent_window = self.scene().parent() if hasattr(self.scene(), 'parent') else None
            if parent_window and hasattr(parent_window, 'current_model_path'):
                model_path = parent_window.current_model_path
                scenario_path = getattr(parent_window, 'current_scenario_path', None)

            # IMPORTANT: Store reference to prevent garbage collection
            # This prevents the window from closing immediately
            self.editor = SpreadsheetDataEditor([self.component], model, parent=None)

            # Set YAML model information for auto-save functionality
            if gui_model:
                self.editor.set_yaml_model_info(gui_model, model_path, scenario_path)

            self.editor.show()

            # Connect to modification signal
            self.editor.component_modified.connect(self.on_component_modified)

        except ImportError as e:
            # Show user-friendly message for missing dependencies
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                None,
                "Spreadsheet Editor",
                f"The spreadsheet editor requires additional components.\n\n"
                f"Error: {e}\n\n"
                f"Please ensure all GUI dependencies are installed:\n"
                f"pip install PyQt6 PyYAML"
            )
        except Exception as e:
            # Show detailed error for debugging
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "Editor Error",
                f"Error opening spreadsheet editor:\n\n{e}\n\n"
                f"Component: {self.component.name}\n"
                f"Type: {self.component.component_type}"
            )

    def on_component_modified(self, component):
        """Handle component modification from the editor."""
        if component == self.component:
            # Update visual representation
            self.update()

            # Emit signal if scene supports it
            if hasattr(self.scene(), 'component_modified'):
                self.scene().component_modified.emit(self.component)

    def open_properties_dialog(self):
        """Open the comprehensive component properties dialog."""
        try:
            from dialogs.component_properties_dialog import ComponentPropertiesDialog

            # Get the model from the scene if available
            model = None
            if hasattr(self.scene(), 'gui_model'):
                model = self.scene().gui_model
            elif hasattr(self.scene(), 'model'):
                model = self.scene().model

            # Open the properties dialog
            dialog = ComponentPropertiesDialog(self.component, model, parent=None)

            # Connect to modification signal
            dialog.component_modified.connect(self.on_component_modified)

            # Show the dialog
            dialog.exec()

        except ImportError as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                None,
                "Properties Dialog",
                f"The properties dialog requires additional components.\n\n"
                f"Error: {e}\n\n"
                f"Falling back to basic multidimensional editor..."
            )
            # Fallback to the original editor
            self.open_multidimensional_editor()

        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "Dialog Error",
                f"Error opening properties dialog:\n\n{e}\n\n"
                f"Component: {self.component.name}\n"
                f"Type: {self.component.component_type}"
            )

    def contextMenuEvent(self, event):
        """Handle right-click context menu."""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction

        menu = QMenu()

        # Properties action
        properties_action = QAction("📝 Properties...", menu)
        properties_action.triggered.connect(self.open_properties_dialog)
        menu.addAction(properties_action)

        # Edit Data action (if multidimensional)
        if self.component.properties.get('spatial_dims'):
            edit_data_action = QAction("📊 Edit Data...", menu)
            edit_data_action.triggered.connect(self.open_multidimensional_editor)
            menu.addAction(edit_data_action)

        menu.addSeparator()

        # Delete action
        delete_action = QAction("❌ Delete", menu)
        delete_action.triggered.connect(self.delete_component)
        menu.addAction(delete_action)

        # Show menu
        menu.exec(event.screenPos())

    def delete_component(self):
        """Delete this component."""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            None,
            "Delete Component",
            f"Delete component '{self.component.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from scene
            if self.scene():
                self.scene().removeItem(self)

            # Emit deletion signal if scene supports it
            if hasattr(self.scene(), 'component_deleted'):
                self.scene().component_deleted.emit(self.component)

    def on_component_modified(self, component):
        """Handle component modification from properties dialog."""
        if component == self.component:
            # Update visual representation
            self.update_text_position()
            self.update()

            # Emit signal if scene supports it
            if hasattr(self.scene(), 'component_modified'):
                self.scene().component_modified.emit(self.component)


class StockItem(BaseComponentItem):
    """Visual representation of a stock component (rectangular box)."""
    
    def __init__(self, component: ModelComponent):
        super().__init__(component)
        
        # Stock-specific appearance
        self.fill_color = QColor(173, 216, 230)  # Light blue
        self.border_color = QColor(70, 130, 180)  # Steel blue
        
        # Adjust size for stocks
        self.width = 100
        self.height = 50
        
        self.update_text_position()
        
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        """Paint the stock as a rectangle."""
        
        # Set up painter
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Choose colors based on selection state
        if self.isSelected():
            fill_color = self.selected_color
            border_color = self.selected_color.darker(150)
            pen_width = 3
        else:
            fill_color = self.fill_color
            border_color = self.border_color
            pen_width = 2
            
        # Create gradient fill
        gradient = QLinearGradient(0, -self.height/2, 0, self.height/2)
        gradient.setColorAt(0, fill_color.lighter(120))
        gradient.setColorAt(1, fill_color)
        
        # Draw rectangle
        rect = QRectF(-self.width/2, -self.height/2, self.width, self.height)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(border_color, pen_width))
        painter.drawRoundedRect(rect, 5, 5)
        
        # Add dimensional indicator if multidimensional
        if self.component.properties.get('spatial_dims'):
            dims = self.component.properties['spatial_dims']
            if dims:
                # Draw dimensional indicator with dimension count
                painter.setBrush(QBrush(QColor(255, 165, 0)))  # Orange
                painter.setPen(QPen(QColor(255, 140, 0), 1))

                # Indicator background
                indicator_rect = QRectF(self.width/2 - 18, -self.height/2 + 2, 16, 12)
                painter.drawRoundedRect(indicator_rect, 2, 2)

                # Dimension count text
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))
                painter.drawText(indicator_rect, Qt.AlignmentFlag.AlignCenter, str(len(dims)))

                # Show dimension names as tooltip-style text below the component
                if len(dims) <= 3:  # Only show if not too many dimensions
                    painter.setPen(QPen(QColor(100, 100, 100), 1))
                    painter.setFont(QFont("Arial", 6))
                    dims_text = ", ".join(dims[:3])
                    if len(dims) > 3:
                        dims_text += "..."

                    # Draw dimension names below the component
                    text_rect = QRectF(-self.width/2, self.height/2 + 2, self.width, 10)
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, dims_text)

                # Tooltip-like behavior could be added here
                # For now, we'll add a small "D" to indicate dimensions
                painter.setPen(QPen(QColor(255, 140, 0), 1))
                painter.setFont(QFont("Arial", 6))
                painter.drawText(QRectF(self.width/2 - 25, -self.height/2 + 2, 8, 8),
                               Qt.AlignmentFlag.AlignCenter, "D")


class FlowItem(BaseComponentItem):
    """Visual representation of a flow component (arrow/pipe shape)."""
    
    def __init__(self, component: ModelComponent):
        super().__init__(component)
        
        # Flow-specific appearance
        self.fill_color = QColor(255, 182, 193)  # Light pink
        self.border_color = QColor(220, 20, 60)   # Crimson
        
        # Adjust size for flows
        self.width = 80
        self.height = 30
        
        self.update_text_position()
        
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        """Paint the flow as an arrow shape."""
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Choose colors based on selection state
        if self.isSelected():
            fill_color = self.selected_color
            border_color = self.selected_color.darker(150)
            pen_width = 3
        else:
            fill_color = self.fill_color
            border_color = self.border_color
            pen_width = 2
            
        # Create arrow shape
        arrow = QPolygonF([
            QPointF(-self.width/2, -self.height/4),
            QPointF(self.width/3, -self.height/4),
            QPointF(self.width/3, -self.height/2),
            QPointF(self.width/2, 0),
            QPointF(self.width/3, self.height/2),
            QPointF(self.width/3, self.height/4),
            QPointF(-self.width/2, self.height/4)
        ])
        
        # Draw arrow
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, pen_width))
        painter.drawPolygon(arrow)

        # Add dimensional indicator if multidimensional
        if self.component.properties.get('spatial_dims'):
            dims = self.component.properties['spatial_dims']
            if dims:
                # Draw dimensional indicator for flows
                painter.setBrush(QBrush(QColor(255, 165, 0)))  # Orange
                painter.setPen(QPen(QColor(255, 140, 0), 1))

                # Smaller indicator for flows
                indicator_rect = QRectF(self.width/2 - 12, -self.height/2 + 1, 10, 8)
                painter.drawRoundedRect(indicator_rect, 1, 1)

                # Dimension count
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                painter.setFont(QFont("Arial", 6, QFont.Weight.Bold))
                painter.drawText(indicator_rect, Qt.AlignmentFlag.AlignCenter, str(len(dims)))


class CalculatorItem(BaseComponentItem):
    """Visual representation of a calculator component (diamond shape)."""
    
    def __init__(self, component: ModelComponent):
        super().__init__(component)
        
        # Calculator-specific appearance
        self.fill_color = QColor(255, 255, 224)  # Light yellow
        self.border_color = QColor(255, 215, 0)   # Gold
        
        # Adjust size for calculators
        self.width = 90
        self.height = 60
        
        self.update_text_position()
        
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        """Paint the calculator as a diamond shape."""
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Choose colors based on selection state
        if self.isSelected():
            fill_color = self.selected_color
            border_color = self.selected_color.darker(150)
            pen_width = 3
        else:
            fill_color = self.fill_color
            border_color = self.border_color
            pen_width = 2
            
        # Create diamond shape
        diamond = QPolygonF([
            QPointF(0, -self.height/2),
            QPointF(self.width/2, 0),
            QPointF(0, self.height/2),
            QPointF(-self.width/2, 0)
        ])
        
        # Draw diamond
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(border_color, pen_width))
        painter.drawPolygon(diamond)
        
        # Add expression indicator
        if self.component.properties.get('expression'):
            # Draw small "f(x)" indicator
            painter.setFont(QFont("Arial", 8))
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawText(QRectF(-10, self.height/2 - 15, 20, 10), Qt.AlignmentFlag.AlignCenter, "f(x)")

        # Add dimensional indicator if multidimensional
        if self.component.properties.get('spatial_dims'):
            dims = self.component.properties['spatial_dims']
            if dims:
                # Draw dimensional indicator for calculators
                painter.setBrush(QBrush(QColor(255, 165, 0)))  # Orange
                painter.setPen(QPen(QColor(255, 140, 0), 1))

                # Position in top-right corner
                indicator_rect = QRectF(self.width/2 - 15, -self.height/2 + 2, 12, 10)
                painter.drawRoundedRect(indicator_rect, 2, 2)

                # Dimension count
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                painter.setFont(QFont("Arial", 6, QFont.Weight.Bold))
                painter.drawText(indicator_rect, Qt.AlignmentFlag.AlignCenter, str(len(dims)))


class AuxiliaryItem(BaseComponentItem):
    """Visual representation of an auxiliary component (circle shape)."""
    
    def __init__(self, component: ModelComponent):
        super().__init__(component)
        
        # Auxiliary-specific appearance
        self.fill_color = QColor(221, 160, 221)  # Plum
        self.border_color = QColor(147, 112, 219)  # Medium slate blue
        
        # Adjust size for auxiliaries (circular)
        self.width = 70
        self.height = 70
        
        self.update_text_position()
        
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        """Paint the auxiliary as a circle."""
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Choose colors based on selection state
        if self.isSelected():
            fill_color = self.selected_color
            border_color = self.selected_color.darker(150)
            pen_width = 3
        else:
            fill_color = self.fill_color
            border_color = self.border_color
            pen_width = 2
            
        # Create gradient fill
        gradient = QLinearGradient(0, -self.height/2, 0, self.height/2)
        gradient.setColorAt(0, fill_color.lighter(120))
        gradient.setColorAt(1, fill_color)
        
        # Draw circle
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(border_color, pen_width))
        painter.drawEllipse(-self.width/2, -self.height/2, self.width, self.height)


class ConnectionItem(QGraphicsLineItem):
    """Visual representation of a connection between components."""
    
    def __init__(self, from_item: BaseComponentItem, to_item: BaseComponentItem, connection_type: str):
        super().__init__()

        self.from_item = from_item
        self.to_item = to_item
        self.connection_type = connection_type

        # Register this connection with both components
        self.from_item.add_connection(self)
        self.to_item.add_connection(self)

        # Connection appearance
        self.line_color = QColor(80, 80, 80)
        self.arrow_color = QColor(60, 60, 60)

        # Connection type styling
        if connection_type == 'inflow':
            self.line_color = QColor(0, 150, 0)  # Green for inflows
        elif connection_type == 'outflow':
            self.line_color = QColor(150, 0, 0)  # Red for outflows
        elif connection_type == 'dependency':
            self.line_color = QColor(100, 100, 100)  # Gray for dependencies

        # Set up line
        self.setPen(QPen(self.line_color, 2))
        self.setZValue(-1)  # Behind components

        # Update line position
        self.update_line()

    def __del__(self):
        """Clean up connection references when deleted."""
        try:
            if hasattr(self, 'from_item') and self.from_item:
                self.from_item.remove_connection(self)
            if hasattr(self, 'to_item') and self.to_item:
                self.to_item.remove_connection(self)
        except:
            # Ignore errors during cleanup
            pass

    def update_line(self):
        """Update the line position based on component positions."""

        # Get component positions
        from_pos = self.from_item.scenePos()
        to_pos = self.to_item.scenePos()

        # Calculate direction vector
        dx = to_pos.x() - from_pos.x()
        dy = to_pos.y() - from_pos.y()

        # Calculate connection points on component edges
        if abs(dx) > abs(dy):
            # Horizontal connection
            if dx > 0:
                # Left to right
                from_point = from_pos + self.from_item.get_connection_point("right")
                to_point = to_pos + self.to_item.get_connection_point("left")
            else:
                # Right to left
                from_point = from_pos + self.from_item.get_connection_point("left")
                to_point = to_pos + self.to_item.get_connection_point("right")
        else:
            # Vertical connection
            if dy > 0:
                # Top to bottom
                from_point = from_pos + self.from_item.get_connection_point("bottom")
                to_point = to_pos + self.to_item.get_connection_point("top")
            else:
                # Bottom to top
                from_point = from_pos + self.from_item.get_connection_point("top")
                to_point = to_pos + self.to_item.get_connection_point("bottom")

        self.setLine(from_point.x(), from_point.y(), to_point.x(), to_point.y())
        
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        """Paint the connection line with arrowhead."""
        
        # Draw the line
        super().paint(painter, option, widget)
        
        # Draw arrowhead
        line = self.line()
        if line.length() == 0:
            return
            
        # Calculate arrowhead
        angle = math.atan2((line.dy()), (line.dx()))
        
        arrowhead_length = 15
        arrowhead_angle = math.pi / 6  # 30 degrees
        
        # Arrowhead points
        arrowP1 = QPointF(
            line.p2().x() - arrowhead_length * math.cos(angle - arrowhead_angle),
            line.p2().y() - arrowhead_length * math.sin(angle - arrowhead_angle)
        )
        
        arrowP2 = QPointF(
            line.p2().x() - arrowhead_length * math.cos(angle + arrowhead_angle),
            line.p2().y() - arrowhead_length * math.sin(angle + arrowhead_angle)
        )
        
        # Draw arrowhead
        arrowhead = QPolygonF([line.p2(), arrowP1, arrowP2])
        painter.setBrush(QBrush(self.arrow_color))
        painter.setPen(QPen(self.arrow_color, 1))
        painter.drawPolygon(arrowhead)
