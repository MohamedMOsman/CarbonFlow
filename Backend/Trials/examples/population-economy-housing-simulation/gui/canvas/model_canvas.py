"""
Model Canvas for Visual System Dynamics Editing

This module provides a zoomable, pannable canvas for visual model design
with drag-and-drop support and component manipulation.
"""

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem,
    QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QPen, QBrush, QColor, QPainter, QFont, QTransform,
    QWheelEvent, QMouseEvent, QKeyEvent, QDragEnterEvent, QDropEvent
)
from typing import Dict, List, Optional, Tuple, Any
import math

from yaml_integration.yaml_loader import GuiModel, ModelComponent
from canvas.graphics_items import StockItem, FlowItem, CalculatorItem, AuxiliaryItem, ConnectionItem


class ModelCanvas(QGraphicsView):
    """
    Main canvas widget for visual model editing.
    
    Provides:
    - Zoomable and pannable workspace
    - Drag-and-drop component placement
    - Component selection and manipulation
    - Visual connection drawing
    """
    
    # Signals
    component_selected = pyqtSignal(object)  # Emitted when a component is selected
    component_moved = pyqtSignal(object, QPointF)  # Emitted when a component is moved
    connection_created = pyqtSignal(str, str, str)  # from_name, to_name, connection_type
    model_modified = pyqtSignal()  # Emitted when model is modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create graphics scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Canvas properties
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Zoom settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_step = 1.15
        
        # Model data
        self.gui_model = None
        self.component_items = {}  # component_name -> graphics_item
        self.connection_items = []  # List of connection graphics items
        
        # Interaction state
        self.selected_component = None
        self.is_connecting = False
        self.connection_start_item = None
        self.temp_connection_line = None
        
        # Setup canvas
        self.setup_canvas()
        self.setup_context_menu()
        self.setup_drag_drop()
        
    def setup_canvas(self):
        """Set up the canvas appearance and behavior."""
        
        # Set scene size (large workspace)
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        
        # Canvas background
        self.setBackgroundBrush(QBrush(QColor(245, 245, 245)))
        
        # Grid (optional - can be toggled)
        self.show_grid = True
        if self.show_grid:
            self.draw_grid()
            
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
    def setup_context_menu(self):
        """Set up context menu for right-click actions."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def setup_drag_drop(self):
        """Set up drag and drop functionality."""
        self.setAcceptDrops(True)
        
    def draw_grid(self):
        """Draw a grid on the canvas background."""
        grid_size = 50
        scene_rect = self.scene.sceneRect()
        
        # Create grid lines
        pen = QPen(QColor(220, 220, 220), 1, Qt.PenStyle.DotLine)
        
        # Vertical lines
        x = scene_rect.left()
        while x <= scene_rect.right():
            line = self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen)
            line.setZValue(-1000)  # Behind everything else
            x += grid_size
            
        # Horizontal lines
        y = scene_rect.top()
        while y <= scene_rect.bottom():
            line = self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen)
            line.setZValue(-1000)  # Behind everything else
            y += grid_size
            
    def load_model(self, gui_model: GuiModel):
        """Load a GUI model into the canvas."""
        
        # Clear existing items
        self.clear_canvas()
        
        # Store model reference
        self.gui_model = gui_model
        
        # Create visual items for components
        self.create_component_items()
        
        # Create visual items for connections
        self.create_connection_items()
        
        # Auto-layout if components don't have positions
        self.auto_layout_components()
        
        # Fit view to content
        QTimer.singleShot(100, self.fit_to_content)
        
    def clear_canvas(self):
        """Clear all items from the canvas."""
        self.scene.clear()
        self.component_items.clear()
        self.connection_items.clear()
        self.selected_component = None
        
        # Redraw grid if enabled
        if self.show_grid:
            self.draw_grid()
            
    def create_component_items(self):
        """Create visual items for all model components."""
        
        if not self.gui_model:
            return
            
        for component in self.gui_model.components.values():
            item = self.create_component_item(component)
            if item:
                self.component_items[component.name] = item
                self.scene.addItem(item)
                
    def create_component_item(self, component: ModelComponent):
        """Create a visual item for a single component."""
        
        if component.component_type == 'stock':
            return StockItem(component)
        elif component.component_type == 'flow':
            return FlowItem(component)
        elif component.component_type == 'calculator':
            return CalculatorItem(component)
        elif component.component_type == 'auxiliary':
            return AuxiliaryItem(component)
        else:
            # Unknown component type - create generic item
            return StockItem(component)  # Fallback to stock appearance
            
    def create_connection_items(self):
        """Create visual items for all model connections."""
        
        if not self.gui_model:
            return
            
        for from_name, to_name, conn_type in self.gui_model.connections:
            from_item = self.component_items.get(from_name)
            to_item = self.component_items.get(to_name)
            
            if from_item and to_item:
                connection_item = ConnectionItem(from_item, to_item, conn_type)
                self.connection_items.append(connection_item)
                self.scene.addItem(connection_item)
                
    def auto_layout_components(self):
        """Automatically layout components if they don't have positions."""
        
        if not self.gui_model:
            return
            
        # Simple grid layout for components without positions
        grid_size = 150
        cols = 5
        x, y = -400, -300
        col = 0
        
        for component_name, item in self.component_items.items():
            # Check if component has a stored position
            if hasattr(item.component, 'position') and item.component.position != (0, 0):
                item.setPos(QPointF(*item.component.position))
            else:
                # Auto-position
                item.setPos(QPointF(x, y))
                item.component.position = (x, y)
                
                # Move to next grid position
                col += 1
                if col >= cols:
                    col = 0
                    x = -400
                    y += grid_size
                else:
                    x += grid_size
                    
    def fit_to_content(self):
        """Fit the view to show all content."""
        if self.component_items:
            self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100))
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
    # Mouse and keyboard event handling
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        
        # Get the position of the mouse in scene coordinates
        scene_pos = self.mapToScene(event.position().toPoint())
        
        # Calculate zoom factor
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_step
        else:
            zoom_factor = 1.0 / self.zoom_step
            
        # Check zoom limits
        new_zoom = self.zoom_factor * zoom_factor
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
            
        # Apply zoom
        self.scale(zoom_factor, zoom_factor)
        self.zoom_factor = new_zoom
        
        # Keep the mouse position fixed during zoom
        new_scene_pos = self.mapToScene(event.position().toPoint())
        delta = new_scene_pos - scene_pos
        self.translate(delta.x(), delta.y())
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on an item
            item = self.itemAt(event.position().toPoint())
            
            # For connection mode, we need to find the component item even if it ignored the event
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Find component item under cursor for connection
                scene_pos = self.mapToScene(event.position().toPoint())
                items_under_cursor = self.scene.items(scene_pos)
                
                component_item = None
                for scene_item in items_under_cursor:
                    if hasattr(scene_item, 'component'):
                        component_item = scene_item
                        break
                
                if component_item:
                    self.select_component(component_item)
                    self.start_connection(component_item)
                    return
            
            if item and hasattr(item, 'component'):
                # Component clicked normally (no Ctrl)
                self.select_component(item)
                    
            else:
                # Empty space clicked - clear selection
                self.clear_selection()
                
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        
        if self.is_connecting and self.temp_connection_line:
            # Update temporary connection line
            scene_pos = self.mapToScene(event.position().toPoint())
            start_pos = self.temp_connection_line.line().p1()
            self.temp_connection_line.setLine(start_pos.x(), start_pos.y(), scene_pos.x(), scene_pos.y())
            
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        
        if self.is_connecting and event.button() == Qt.MouseButton.LeftButton:
            # Find component item under cursor for connection target
            scene_pos = self.mapToScene(event.position().toPoint())
            items_under_cursor = self.scene.items(scene_pos)
            
            target_item = None
            for scene_item in items_under_cursor:
                if hasattr(scene_item, 'component') and scene_item != self.connection_start_item:
                    target_item = scene_item
                    break
            
            if target_item:
                # Create connection
                self.create_connection(self.connection_start_item, target_item)
                
            # End connection mode
            self.end_connection()
            
        super().mouseReleaseEvent(event)
        
    def select_component(self, item):
        """Select a component item."""
        
        # Clear previous selection
        self.clear_selection()
        
        # Select new item
        self.selected_component = item
        item.setSelected(True)
        
        # Emit signal
        self.component_selected.emit(item.component)
        
    def clear_selection(self):
        """Clear component selection."""
        
        if self.selected_component:
            self.selected_component.setSelected(False)
            self.selected_component = None
            
    def start_connection(self, from_item):
        """Start creating a connection from the given item."""
        
        self.is_connecting = True
        self.connection_start_item = from_item
        
        # Temporarily disable drag mode to prevent interference
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        
        # Create temporary line
        start_pos = from_item.scenePos()
        self.temp_connection_line = self.scene.addLine(
            start_pos.x(), start_pos.y(), start_pos.x(), start_pos.y(),
            QPen(QColor(100, 100, 100), 2, Qt.PenStyle.DashLine)
        )
        
    def end_connection(self):
        """End connection creation mode."""
        
        self.is_connecting = False
        self.connection_start_item = None
        
        # Restore drag mode
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        # Remove temporary line
        if self.temp_connection_line:
            self.scene.removeItem(self.temp_connection_line)
            self.temp_connection_line = None
            
    def create_connection(self, from_item, to_item):
        """Create a connection between two items."""

        # Import here to avoid circular imports
        from components.component_types import get_valid_connection_types, is_valid_connection

        # Determine valid connection types
        from_type = from_item.component.component_type
        to_type = to_item.component.component_type

        valid_types = get_valid_connection_types(from_type, to_type)

        if not valid_types:
            QMessageBox.warning(
                self,
                "Invalid Connection",
                f"Cannot create connection from {from_type} to {to_type}.\n"
                f"This connection type is not supported."
            )
            return

        # Use first valid type (could be enhanced with user selection)
        conn_type = valid_types[0]

        # Check if connection already exists
        existing_connection = None
        for from_name, to_name, existing_type in self.gui_model.connections:
            if from_name == from_item.component.name and to_name == to_item.component.name:
                existing_connection = (from_name, to_name, existing_type)
                break

        if existing_connection:
            QMessageBox.information(
                self,
                "Connection Exists",
                f"Connection already exists: {existing_connection[0]} → {existing_connection[1]} ({existing_connection[2]})"
            )
            return

        # Add to model
        if self.gui_model:
            self.gui_model.add_connection(
                from_item.component.name,
                to_item.component.name,
                conn_type
            )

        # Create visual connection
        connection_item = ConnectionItem(from_item, to_item, conn_type)
        self.connection_items.append(connection_item)
        self.scene.addItem(connection_item)

        # Emit signals
        self.connection_created.emit(from_item.component.name, to_item.component.name, conn_type)
        self.model_modified.emit()
        
    def show_context_menu(self, position):
        """Show context menu at the given position."""
        
        menu = QMenu(self)
        
        # Add common actions
        menu.addAction("Fit to Content", self.fit_to_content)
        menu.addAction("Clear Selection", self.clear_selection)
        menu.addSeparator()
        
        # Check if right-clicking on a component
        item = self.itemAt(position)
        if item and hasattr(item, 'component'):
            menu.addAction("Delete Component", lambda: self.delete_component(item))
            menu.addAction("Edit Properties", lambda: self.edit_component_properties(item))
            
        menu.exec(self.mapToGlobal(position))
        
    def delete_component(self, item):
        """Delete a component from the model."""
        
        if not self.gui_model:
            return
            
        # Remove from model
        component_name = item.component.name
        if component_name in self.gui_model.components:
            del self.gui_model.components[component_name]
            
        # Remove connections involving this component
        self.gui_model.connections = [
            (f, t, c) for f, t, c in self.gui_model.connections
            if f != component_name and t != component_name
        ]
        
        # Remove visual items
        self.scene.removeItem(item)
        if component_name in self.component_items:
            del self.component_items[component_name]
            
        # Remove related connection items
        for conn_item in self.connection_items[:]:
            if conn_item.from_item == item or conn_item.to_item == item:
                self.scene.removeItem(conn_item)
                self.connection_items.remove(conn_item)
                
        # Emit signal
        self.model_modified.emit()
        
    def edit_component_properties(self, item):
        """Edit component properties (placeholder)."""
        QMessageBox.information(self, "Edit Properties", f"Property editing for {item.component.name} will be implemented in the inspector panel.")
        
    def get_zoom_level(self) -> float:
        """Get current zoom level."""
        return self.zoom_factor
        
    def set_zoom_level(self, zoom: float):
        """Set zoom level."""
        if self.min_zoom <= zoom <= self.max_zoom:
            scale_factor = zoom / self.zoom_factor
            self.scale(scale_factor, scale_factor)
            self.zoom_factor = zoom

    # Drag and drop event handling
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith("component_type:"):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events."""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith("component_type:"):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events to create new components."""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith("component_type:"):
                component_type = text.split(":", 1)[1]

                # Get drop position in scene coordinates
                scene_pos = self.mapToScene(event.position().toPoint())

                # Create new component
                self.create_new_component(component_type, scene_pos)

                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def create_new_component(self, component_type: str, position: QPointF):
        """Create a new component at the specified position."""

        if not self.gui_model:
            QMessageBox.warning(self, "No Model", "Please load a model first.")
            return

        # Import here to avoid circular imports
        from components.component_types import get_default_component_name, create_component_template
        from yaml_integration.yaml_loader import ModelComponent

        # Generate unique name
        existing_names = list(self.gui_model.components.keys())
        component_name = get_default_component_name(component_type, existing_names)

        # Create component template
        template = create_component_template(component_type, component_name)

        # Create ModelComponent
        component = ModelComponent(
            name=component_name,
            component_type=component_type,
            properties=template
        )

        # Set position
        component.position = (position.x(), position.y())

        # Add to model
        self.gui_model.add_component(component)

        # Create visual item
        item = self.create_component_item(component)
        if item:
            item.setPos(position)
            self.component_items[component_name] = item
            self.scene.addItem(item)

            # Select the new component
            self.select_component(item)

                    # Emit signals
        self.model_modified.emit()
