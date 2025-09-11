"""
Component Palette for System Dynamics Elements

This module provides a docked panel with draggable system dynamics components
that can be placed on the model canvas.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QToolButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QMimeData, QSize, pyqtSignal
from PyQt6.QtGui import (
    QDrag, QPainter, QPixmap, QColor, QBrush, QPen, QFont,
    QIcon, QMouseEvent
)
from typing import Dict, List, Optional

from components.component_types import ComponentType, COMPONENT_DEFINITIONS
from yaml_integration.yaml_loader import ModelComponent


class ComponentPaletteItem(QFrame):
    """A draggable item in the component palette."""
    
    def __init__(self, component_type: ComponentType, parent=None):
        super().__init__(parent)
        
        self.component_type = component_type
        
        # Setup frame appearance
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setFixedSize(80, 60)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QFrame:hover {
                background-color: #e8e8e8;
                border: 2px solid #4a90e2;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Component icon (simplified visual representation)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedHeight(30)
        self.create_component_icon()
        layout.addWidget(self.icon_label)
        
        # Component name
        name_label = QLabel(component_type.display_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setFont(QFont("Arial", 8))
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Enable drag and drop
        self.setAcceptDrops(False)  # This item is dragged, not dropped on
        
    def create_component_icon(self):
        """Create a simple icon representation of the component."""
        
        pixmap = QPixmap(30, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set colors based on component type
        if self.component_type.name == 'stock':
            fill_color = QColor(173, 216, 230)  # Light blue
            border_color = QColor(70, 130, 180)  # Steel blue
            # Draw rectangle
            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawRoundedRect(2, 2, 26, 16, 3, 3)
            
        elif self.component_type.name == 'flow':
            fill_color = QColor(255, 182, 193)  # Light pink
            border_color = QColor(220, 20, 60)   # Crimson
            # Draw arrow
            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(border_color, 2))
            points = [
                (2, 8), (20, 8), (20, 4), (28, 10), (20, 16), (20, 12), (2, 12)
            ]
            from PyQt6.QtCore import QPoint
            from PyQt6.QtGui import QPolygon
            polygon = QPolygon([QPoint(x, y) for x, y in points])
            painter.drawPolygon(polygon)
            
        elif self.component_type.name == 'calculator':
            fill_color = QColor(255, 255, 224)  # Light yellow
            border_color = QColor(255, 215, 0)   # Gold
            # Draw diamond
            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(border_color, 2))
            points = [(15, 2), (28, 10), (15, 18), (2, 10)]
            from PyQt6.QtCore import QPoint
            from PyQt6.QtGui import QPolygon
            polygon = QPolygon([QPoint(x, y) for x, y in points])
            painter.drawPolygon(polygon)
            
        elif self.component_type.name == 'auxiliary':
            fill_color = QColor(221, 160, 221)  # Plum
            border_color = QColor(147, 112, 219)  # Medium slate blue
            # Draw circle
            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawEllipse(2, 2, 26, 16)
            
        painter.end()
        self.icon_label.setPixmap(pixmap)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press to start drag operation."""
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Create drag operation
            drag = QDrag(self)
            mime_data = QMimeData()
            
            # Store component type information
            mime_data.setText(f"component_type:{self.component_type.name}")
            drag.setMimeData(mime_data)
            
            # Create drag pixmap (copy of this widget)
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.position().toPoint())
            
            # Execute drag
            drag.exec(Qt.DropAction.CopyAction)
            
        super().mousePressEvent(event)


class ComponentPalette(QWidget):
    """
    Component palette widget providing draggable system dynamics components.
    
    This widget displays available component types that can be dragged onto
    the model canvas to create new components.
    """
    
    # Signals
    component_requested = pyqtSignal(str)  # Emitted when a component type is requested
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumWidth(200)
        self.setMaximumWidth(250)
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the palette user interface."""
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Component Palette")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("QLabel { color: #333; padding: 5px; }")
        layout.addWidget(title_label)
        
        # Create scroll area for components
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create widget for scroll area content
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(10)
        
        # Add component categories
        self.create_component_categories(scroll_layout)
        
        # Add stretch to push everything to top
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Add instructions
        instructions = QLabel(
            "Drag components onto the canvas to add them to your model.\n\n"
            "To connect components:\n"
            "1. Hold Ctrl and click the source component\n"
            "2. Drag to the target component and release\n\n"
            "Valid connections:\n"
            "• Flow → Stock (inflow)\n"
            "• Stock → Flow (outflow)\n"
            "• Any component → Flow/Calculator (dependency)"
        )
        instructions.setFont(QFont("Arial", 8))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { color: #666; padding: 5px; }")
        layout.addWidget(instructions)
        
    def create_component_categories(self, layout: QVBoxLayout):
        """Create component categories with draggable items."""
        
        # Group components by category
        categories = {
            "Core Components": ['stock', 'flow'],
            "Calculations": ['calculator', 'auxiliary'],
        }
        
        for category_name, component_names in categories.items():
            # Category header
            category_label = QLabel(category_name)
            category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            category_label.setStyleSheet("QLabel { color: #555; margin-top: 10px; }")
            layout.addWidget(category_label)
            
            # Create grid layout for components in this category
            grid_layout = QVBoxLayout()
            grid_layout.setSpacing(5)
            
            # Add components in rows of 2
            row_layout = None
            for i, component_name in enumerate(component_names):
                if i % 2 == 0:
                    row_layout = QHBoxLayout()
                    row_layout.setSpacing(5)
                    grid_layout.addLayout(row_layout)
                    
                component_type = COMPONENT_DEFINITIONS.get(component_name)
                if component_type:
                    palette_item = ComponentPaletteItem(component_type)
                    row_layout.addWidget(palette_item)
                    
            # Add stretch to last row if needed
            if row_layout and len(component_names) % 2 == 1:
                row_layout.addStretch()
                
            layout.addLayout(grid_layout)
            
    def get_component_definition(self, component_type_name: str) -> Optional[ComponentType]:
        """Get component definition by type name."""
        return COMPONENT_DEFINITIONS.get(component_type_name)
        
    def create_default_component(self, component_type_name: str, name: str = None) -> ModelComponent:
        """Create a default component of the specified type."""
        
        component_type = self.get_component_definition(component_type_name)
        if not component_type:
            raise ValueError(f"Unknown component type: {component_type_name}")
            
        # Generate default name if not provided
        if not name:
            name = f"New_{component_type.display_name.replace(' ', '_')}"
            
        # Create component with default properties
        properties = component_type.default_properties.copy()
        properties['description'] = f"A {component_type.display_name.lower()} component"
        
        return ModelComponent(
            name=name,
            component_type=component_type_name,
            properties=properties
        )
