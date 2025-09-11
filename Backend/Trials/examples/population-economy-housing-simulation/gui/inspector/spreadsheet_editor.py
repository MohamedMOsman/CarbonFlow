"""
Spreadsheet-Style Component Data Editor

This module provides a comprehensive Excel-like interface for editing
multidimensional system dynamics data with dynamic dimension selection
and real-time validation.
"""

import copy

# Check for PyQt6 availability
try:
    from PyQt6.QtWidgets import (
        QWidget, QTableWidget, QTableWidgetItem, QTableView, QVBoxLayout, QHBoxLayout,
        QDialog, QDialogButtonBox, QGroupBox, QFormLayout, QScrollArea,
        QSplitter, QTabWidget, QMessageBox, QInputDialog, QMenu, QApplication,
        QPushButton, QLabel, QHeaderView, QTextEdit, QLineEdit, QSpinBox,
        QComboBox, QToolBar, QStatusBar, QMainWindow, QCheckBox, QProgressBar,
        QFrame, QGridLayout, QToolButton, QFileDialog
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QModelIndex, QAbstractTableModel
    from PyQt6.QtGui import (
        QFont, QAction, QKeySequence, QClipboard, QColor, QPalette,
        QBrush, QPen, QPainter, QIcon, QUndoStack, QUndoCommand
    )
    PYQT6_AVAILABLE = True
except ImportError as e:
    PYQT6_AVAILABLE = False
    PYQT6_ERROR = str(e)

    # Create dummy classes to prevent import errors
    class QWidget: pass
    class QMainWindow: pass
    class QAbstractTableModel: pass
    class QDialog: pass
    class pyqtSignal:
        def __init__(self, *args): pass
        def emit(self, *args): pass
        def connect(self, *args): pass
from typing import Any, Dict, List, Optional, Union, Tuple, Set
import json
import copy
import csv
import io

# Import numpy if available
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Create dummy numpy for basic functionality
    class np:
        @staticmethod
        def linspace(start, stop, num):
            return [start + (stop - start) * i / (num - 1) for i in range(num)]

        @staticmethod
        def power(base, exp):
            return [base ** e for e in exp]

        @staticmethod
        def arange(num):
            return list(range(num))

        @staticmethod
        def sin(x):
            import math
            return [math.sin(val) for val in x]

# Import climate adaptation features
try:
    from .climate_adaptation_features import (
        ClimateAdaptationTemplates, ClimateValidationRules,
        DataPatternGenerator, QuickTemplateDialog
    )
    CLIMATE_FEATURES_AVAILABLE = True
except ImportError:
    CLIMATE_FEATURES_AVAILABLE = False


def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []

    if not PYQT6_AVAILABLE:
        missing_deps.append("PyQt6")

    if not NUMPY_AVAILABLE:
        missing_deps.append("numpy")

    return missing_deps


def show_dependency_error(missing_deps):
    """Show a helpful error message for missing dependencies."""
    deps_str = ", ".join(missing_deps)

    error_msg = f"""
Spreadsheet Editor Dependencies Missing

The following required packages are not installed:
{deps_str}

To install the missing dependencies, run:

    pip install {" ".join(missing_deps)}

Or if using conda:

    conda install {" ".join(missing_deps)}

Additional optional dependencies for full functionality:
    pip install PyYAML matplotlib pandas

Once installed, restart your Python environment and try again.
"""

    print(error_msg)

    # Try to show a GUI message if possible
    if PYQT6_AVAILABLE:
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])

            msg = QMessageBox()
            msg.setWindowTitle("Missing Dependencies")
            msg.setText("Spreadsheet Editor requires additional packages.")
            msg.setDetailedText(error_msg)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()
        except:
            pass  # Fall back to console message

    return error_msg


class DimensionChangeCommand(QUndoCommand):
    """Command for undoable dimension changes."""

    def __init__(self, editor, old_dims, new_dims, description="Change Dimensions"):
        super().__init__(description)

        self.editor = editor
        self.old_dims = old_dims  # (dim1, dim2)
        self.new_dims = new_dims  # (dim1, dim2)

    def redo(self):
        """Apply the dimension change."""
        if self.new_dims[0] and self.new_dims[1]:
            # Set flag to prevent signal emission during undo/redo
            self.editor.dimension_selector._updating_dimensions = True
            try:
                self.editor.dimension_selector.y_axis_zone.set_dimension(self.new_dims[0])
                self.editor.dimension_selector.x_axis_zone.set_dimension(self.new_dims[1])
                self.editor.dimension_selector.update_selection_info()
                self.editor._apply_dimension_change(self.new_dims[0], self.new_dims[1])
            finally:
                self.editor.dimension_selector._updating_dimensions = False

    def undo(self):
        """Revert the dimension change."""
        if self.old_dims[0] and self.old_dims[1]:
            # Set flag to prevent signal emission during undo/redo
            self.editor.dimension_selector._updating_dimensions = True
            try:
                self.editor.dimension_selector.y_axis_zone.set_dimension(self.old_dims[0])
                self.editor.dimension_selector.x_axis_zone.set_dimension(self.old_dims[1])
                self.editor.dimension_selector.update_selection_info()
                self.editor._apply_dimension_change(self.old_dims[0], self.old_dims[1])
            finally:
                self.editor.dimension_selector._updating_dimensions = False


class SpreadsheetTableModel(QAbstractTableModel):
    """
    Custom table model for the spreadsheet editor that handles
    multidimensional data efficiently.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data storage
        self.components = []  # List of component objects
        self.dimension_1 = None  # First selected dimension
        self.dimension_2 = None  # Second selected dimension
        self.dimension_1_coords = []  # Coordinates for dimension 1
        self.dimension_2_coords = []  # Coordinates for dimension 2
        self.data_matrix = {}  # {(component_name, coord1, coord2, **filters): value}
        self.headers_horizontal = []  # Column headers
        self.headers_vertical = []  # Row headers

        # Dimension filters for additional dimensions
        self.dimension_filters = {}  # {dim_name: selected_value}

        # Metadata
        self.dimension_metadata = {}
        self.component_metadata = {}
        
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows."""
        return len(self.headers_vertical)
        
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns."""
        return len(self.headers_horizontal)
        
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Return data for the given index and role."""
        if not index.isValid():
            return None
            
        row = index.row()
        col = index.column()
        
        if row >= len(self.headers_vertical) or col >= len(self.headers_horizontal):
            return None
            
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            # Extract component and dimension 1 coordinate from row
            component_name, coord1 = self._parse_row_header(row)

            # Get dimension 2 coordinate from column
            coord2 = self.headers_horizontal[col] if col < len(self.headers_horizontal) else ""

            # Create data key including dimension filters
            key = self._create_data_key(component_name, coord1, coord2)
            return self.data_matrix.get(key, 0.0)
            
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Alternating row colors
            if row % 2 == 0:
                return QBrush(QColor(248, 248, 248))
            else:
                return QBrush(QColor(255, 255, 255))
                
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
            
        return None

    def _parse_row_header(self, row):
        """Parse component name and dimension 1 coordinate from row header."""
        if row >= len(self.headers_vertical):
            return "", ""

        row_header = self.headers_vertical[row]

        if "\n(" in row_header and row_header.endswith(")"):
            # Format: "component_name\n(coord1)"
            parts = row_header.split("\n(")
            component_name = parts[0]
            coord1 = parts[1][:-1]  # Remove closing parenthesis
            return component_name, coord1
        else:
            # Just component name
            return row_header, ""

    def _create_data_key(self, component_name, coord1, coord2):
        """Create a data key including dimension filters."""
        # Base key
        key_parts = [component_name, coord1, coord2]

        # Add dimension filters in sorted order for consistency
        # BUT exclude the current row and column dimensions since they're already in coord1/coord2
        for dim_name in sorted(self.dimension_filters.keys()):
            if dim_name != self.dimension_1 and dim_name != self.dimension_2:
                key_parts.append(f"{dim_name}:{self.dimension_filters[dim_name]}")

        return tuple(key_parts)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """Set data for the given index."""
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
            
        row = index.row()
        col = index.column()
        
        if row >= len(self.headers_vertical) or col >= len(self.headers_horizontal):
            return False
            
        # Extract component and dimension 1 coordinate from row
        component_name, coord1 = self._parse_row_header(row)

        # Get dimension 2 coordinate from column
        coord2 = self.headers_horizontal[col] if col < len(self.headers_horizontal) else ""

        # Create data key including dimension filters
        key = self._create_data_key(component_name, coord1, coord2)
        self.data_matrix[key] = value
        
        self.dataChanged.emit(index, index, [role])
        return True
        
    def flags(self, index):
        """Return item flags."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
            
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return header data."""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self.headers_horizontal):
                    return self.headers_horizontal[section]
            elif orientation == Qt.Orientation.Vertical:
                if section < len(self.headers_vertical):
                    return self.headers_vertical[section]
                    
        elif role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setBold(True)
            return font
            
        elif role == Qt.ItemDataRole.BackgroundRole:
            return QBrush(QColor(230, 230, 230))
            
        return None
        
    def set_dimensions(self, dim1_name, dim1_coords, dim2_name, dim2_coords):
        """Set the dimensions to display."""
        self.beginResetModel()

        self.dimension_1 = dim1_name  # Row dimension
        self.dimension_2 = dim2_name  # Column dimension
        self.dimension_1_coords = dim1_coords
        self.dimension_2_coords = dim2_coords

        # Update headers based on new dimensions
        self._update_headers()

        self.endResetModel()

    def _update_headers(self):
        """Update row and column headers based on current dimensions and components."""

        # Set column headers (dimension 2 coordinates)
        self.headers_horizontal = []
        if self.dimension_2_coords:
            self.headers_horizontal = list(self.dimension_2_coords)
        else:
            # Default single column if no dimension 2
            self.headers_horizontal = ["Value"]

        # Set row headers (component-dimension1 combinations)
        self.headers_vertical = []
        if self.components and self.dimension_1_coords:
            # Create rows for each component-dimension1 combination
            for component in self.components:
                for coord1 in self.dimension_1_coords:
                    row_header = f"{component.name}\n({coord1})"
                    self.headers_vertical.append(row_header)
        elif self.components:
            # Just component names if no dimension 1
            self.headers_vertical = [comp.name for comp in self.components]

    def set_available_dimensions(self, available_dimensions):
        """Set the available dimensions for coordinate matching during data restoration."""
        self._available_dimensions = available_dimensions
        
    def set_components(self, components):
        """Set the components to display."""
        self.beginResetModel()
        
        self.components = components
        self.headers_vertical = [comp.name for comp in components]
        
        self.endResetModel()
        
    def get_data_matrix(self):
        """Get the current data matrix."""
        return copy.deepcopy(self.data_matrix)

    def restore_data_matrix(self, data_matrix):
        """Restore data matrix from a previous state, handling dimension role changes."""
        if not data_matrix:
            return

        # Parse old keys and reconstruct them for the current dimension configuration
        for old_key, value in data_matrix.items():
            if value is None or value == "":
                continue

            # Parse the old key to extract all dimensional coordinates
            parsed_coords = self._parse_data_key(old_key)
            if not parsed_coords:
                continue

            component_name = parsed_coords['component']
            all_coords = parsed_coords['coordinates']  # {dim_name: coord_value}

            # Reconstruct the key for current dimension configuration
            new_key = self._reconstruct_data_key(component_name, all_coords)

            if new_key:
                # Only restore if the new key doesn't already have data
                if new_key not in self.data_matrix or not self.data_matrix[new_key]:
                    self.data_matrix[new_key] = value

        # Emit data changed signal to update the view
        if self.rowCount() > 0 and self.columnCount() > 0:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(self.rowCount() - 1, self.columnCount() - 1),
                [Qt.ItemDataRole.DisplayRole]
            )

    def _parse_data_key(self, key):
        """Parse a data key to extract component name and all dimensional coordinates."""
        if len(key) < 3:
            return None

        component_name = key[0]
        old_coord1 = key[1]  # Previous row dimension coordinate
        old_coord2 = key[2]  # Previous column dimension coordinate

        # Extract all coordinates from the key
        coordinates = {}

        # Parse filter coordinates from key parts (these we know for sure)
        for i in range(3, len(key)):
            filter_part = key[i]
            if ':' in filter_part:
                dim_name, coord_value = filter_part.split(':', 1)
                coordinates[dim_name] = coord_value

        # For the old coord1 and coord2, we need to figure out which dimensions they belong to
        # We'll try to match them against available dimension labels
        unmatched_coords = [(old_coord1, 1), (old_coord2, 2)]  # Track position for debugging

        # Get all available dimensions
        available_dims = getattr(self, '_available_dimensions', {})

        # Try to match unmatched coordinates to dimensions
        for coord, position in unmatched_coords:
            if not coord:
                continue

            # Find which dimension this coordinate belongs to
            best_match = None
            for dim_name, dim_info in available_dims.items():
                if dim_name not in coordinates:  # Don't override already known coordinates
                    labels = dim_info.get('labels', [])
                    if coord in labels:
                        # If we find a match, use it
                        best_match = dim_name
                        break

            if best_match:
                coordinates[best_match] = coord

        return {
            'component': component_name,
            'coordinates': coordinates
        }

    def _reconstruct_data_key(self, component_name, all_coords):
        """Reconstruct a data key for the current dimension configuration."""
        # Get current row and column coordinates
        current_coord1 = all_coords.get(self.dimension_1, "")
        current_coord2 = all_coords.get(self.dimension_2, "")

        # If we don't have coordinates for current row/column dimensions, skip this entry
        if not current_coord1 or not current_coord2:
            return None

        # Check if this data entry matches the current filter context
        for filter_dim, filter_value in self.dimension_filters.items():
            if filter_dim in all_coords:
                if all_coords[filter_dim] != filter_value:
                    # This data doesn't match the current filter, skip it
                    return None

        # Create the new key with current dimension configuration
        return self._create_data_key(component_name, current_coord1, current_coord2)
        
    def set_data_matrix(self, data_matrix):
        """Set the data matrix."""
        self.beginResetModel()
        self.data_matrix = copy.deepcopy(data_matrix)
        self.endResetModel()

    def get_current_dimensions(self):
        """Get the current dimension names."""
        return (self.dimension_1, self.dimension_2)

    def set_dimension_filters(self, filters):
        """Set the current dimension filters."""
        self.dimension_filters = filters.copy()

    def get_dimension_filters(self):
        """Get the current dimension filters."""
        return self.dimension_filters.copy()


class EnhancedDimensionSelector(QWidget):
    """
    Enhanced widget for selecting dimensions with drag-and-drop and dynamic management.
    """

    dimensions_changed = pyqtSignal(str, str)  # dim1_name, dim2_name
    dimension_added = pyqtSignal(dict)  # new dimension data

    def __init__(self, parent=None):
        super().__init__(parent)

        self.available_dimensions = {}  # {dim_name: {labels: [], metadata: {}}}
        self._updating_dimensions = False  # Flag to prevent recursion

        self.setup_ui()

    def setup_ui(self):
        """Set up the enhanced dimension selector UI."""

        main_layout = QVBoxLayout(self)

        # Title and controls
        header_layout = QHBoxLayout()

        title_label = QLabel("Dimension Management")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Add dimension button
        self.add_dimension_btn = QPushButton("+ Add Dimension")
        self.add_dimension_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.add_dimension_btn.clicked.connect(self.add_new_dimension)
        header_layout.addWidget(self.add_dimension_btn)

        main_layout.addLayout(header_layout)

        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Available dimensions panel
        dimensions_panel = QGroupBox("Available Dimensions")
        dimensions_layout = QVBoxLayout(dimensions_panel)

        # Dimensions scroll area
        self.dimensions_scroll = QScrollArea()
        self.dimensions_scroll.setWidgetResizable(True)
        self.dimensions_scroll.setMinimumHeight(120)
        self.dimensions_scroll.setMaximumHeight(200)

        self.dimensions_widget = QWidget()
        self.dimensions_layout = QGridLayout(self.dimensions_widget)
        self.dimensions_scroll.setWidget(self.dimensions_widget)

        dimensions_layout.addWidget(self.dimensions_scroll)

        # Instructions
        instructions = QLabel("Drag dimensions to the axis zones below")
        instructions.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 12px;")
        dimensions_layout.addWidget(instructions)

        content_splitter.addWidget(dimensions_panel)

        # Drop zones panel
        drop_zones_panel = QGroupBox("Axis Assignment")
        drop_zones_layout = QVBoxLayout(drop_zones_panel)

        # Drop zones
        zones_layout = QHBoxLayout()

        # Import the drop zone class
        from .dimension_management import DropZone

        self.x_axis_zone = DropZone("x_axis", "X-Axis (Columns)")
        self.x_axis_zone.dimension_dropped.connect(self.on_dimension_dropped)
        zones_layout.addWidget(self.x_axis_zone)

        self.y_axis_zone = DropZone("y_axis", "Y-Axis (Rows)")
        self.y_axis_zone.dimension_dropped.connect(self.on_dimension_dropped)
        zones_layout.addWidget(self.y_axis_zone)

        drop_zones_layout.addLayout(zones_layout)

        # Current selection info
        self.selection_info = QLabel("No dimensions assigned")
        self.selection_info.setStyleSheet("color: #7f8c8d; font-style: italic; text-align: center;")
        self.selection_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_zones_layout.addWidget(self.selection_info)

        # Clear button
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all_dimensions)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        drop_zones_layout.addWidget(clear_btn)

        content_splitter.addWidget(drop_zones_panel)

        # Set splitter proportions
        content_splitter.setSizes([300, 400])

        main_layout.addWidget(content_splitter)

    def set_available_dimensions(self, dimensions):
        """Set the available dimensions and update the UI."""
        self.available_dimensions = dimensions
        self.update_dimensions_panel()

    def update_dimensions_panel(self):
        """Update the dimensions panel with draggable items."""

        try:
            # Clear existing items
            for i in reversed(range(self.dimensions_layout.count())):
                child = self.dimensions_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)

            # Import the draggable item class
            from .dimension_management import DraggableDimensionItem

            # Add dimension items
            row = 0
            col = 0
            max_cols = 2

            for dim_name, dim_info in self.available_dimensions.items():
                # Validate dimension info before creating item
                if not isinstance(dim_info, dict):
                    print(f"Warning: Invalid dimension info for {dim_name}: {dim_info}")
                    continue

                # Ensure required fields exist
                if 'labels' not in dim_info:
                    dim_info['labels'] = []
                if 'type' not in dim_info:
                    dim_info['type'] = 'categorical'
                if 'size' not in dim_info:
                    dim_info['size'] = len(dim_info.get('labels', []))

                try:
                    item = DraggableDimensionItem(dim_name, dim_info)
                    self.dimensions_layout.addWidget(item, row, col)

                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Warning: Failed to create dimension item for {dim_name}: {str(e)}")
                    continue

            # Add stretch to fill remaining space
            self.dimensions_layout.setRowStretch(row + 1, 1)

        except Exception as e:
            print(f"Error updating dimensions panel: {str(e)}")
            import traceback
            traceback.print_exc()

    def on_dimension_dropped(self, zone_name, dimension_name):
        """Handle dimension drop events."""

        try:
            # Prevent recursion
            if self._updating_dimensions:
                return

            # Validate inputs
            if not zone_name or not isinstance(zone_name, str):
                print(f"Warning: Invalid zone name: {zone_name}")
                return

            if not dimension_name or not isinstance(dimension_name, str):
                print(f"Warning: Invalid dimension name: {dimension_name}")
                return

            # Validate dimension exists
            if dimension_name not in self.available_dimensions:
                print(f"Warning: Dimension '{dimension_name}' not found in available dimensions")
                return

            # Set flag to prevent recursion
            self._updating_dimensions = True

            try:
                # Clear the dimension from other zones
                try:
                    if zone_name == "x_axis":
                        if hasattr(self, 'y_axis_zone') and self.y_axis_zone.current_dimension == dimension_name:
                            self.y_axis_zone.clear_dimension()
                    elif zone_name == "y_axis":
                        if hasattr(self, 'x_axis_zone') and self.x_axis_zone.current_dimension == dimension_name:
                            self.x_axis_zone.clear_dimension()
                except Exception as e:
                    print(f"Error clearing dimension from other zones: {str(e)}")

                # Update selection info and emit signal
                try:
                    self.update_selection_info()
                except Exception as e:
                    print(f"Error updating selection info: {str(e)}")

                # Get current dimensions safely
                try:
                    x_dim = getattr(self.x_axis_zone, 'current_dimension', None) if hasattr(self, 'x_axis_zone') else None
                    y_dim = getattr(self.y_axis_zone, 'current_dimension', None) if hasattr(self, 'y_axis_zone') else None

                    if x_dim and y_dim:
                        # Validate both dimensions exist
                        if x_dim in self.available_dimensions and y_dim in self.available_dimensions:
                            self.dimensions_changed.emit(y_dim, x_dim)  # y_dim as rows, x_dim as columns
                        else:
                            print(f"Warning: One or both dimensions not available: x={x_dim}, y={y_dim}")
                except Exception as e:
                    print(f"Error emitting dimensions changed signal: {str(e)}")

            finally:
                # Always reset the flag
                self._updating_dimensions = False

        except Exception as e:
            print(f"Error in on_dimension_dropped: {str(e)}")
            import traceback
            traceback.print_exc()
            # Ensure flag is reset even on error
            self._updating_dimensions = False

    def update_selection_info(self):
        """Update the selection information display."""

        try:
            # Safely get current dimensions
            x_dim = getattr(self.x_axis_zone, 'current_dimension', None) if hasattr(self, 'x_axis_zone') else None
            y_dim = getattr(self.y_axis_zone, 'current_dimension', None) if hasattr(self, 'y_axis_zone') else None

            if x_dim and y_dim:
                try:
                    x_info = self.available_dimensions.get(x_dim, {})
                    y_info = self.available_dimensions.get(y_dim, {})

                    x_size = len(x_info.get('labels', []))
                    y_size = len(y_info.get('labels', []))

                    self.selection_info.setText(f"Table: {y_dim} ({y_size}) × {x_dim} ({x_size})")
                    self.selection_info.setStyleSheet("color: #2c3e50; font-weight: bold;")
                except Exception as e:
                    print(f"Error calculating dimension sizes: {str(e)}")
                    self.selection_info.setText(f"Table: {y_dim} × {x_dim}")
                    self.selection_info.setStyleSheet("color: #2c3e50; font-weight: bold;")

            elif x_dim or y_dim:
                assigned = x_dim or y_dim
                self.selection_info.setText(f"Assigned: {assigned} (need one more dimension)")
                self.selection_info.setStyleSheet("color: #f39c12; font-weight: bold;")
            else:
                self.selection_info.setText("No dimensions assigned")
                self.selection_info.setStyleSheet("color: #7f8c8d; font-style: italic;")

        except Exception as e:
            print(f"Error updating selection info: {str(e)}")
            # Set safe fallback
            try:
                self.selection_info.setText("Selection info unavailable")
                self.selection_info.setStyleSheet("color: #e74c3c; font-style: italic;")
            except Exception as e2:
                print(f"Error setting fallback selection info: {str(e2)}")

    def clear_all_dimensions(self):
        """Clear all dimension assignments."""
        self.x_axis_zone.clear_dimension()
        self.y_axis_zone.clear_dimension()
        self.update_selection_info()

    def add_new_dimension(self):
        """Open dialog to add a new dimension."""

        from .dimension_management import AddDimensionDialog

        dialog = AddDimensionDialog(self.available_dimensions, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            dimension_data = dialog.get_dimension_data()

            if dimension_data:
                # Add to available dimensions
                dim_name = dimension_data['name']
                dim_info = {
                    'labels': dimension_data['labels'],
                    'description': dimension_data['description'],
                    'type': dimension_data['type'],
                    'size': dimension_data['size'],
                    'metadata': dimension_data['metadata']
                }

                self.available_dimensions[dim_name] = dim_info

                # Update UI
                self.update_dimensions_panel()

                # Emit signal
                self.dimension_added.emit(dimension_data)

    def get_selected_dimensions(self):
        """Get the currently selected dimensions."""
        y_dim = self.y_axis_zone.current_dimension
        x_dim = self.x_axis_zone.current_dimension
        return y_dim, x_dim

    def set_selected_dimensions(self, dim1_name, dim2_name):
        """Set the selected dimensions programmatically."""
        try:
            # Prevent recursion
            if self._updating_dimensions:
                return

            # Validate dimension names
            if dim1_name and dim1_name not in self.available_dimensions:
                print(f"Warning: Dimension '{dim1_name}' not found in available dimensions")
                return

            if dim2_name and dim2_name not in self.available_dimensions:
                print(f"Warning: Dimension '{dim2_name}' not found in available dimensions")
                return

            # Set flag to prevent recursion
            self._updating_dimensions = True

            try:
                # Set dimensions in drop zones
                self.y_axis_zone.set_dimension(dim1_name)
                self.x_axis_zone.set_dimension(dim2_name)
                self.update_selection_info()

                # Emit the dimensions changed signal to trigger the update
                if dim1_name and dim2_name:
                    self.dimensions_changed.emit(dim1_name, dim2_name)

            finally:
                # Always reset the flag
                self._updating_dimensions = False

        except Exception as e:
            print(f"Error setting selected dimensions: {str(e)}")
            import traceback
            traceback.print_exc()
            # Ensure flag is reset even on error
            self._updating_dimensions = False


class DimensionFiltersWidget(QWidget):
    """
    Widget for filtering additional dimensions not used as rows/columns.
    """

    filters_changed = pyqtSignal(dict)  # {dim_name: selected_value}

    def __init__(self, parent=None):
        super().__init__(parent)

        self.available_dimensions = {}
        self.current_filters = {}
        self.filter_combos = {}

        self.setup_ui()

    def setup_ui(self):
        """Set up the dimension filters UI."""

        self.main_layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("Additional Dimension Filters")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        self.main_layout.addWidget(self.title_label)

        # Filters container
        self.filters_frame = QFrame()
        self.filters_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.filters_layout = QHBoxLayout(self.filters_frame)
        self.main_layout.addWidget(self.filters_frame)

        # Initially hidden
        self.hide()

    def set_available_dimensions(self, dimensions, row_dim=None, col_dim=None):
        """Set available dimensions and create filters for unused ones."""

        self.available_dimensions = dimensions

        # Clear existing filters
        for combo in self.filter_combos.values():
            combo.setParent(None)
        self.filter_combos.clear()
        self.current_filters.clear()

        # Find dimensions not used as rows or columns
        unused_dimensions = {}
        for dim_name, dim_info in dimensions.items():
            if dim_name != row_dim and dim_name != col_dim:
                unused_dimensions[dim_name] = dim_info

        # Create filter combos for unused dimensions
        if unused_dimensions:
            for dim_name, dim_info in unused_dimensions.items():
                # Create label
                label = QLabel(f"{dim_name}:")
                label.setStyleSheet("font-weight: bold; color: #495057;")
                self.filters_layout.addWidget(label)

                # Create combo box
                combo = QComboBox()
                combo.addItems(dim_info.get('labels', []))
                combo.currentTextChanged.connect(lambda value, name=dim_name: self.on_filter_changed(name, value))

                # Set tooltip
                description = dim_info.get('description', 'No description')
                combo.setToolTip(f"{dim_name}: {description}")

                self.filter_combos[dim_name] = combo
                self.filters_layout.addWidget(combo)

                # Set initial filter value
                if dim_info.get('labels'):
                    self.current_filters[dim_name] = dim_info['labels'][0]

            self.filters_layout.addStretch()

            # Show the widget after all filters are created
            self.show()

        else:
            self.hide()

    def on_filter_changed(self, dim_name, value):
        """Handle filter value changes."""
        self.current_filters[dim_name] = value
        self.filters_changed.emit(self.current_filters.copy())

    def get_current_filters(self):
        """Get current filter values."""
        return self.current_filters.copy()


# Keep the old class for backward compatibility
class DimensionSelector(EnhancedDimensionSelector):
    """Backward compatibility alias."""
    pass


class SpreadsheetDataEditor(QMainWindow):
    """
    Main spreadsheet-style data editor for multidimensional components.

    Provides an Excel-like interface for editing system dynamics data
    with dynamic dimension selection and comprehensive data management.
    """

    # Signals
    data_changed = pyqtSignal()
    component_modified = pyqtSignal(object)  # component
    dimension_modified = pyqtSignal(str, dict)  # dimension_name, dimension_data

    def __init__(self, components=None, model=None, parent=None):
        # Check dependencies first
        missing_deps = check_dependencies()
        if missing_deps:
            show_dependency_error(missing_deps)
            raise ImportError(f"Missing required dependencies: {', '.join(missing_deps)}")

        super().__init__(parent)

        self.components = components or []
        self.model = model
        self.current_file = None
        self.is_modified = False
        self.is_locked = False  # Data locking state
        self.auto_save_enabled = True  # Auto-save on close

        # YAML integration
        self.yaml_saver = None
        self.current_gui_model = None
        self.current_model_path = None
        self.current_scenario_path = None

        # Initialize YAML saver if available
        try:
            from yaml_integration.yaml_saver import YAMLModelSaver
            self.yaml_saver = YAMLModelSaver()
        except ImportError:
            pass

        # Undo/redo system
        self.undo_stack = QUndoStack(self)

        # Setup UI
        self.setWindowTitle("Component Data Spreadsheet Editor")
        self.setMinimumSize(1000, 600)

        self.setup_ui()
        self.setup_actions()
        self.setup_toolbar()
        self.setup_statusbar()

        # Load initial data
        if self.components:
            self.load_components(self.components)
            
    def setup_ui(self):
        """Set up the main user interface."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Enhanced dimension selector
        self.dimension_selector = EnhancedDimensionSelector()
        self.dimension_selector.dimensions_changed.connect(self.on_dimensions_changed)
        self.dimension_selector.dimension_added.connect(self.on_dimension_added)
        layout.addWidget(self.dimension_selector)

        # Additional dimension filters
        self.dimension_filters = DimensionFiltersWidget()
        self.dimension_filters.filters_changed.connect(self.on_dimension_filters_changed)
        layout.addWidget(self.dimension_filters)
        
        # Main table
        self.table_model = SpreadsheetTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)

        # Table styling
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setGridStyle(Qt.PenStyle.SolidLine)
        self.table_view.setShowGrid(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)

        # Header styling and context menus
        self.table_view.horizontalHeader().setStretchLastSection(False)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        # Enable header context menus for dimension editing
        self.table_view.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.verticalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.horizontalHeader().customContextMenuRequested.connect(self.show_horizontal_header_menu)
        self.table_view.verticalHeader().customContextMenuRequested.connect(self.show_vertical_header_menu)
        
        layout.addWidget(self.table_view)

        # Ensure table view is visible
        self.table_view.show()
        
    def setup_actions(self):
        """Set up actions for the editor."""
        
        # File actions
        self.action_new = QAction("&New", self)
        self.action_new.setShortcut(QKeySequence.StandardKey.New)
        self.action_new.triggered.connect(self.new_file)
        
        self.action_open = QAction("&Open", self)
        self.action_open.setShortcut(QKeySequence.StandardKey.Open)
        self.action_open.triggered.connect(self.open_file)
        
        self.action_save = QAction("&Save", self)
        self.action_save.setShortcut(QKeySequence.StandardKey.Save)
        self.action_save.triggered.connect(self.save_file)
        
        self.action_save_as = QAction("Save &As...", self)
        self.action_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.action_save_as.triggered.connect(self.save_file_as)
        
        # Edit actions
        self.action_undo = self.undo_stack.createUndoAction(self, "&Undo")
        self.action_undo.setShortcut(QKeySequence.StandardKey.Undo)
        
        self.action_redo = self.undo_stack.createRedoAction(self, "&Redo")
        self.action_redo.setShortcut(QKeySequence.StandardKey.Redo)
        
        self.action_copy = QAction("&Copy", self)
        self.action_copy.setShortcut(QKeySequence.StandardKey.Copy)
        self.action_copy.triggered.connect(self.copy_selection)
        
        self.action_paste = QAction("&Paste", self)
        self.action_paste.setShortcut(QKeySequence.StandardKey.Paste)
        self.action_paste.triggered.connect(self.paste_selection)
        
        # Data protection actions
        self.action_lock = QAction("🔒 Lock Data", self)
        self.action_lock.setCheckable(True)
        self.action_lock.triggered.connect(self.toggle_data_lock)
        self.action_lock.setToolTip("Lock/unlock data to prevent accidental modifications")

        self.action_auto_save = QAction("Auto-save on Close", self)
        self.action_auto_save.setCheckable(True)
        self.action_auto_save.setChecked(True)
        self.action_auto_save.triggered.connect(self.toggle_auto_save)
        self.action_auto_save.setToolTip("Automatically save changes when closing the editor")

        # Data actions
        self.action_validate = QAction("&Validate Data", self)
        self.action_validate.triggered.connect(self.validate_data)

        self.action_export_csv = QAction("Export to &CSV", self)
        self.action_export_csv.triggered.connect(self.export_csv)

        self.action_import_csv = QAction("&Import from CSV", self)
        self.action_import_csv.triggered.connect(self.import_csv)

        # Climate adaptation actions
        if CLIMATE_FEATURES_AVAILABLE:
            self.action_quick_template = QAction("Apply &Template...", self)
            self.action_quick_template.triggered.connect(self.apply_quick_template)

            self.action_climate_presets = QAction("Climate &Presets...", self)
            self.action_climate_presets.triggered.connect(self.show_climate_presets)

    def setup_toolbar(self):
        """Set up the toolbar."""

        toolbar = self.addToolBar("Main")

        # File operations
        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_open)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()

        # Edit operations
        toolbar.addAction(self.action_undo)
        toolbar.addAction(self.action_redo)
        toolbar.addSeparator()
        toolbar.addAction(self.action_copy)
        toolbar.addAction(self.action_paste)
        toolbar.addSeparator()

        # Data protection
        toolbar.addAction(self.action_lock)
        toolbar.addAction(self.action_auto_save)
        toolbar.addSeparator()

        # Data operations
        toolbar.addAction(self.action_validate)
        toolbar.addAction(self.action_export_csv)
        toolbar.addAction(self.action_import_csv)

        # Climate adaptation features
        if CLIMATE_FEATURES_AVAILABLE:
            toolbar.addSeparator()
            toolbar.addAction(self.action_quick_template)
            toolbar.addAction(self.action_climate_presets)

    def setup_statusbar(self):
        """Set up the status bar."""

        self.statusbar = self.statusBar()

        # Status labels
        self.status_label = QLabel("Ready")
        self.statusbar.addWidget(self.status_label)

        self.statusbar.addPermanentWidget(QLabel("|"))

        self.dimensions_label = QLabel("No dimensions selected")
        self.statusbar.addPermanentWidget(self.dimensions_label)

        self.statusbar.addPermanentWidget(QLabel("|"))

        self.data_summary_label = QLabel("No data")
        self.statusbar.addPermanentWidget(self.data_summary_label)

    def load_components(self, components):
        """Load components into the editor."""

        self.components = components

        # Extract all available dimensions from components
        all_dimensions = {}

        for component in components:
            spatial_dims = component.properties.get('spatial_dims', [])

            for dim_name in spatial_dims:
                if dim_name not in all_dimensions:
                    # Get dimension info from model if available
                    if self.model and hasattr(self.model, 'dimensions'):
                        dim_info = self.model.dimensions.get(dim_name, {})

                        # Convert YAML dimension format to enhanced editor format
                        all_dimensions[dim_name] = self._convert_dimension_format(dim_name, dim_info)
                    else:
                        # Create default dimension info
                        all_dimensions[dim_name] = {
                            'labels': [f"{dim_name}_{i}" for i in range(3)],  # Default labels
                            'description': f'Dimension {dim_name}',
                            'type': 'categorical',
                            'size': 3,
                            'metadata': {
                                'user_created': False,
                                'source': 'default'
                            }
                        }

        # Set available dimensions
        self.dimension_selector.set_available_dimensions(all_dimensions)

        # Set components in model
        self.table_model.set_components(components)

        # Load existing multidimensional data from component properties
        self.load_existing_component_data()

        # Update dimension filters (initially no row/col dimensions selected)
        self.dimension_filters.set_available_dimensions(all_dimensions)

        # Update status
        self.update_status()

    def load_existing_component_data(self):
        """Load existing multidimensional data from component properties."""

        if not self.components:
            return

        # Collect all existing data from component properties
        existing_data = {}

        for component in self.components:
            # Check for multidimensional_data in component properties
            multidim_data = component.properties.get('multidimensional_data', {})

            if multidim_data:
                # Add existing data to our data matrix
                for key, value in multidim_data.items():
                    if isinstance(key, tuple) and len(key) > 0:
                        # Validate that the key starts with the component name
                        if key[0] == component.name:
                            existing_data[key] = value
                        else:
                            # Fix key if component name doesn't match (data migration)
                            corrected_key = tuple([component.name] + list(key[1:]))
                            existing_data[corrected_key] = value

            # Also check for legacy data formats
            initial_value = component.properties.get('initial_value')
            if isinstance(initial_value, dict) and 'sample_data' in initial_value:
                # Handle legacy sample_data format
                sample_data = initial_value['sample_data']
                for key, value in sample_data.items():
                    if isinstance(key, tuple):
                        existing_data[key] = value

        # Load the data into the table model
        if existing_data:
            print(f"Loading {len(existing_data)} existing data entries from component properties")
            self.table_model.set_data_matrix(existing_data)
            self.is_modified = False  # Data was loaded, not modified by user

            # Update status to show loaded data
            self.status_label.setText(f"Loaded {len(existing_data)} data entries from components")
        else:
            print("No existing multidimensional data found in component properties")

    def _convert_dimension_format(self, dim_name, yaml_dim_info):
        """Convert YAML dimension format to enhanced editor format."""

        try:
            # Safely extract values with defaults
            labels = yaml_dim_info.get('labels', []) if yaml_dim_info else []
            if labels is None:
                labels = []

            # Ensure all labels are strings and filter out None values
            clean_labels = []
            for label in labels:
                if label is not None:
                    clean_labels.append(str(label))
            labels = clean_labels

            size = yaml_dim_info.get('size', len(labels)) if yaml_dim_info else len(labels)
            if size is None:
                size = len(labels)

            description = yaml_dim_info.get('description', f'Dimension {dim_name}') if yaml_dim_info else f'Dimension {dim_name}'
            if description is None:
                description = f'Dimension {dim_name}'

            # Determine dimension type from YAML or infer from labels and name
            dim_type = yaml_dim_info.get('type', 'categorical') if yaml_dim_info else 'categorical'
            if not dim_type or dim_type == 'categorical':
                # Enhanced temporal dimension detection with error handling
                temporal_keywords = ['year', 'time', 'period', 'temporal', 'date', 'month', 'day', 'decade']

                # Check dimension name for temporal indicators
                name_is_temporal = False
                try:
                    name_is_temporal = any(keyword in dim_name.lower() for keyword in temporal_keywords) if dim_name else False
                except (AttributeError, TypeError):
                    name_is_temporal = False

                # Check description for temporal indicators
                desc_is_temporal = False
                try:
                    desc_is_temporal = any(keyword in description.lower() for keyword in temporal_keywords) if description else False
                except (AttributeError, TypeError):
                    desc_is_temporal = False

                # Check if labels look like years (4-digit numbers between 1900-2200)
                labels_are_years = False
                if labels:
                    try:
                        # Check if all labels are 4-digit numbers that could be years
                        year_labels = []
                        for label in labels:
                            if isinstance(label, (str, int)) and str(label).isdigit() and len(str(label)) == 4:
                                year_labels.append(int(label))
                        if len(year_labels) == len(labels) and all(1900 <= year <= 2200 for year in year_labels):
                            labels_are_years = True
                    except (ValueError, TypeError, AttributeError):
                        pass

                # Check if labels look like time periods (contain numbers and time indicators)
                labels_are_time_periods = False
                if labels:
                    try:
                        time_patterns = ['_10yr', '_5yr', 'yr', 'year', 'period', 'step', 'decade']
                        labels_are_time_periods = any(
                            any(pattern in str(label).lower() for pattern in time_patterns)
                            for label in labels if label is not None
                        )
                    except (AttributeError, TypeError):
                        pass

                # Check if dimension name contains time period indicators
                name_has_time_periods = False
                if dim_name:
                    try:
                        time_period_patterns = ['_10yr', '_5yr', 'yr', 'decade', 'period']
                        name_has_time_periods = any(pattern in dim_name.lower() for pattern in time_period_patterns)
                    except (AttributeError, TypeError):
                        pass

                # Determine if this is a temporal dimension
                if (name_is_temporal or desc_is_temporal or labels_are_years or
                    labels_are_time_periods or name_has_time_periods):
                    dim_type = 'temporal'
                elif labels:
                    try:
                        # Check if all labels are numeric
                        all_numeric = all(str(label).replace('.', '').replace('-', '').isdigit()
                                        for label in labels if label is not None)
                        if all_numeric:
                            dim_type = 'numerical'
                        else:
                            dim_type = 'categorical'
                    except (AttributeError, TypeError):
                        dim_type = 'categorical'
                else:
                    dim_type = 'categorical'

            return {
                'labels': labels,
                'description': description,
                'type': dim_type,
                'size': size,
                'metadata': {
                    'user_created': False,
                    'source': 'yaml',
                    'coordinates': yaml_dim_info.get('coordinates', []) if yaml_dim_info else [],
                    'original_yaml': yaml_dim_info
                }
            }

        except Exception as e:
            print(f"Error converting dimension format for {dim_name}: {str(e)}")
            # Return a safe default
            return {
                'labels': [],
                'description': f'Dimension {dim_name}',
                'type': 'categorical',
                'size': 0,
                'metadata': {
                    'user_created': False,
                    'source': 'error',
                    'coordinates': [],
                    'original_yaml': yaml_dim_info,
                    'error': str(e)
                }
            }

    def on_dimensions_changed(self, dim1_name, dim2_name):
        """Handle dimension selection changes."""

        if not dim1_name or not dim2_name:
            return

        # Get current dimensions for undo
        old_dims = self.table_model.get_current_dimensions() if hasattr(self.table_model, 'get_current_dimensions') else (None, None)
        new_dims = (dim1_name, dim2_name)

        # Create undo command if dimensions actually changed
        if old_dims != new_dims and old_dims != (None, None):
            command = DimensionChangeCommand(self, old_dims, new_dims, f"Change to {dim1_name} × {dim2_name}")
            self.undo_stack.push(command)
        else:
            # First time or no change, apply directly
            self._apply_dimension_change(dim1_name, dim2_name)

    def _apply_dimension_change(self, dim1_name, dim2_name):
        """Apply dimension changes (used by both direct calls and undo/redo)."""

        if not dim1_name or not dim2_name:
            return

        # Show loading indicator for large datasets
        total_cells = len(self.components) * len(self.dimension_selector.available_dimensions.get(dim1_name, {}).get('labels', [])) * len(self.dimension_selector.available_dimensions.get(dim2_name, {}).get('labels', []))

        if total_cells > 1000:
            self.show_loading_indicator("Rebuilding table...")

        try:
            # IMPORTANT: Preserve existing data before dimension change
            # The table model's data_matrix should be preserved across dimension changes
            existing_data = self.table_model.get_data_matrix() if hasattr(self.table_model, 'get_data_matrix') else {}

            # Get dimension coordinates with validation
            try:
                dim1_info = self.dimension_selector.available_dimensions.get(dim1_name, {})
                dim2_info = self.dimension_selector.available_dimensions.get(dim2_name, {})

                dim1_coords = dim1_info.get('labels', [])
                dim2_coords = dim2_info.get('labels', [])

                # Validate coordinates
                if not isinstance(dim1_coords, list):
                    print(f"Warning: Invalid coordinates for dimension {dim1_name}: {dim1_coords}")
                    dim1_coords = []

                if not isinstance(dim2_coords, list):
                    print(f"Warning: Invalid coordinates for dimension {dim2_name}: {dim2_coords}")
                    dim2_coords = []

                # Ensure coordinates are not empty
                if not dim1_coords:
                    print(f"Warning: No coordinates found for dimension {dim1_name}")
                    dim1_coords = [f"{dim1_name}_default"]

                if not dim2_coords:
                    print(f"Warning: No coordinates found for dimension {dim2_name}")
                    dim2_coords = [f"{dim2_name}_default"]

            except Exception as e:
                print(f"Error getting dimension coordinates: {str(e)}")
                # Use safe defaults
                dim1_coords = [f"{dim1_name}_default"]
                dim2_coords = [f"{dim2_name}_default"]

            # Update dimension filters for unused dimensions
            try:
                self.dimension_filters.set_available_dimensions(
                    self.dimension_selector.available_dimensions,
                    dim1_name,
                    dim2_name
                )
            except Exception as e:
                print(f"Error updating dimension filters: {str(e)}")

            # Update table model with preserved data
            try:
                self.table_model.set_dimensions(dim1_name, dim1_coords, dim2_name, dim2_coords)
            except Exception as e:
                print(f"Error setting table model dimensions: {str(e)}")
                return

            # Provide available dimensions for coordinate matching during restoration
            try:
                self.table_model.set_available_dimensions(self.dimension_selector.available_dimensions)
            except Exception as e:
                print(f"Error setting available dimensions in table model: {str(e)}")

            # Restore the preserved data after dimension change
            if existing_data:
                try:
                    self.table_model.restore_data_matrix(existing_data)
                except Exception as e:
                    print(f"Error restoring data matrix: {str(e)}")

            # Apply current filters to the table
            try:
                self.apply_dimension_filters()
            except Exception as e:
                print(f"Error applying dimension filters: {str(e)}")

            # Rebuild table widget to match model
            try:
                self.rebuild_table()
            except Exception as e:
                print(f"Error rebuilding table: {str(e)}")

            # Update status
            try:
                self.update_status()
            except Exception as e:
                print(f"Error updating status: {str(e)}")

        finally:
            if total_cells > 1000:
                self.hide_loading_indicator()

    def on_dimension_filters_changed(self, filters):
        """Handle changes to dimension filters."""
        # The apply_dimension_filters method now handles data preservation
        self.apply_dimension_filters()

        # Update status to reflect the filter change
        self.update_status()

    def apply_dimension_filters(self):
        """Apply current dimension filters to the table model."""
        current_filters = self.dimension_filters.get_current_filters()

        # Preserve existing data before applying new filters
        existing_data = self.table_model.get_data_matrix() if hasattr(self.table_model, 'get_data_matrix') else {}

        # Update table model with filter information
        if hasattr(self.table_model, 'set_dimension_filters'):
            self.table_model.set_dimension_filters(current_filters)

        # Restore data after filter change
        if existing_data and hasattr(self.table_model, 'restore_data_matrix'):
            self.table_model.restore_data_matrix(existing_data)

        # Rebuild table to reflect filters
        self.rebuild_table()

    def on_dimension_added(self, dimension_data):
        """Handle new dimension addition."""

        try:
            # Validate dimension data
            if not isinstance(dimension_data, dict):
                print(f"Error: Invalid dimension data: {dimension_data}")
                return

            required_fields = ['name', 'labels', 'size', 'description', 'type']
            for field in required_fields:
                if field not in dimension_data:
                    print(f"Error: Missing required field '{field}' in dimension data")
                    return

            # The dimension is already added to available_dimensions by the selector
            # Also add it to the model if available
            if self.model and hasattr(self.model, 'dimensions'):
                try:
                    # Convert to YAML format and add to model
                    yaml_format = {
                        'labels': dimension_data['labels'],
                        'size': dimension_data['size'],
                        'description': dimension_data['description'],
                        'type': dimension_data['type']
                    }
                    self.model.dimensions[dimension_data['name']] = yaml_format
                except Exception as e:
                    print(f"Warning: Failed to add dimension to model: {str(e)}")

            # Update status and show confirmation
            self.status_label.setText(f"✅ Added new dimension: {dimension_data['name']} ({dimension_data['size']} values)")

            # Update dimension filters to include the new dimension
            try:
                current_dims = self.dimension_selector.get_selected_dimensions()
                self.dimension_filters.set_available_dimensions(
                    self.dimension_selector.available_dimensions,
                    current_dims[0],
                    current_dims[1]
                )
            except Exception as e:
                print(f"Warning: Failed to update dimension filters: {str(e)}")

        except Exception as e:
            print(f"Error handling dimension addition: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"❌ Error adding dimension: {str(e)}")

        # Auto-assign the new dimension if no dimensions are currently selected
        if not current_dims[0] and not current_dims[1]:
            # If we have at least one other dimension, assign both
            available_dims = list(self.dimension_selector.available_dimensions.keys())
            if len(available_dims) >= 2:
                # Find a different dimension to pair with
                other_dim = None
                for dim_name in available_dims:
                    if dim_name != dimension_data['name']:
                        other_dim = dim_name
                        break

                if other_dim:
                    self.dimension_selector.set_selected_dimensions(dimension_data['name'], other_dim)

    def show_loading_indicator(self, message="Loading..."):
        """Show a loading indicator."""

        if not hasattr(self, 'loading_label'):
            self.loading_label = QLabel()
            self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.loading_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(0, 0, 0, 0.7);
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 10px;
                    padding: 20px;
                }
            """)

        self.loading_label.setText(message)
        self.loading_label.setParent(self)
        self.loading_label.show()
        self.loading_label.raise_()

        # Position in center of window
        self.loading_label.resize(200, 80)
        center_x = (self.width() - self.loading_label.width()) // 2
        center_y = (self.height() - self.loading_label.height()) // 2
        self.loading_label.move(center_x, center_y)

        # Process events to show the indicator
        QApplication.processEvents()

    def hide_loading_indicator(self):
        """Hide the loading indicator."""
        if hasattr(self, 'loading_label'):
            self.loading_label.hide()

    def rebuild_table(self):
        """Rebuild the table view to match the model."""

        # The QTableView automatically updates when the model changes
        # We just need to ensure the model is properly set
        if self.table_model:
            # Reset the model to trigger a complete refresh
            self.table_view.setModel(None)
            self.table_view.setModel(self.table_model)

            # Resize columns to content
            self.table_view.resizeColumnsToContents()
            self.table_view.resizeRowsToContents()

            # Connect to model signals for data changes
            self.table_model.dataChanged.connect(self.on_data_changed)

    def on_data_changed(self, top_left, bottom_right, roles):
        """Handle data changes in the model."""

        # Mark as modified
        self.is_modified = True
        self.update_window_title()

        # Emit signals
        self.data_changed.emit()

        # Update status
        self.update_status()

    def update_status(self):
        """Update status bar information."""

        dim1, dim2 = self.dimension_selector.get_selected_dimensions()

        if dim1 and dim2:
            dim1_size = len(self.dimension_selector.available_dimensions.get(dim1, {}).get('labels', []))
            dim2_size = len(self.dimension_selector.available_dimensions.get(dim2, {}).get('labels', []))

            self.dimensions_label.setText(f"Dimensions: {dim1} ({dim1_size}) × {dim2} ({dim2_size})")

            # Data summary
            total_cells = len(self.components) * dim1_size * dim2_size
            filled_cells = len([v for v in self.table_model.data_matrix.values() if v])

            self.data_summary_label.setText(f"Data: {filled_cells}/{total_cells} cells filled")
        else:
            self.dimensions_label.setText("No dimensions selected")
            self.data_summary_label.setText("No data")

    def update_window_title(self):
        """Update window title with modification status."""

        title = "Component Data Spreadsheet Editor"

        if self.current_file:
            title += f" - {self.current_file}"

        if self.is_modified:
            title += " *"

        self.setWindowTitle(title)

    def copy_selection(self):
        """Copy selected cells to clipboard."""

        selection_model = self.table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        # Get selected indexes
        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            return

        # Group by rows
        rows_data = {}
        for index in selected_indexes:
            row = index.row()
            col = index.column()
            value = self.table_model.data(index, Qt.ItemDataRole.DisplayRole)

            if row not in rows_data:
                rows_data[row] = {}
            rows_data[row][col] = str(value) if value is not None else ""

        # Build clipboard text
        clipboard_data = []
        for row in sorted(rows_data.keys()):
            row_data = []
            for col in sorted(rows_data[row].keys()):
                row_data.append(rows_data[row][col])
            clipboard_data.append("\t".join(row_data))

        # Copy to clipboard
        clipboard_text = "\n".join(clipboard_data)
        QApplication.clipboard().setText(clipboard_text)

        self.status_label.setText(f"Copied {len(clipboard_data)} rows to clipboard")

    def paste_selection(self):
        """Paste clipboard data to selected cells."""

        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()

        if not clipboard_text:
            return

        # Parse clipboard data
        lines = clipboard_text.split('\n')
        data_rows = [line.split('\t') for line in lines if line.strip()]

        if not data_rows:
            return

        # Get starting position
        current_index = self.table_view.currentIndex()
        if not current_index.isValid():
            return

        start_row = current_index.row()
        start_col = current_index.column()

        # Paste data
        pasted_cells = 0
        for row_offset, row_data in enumerate(data_rows):
            for col_offset, cell_data in enumerate(row_data):
                target_row = start_row + row_offset
                target_col = start_col + col_offset

                if (target_row < self.table_model.rowCount() and
                    target_col < self.table_model.columnCount()):

                    index = self.table_model.index(target_row, target_col)
                    self.table_model.setData(index, cell_data, Qt.ItemDataRole.EditRole)
                    pasted_cells += 1

        self.status_label.setText(f"Pasted {pasted_cells} cells from clipboard")
        self.is_modified = True
        self.update_window_title()

    def validate_data(self):
        """Validate the current data."""

        validation_results = {
            'errors': [],
            'warnings': [],
            'info': []
        }

        # Check for empty cells
        empty_cells = 0
        invalid_cells = 0

        for row in range(self.table_model.rowCount()):
            for col in range(self.table_model.columnCount()):
                index = self.table_model.index(row, col)
                value = self.table_model.data(index, Qt.ItemDataRole.DisplayRole)
                value_str = str(value) if value is not None else ""

                if not value_str.strip():
                    empty_cells += 1
                else:
                    # Get component name for validation
                    component_name = ""
                    if row < len(self.table_model.headers_vertical):
                        component_name = self.table_model.headers_vertical[row]

                    # Use climate validation if available
                    if CLIMATE_FEATURES_AVAILABLE:
                        is_valid, error_msg = self.validate_climate_data(value_str, component_name)
                        if not is_valid:
                            validation_results['errors'].append(
                                f"Row {row+1}, Col {col+1} ({component_name}): {error_msg}"
                            )
                            invalid_cells += 1
                    else:
                        # Basic numeric validation
                        try:
                            float(value_str)
                        except ValueError:
                            # Check if it's a valid categorical value
                            pass  # For now, accept any text

        if empty_cells > 0:
            validation_results['warnings'].append(f"{empty_cells} empty cells found")

        if invalid_cells > 0:
            validation_results['errors'].append(f"{invalid_cells} invalid values found")

        # Show validation results
        self.show_validation_results(validation_results)

    def show_validation_results(self, results):
        """Show validation results to the user."""

        message = "Data Validation Results:\n\n"

        if results['errors']:
            message += "Errors:\n"
            for error in results['errors']:
                message += f"  • {error}\n"
            message += "\n"

        if results['warnings']:
            message += "Warnings:\n"
            for warning in results['warnings']:
                message += f"  • {warning}\n"
            message += "\n"

        if not results['errors'] and not results['warnings']:
            message += "✓ All data is valid!"

        QMessageBox.information(self, "Validation Results", message)

    def export_csv(self):
        """Export data to CSV file."""

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv)"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write headers
                headers = ['Component']
                for col in range(self.table_model.columnCount()):
                    header = self.table_model.headerData(col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
                    headers.append(str(header) if header else f"Col_{col}")
                writer.writerow(headers)

                # Write data
                for row in range(self.table_model.rowCount()):
                    row_data = []

                    # Row header (component name)
                    header = self.table_model.headerData(row, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole)
                    row_data.append(str(header) if header else f"Row_{row}")

                    # Cell data
                    for col in range(self.table_model.columnCount()):
                        index = self.table_model.index(row, col)
                        value = self.table_model.data(index, Qt.ItemDataRole.DisplayRole)
                        row_data.append(str(value) if value is not None else "")

                    writer.writerow(row_data)

            self.status_label.setText(f"Data exported to {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{e}")

    def import_csv(self):
        """Import data from CSV file."""

        filename, _ = QFileDialog.getOpenFileName(
            self, "Import from CSV", "", "CSV Files (*.csv)"
        )

        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)

                # Read headers
                headers = next(reader)

                # Read data
                imported_rows = 0
                for row_data in reader:
                    if len(row_data) > 1:  # Skip empty rows
                        # Find matching component row
                        component_name = row_data[0]

                        for row in range(self.table_model.rowCount()):
                            header = self.table_model.headerData(row, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole)
                            if header and str(header) == component_name:
                                # Import data for this row
                                for col, value in enumerate(row_data[1:]):
                                    if col < self.table_model.columnCount():
                                        index = self.table_model.index(row, col)
                                        self.table_model.setData(index, value, Qt.ItemDataRole.EditRole)

                                imported_rows += 1
                                break

            self.status_label.setText(f"Imported data for {imported_rows} components from {filename}")
            self.is_modified = True
            self.update_window_title()

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import data:\n{e}")

    def new_file(self):
        """Create a new file."""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        # Clear data
        self.table_model.set_data_matrix({})
        self.rebuild_table()
        self.current_file = None
        self.is_modified = False
        self.update_window_title()

    def open_file(self):
        """Open a file."""
        # Implementation would depend on file format
        pass

    def save_file(self):
        """Save the current file."""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save the file with a new name."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save As", "", "JSON Files (*.json)"
        )

        if filename:
            self.save_to_file(filename)

    def save_to_file(self, filename):
        """Save data to the specified file."""
        try:
            data = {
                'components': [comp.name for comp in self.components],
                'dimensions': self.dimension_selector.available_dimensions,
                'data_matrix': self.table_model.get_data_matrix(),
                'selected_dimensions': self.dimension_selector.get_selected_dimensions()
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            self.current_file = filename
            self.is_modified = False
            self.update_window_title()
            self.status_label.setText(f"Saved to {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{e}")

    def closeEvent(self, event):
        """Handle close event with enhanced auto-save functionality."""
        if self.is_modified:
            if self.auto_save_enabled:
                # Auto-save is enabled, try to save automatically
                try:
                    success = self.auto_save_to_yaml()
                    if success:
                        self.status_label.setText("Auto-saved changes to YAML files")
                        event.accept()
                        return
                    else:
                        # Auto-save failed, ask user what to do
                        reply = QMessageBox.question(
                            self, "Auto-save Failed",
                            "Auto-save to YAML files failed. Do you want to save manually or discard changes?",
                            QMessageBox.StandardButton.Save |
                            QMessageBox.StandardButton.Discard |
                            QMessageBox.StandardButton.Cancel
                        )
                except Exception as e:
                    # Auto-save error, ask user what to do
                    reply = QMessageBox.question(
                        self, "Auto-save Error",
                        f"Auto-save encountered an error: {str(e)}\n\nDo you want to save manually or discard changes?",
                        QMessageBox.StandardButton.Save |
                        QMessageBox.StandardButton.Discard |
                        QMessageBox.StandardButton.Cancel
                    )
            else:
                # Auto-save is disabled, ask user
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    "You have unsaved changes. Do you want to save them?",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel
                )

            if reply == QMessageBox.StandardButton.Save:
                if self.save_file():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def auto_save_to_yaml(self):
        """Automatically save changes back to YAML files."""
        try:
            # Synchronize current editor state with GUI model
            self.sync_with_gui_model()

            # Try to save using YAML saver
            if self.yaml_saver and self.current_gui_model and self.current_model_path:
                self.yaml_saver.save_model_to_file(
                    self.current_gui_model,
                    self.current_model_path,
                    self.current_scenario_path,
                    save_scenario_separately=bool(self.current_scenario_path)
                )
                self.is_modified = False
                self.update_window_title()
                return True
            elif self.model and hasattr(self.model, 'dimensions'):
                # Update model dimensions with current dimension data
                self.update_model_dimensions()

                # Update component data with current spreadsheet values
                self.update_component_data()

                # If model has save method, use it
                if hasattr(self.model, 'save_to_yaml'):
                    self.model.save_to_yaml()
                    self.is_modified = False
                    self.update_window_title()
                    return True

            # Fallback: save to JSON format
            return self.save_to_json_fallback()

        except Exception as e:
            print(f"Auto-save error: {e}")
            return False

    def update_model_dimensions(self):
        """Update the model's dimension data with current editor state."""
        if not self.model or not hasattr(self.model, 'dimensions'):
            return

        # Update model dimensions with current dimension selector data
        for dim_name, dim_data in self.dimension_selector.available_dimensions.items():
            self.model.dimensions[dim_name] = {
                'labels': dim_data.get('labels', []),
                'size': dim_data.get('size', len(dim_data.get('labels', []))),
                'description': dim_data.get('description', f'Dimension {dim_name}'),
                'type': dim_data.get('type', 'categorical')
            }

    def update_component_data(self):
        """Update component data with current spreadsheet values."""
        # Get current data matrix
        data_matrix = self.table_model.get_data_matrix()

        # Update component properties with the modified data
        for component in self.components:
            component_data = {}

            # Extract data for this component from the matrix
            for key, value in data_matrix.items():
                if isinstance(key, tuple) and len(key) > 0 and key[0] == component.name:
                    # Only store non-empty values
                    if value is not None and value != "" and value != 0:
                        component_data[key] = value

            # Store the multidimensional data in component properties
            # Always update the property, even if empty (to clear old data)
            component.properties['multidimensional_data'] = component_data

            # Emit signal that component was modified
            self.component_modified.emit(component)

    def save_to_json_fallback(self):
        """Fallback save method using JSON format."""
        try:
            if not self.current_file:
                # Generate a filename based on component names
                component_names = [comp.name for comp in self.components]
                filename = f"spreadsheet_data_{'_'.join(component_names[:2])}.json"
                self.current_file = filename

            self.save_to_file(self.current_file)
            return True
        except Exception:
            return False

    def apply_quick_template(self):
        """Apply a quick data template to selected cells."""
        if not CLIMATE_FEATURES_AVAILABLE:
            return

        selection_model = self.table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            QMessageBox.information(
                self, "No Selection",
                "Please select cells to apply the template to."
            )
            return

        # Open template dialog
        dialog = QuickTemplateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_generated_values()

            if not values:
                return

            # Apply values to selected cells
            applied_count = 0
            value_index = 0

            selected_indexes = selection_model.selectedIndexes()
            for index in selected_indexes:
                if value_index < len(values):
                    self.table_model.setData(index, str(values[value_index]), Qt.ItemDataRole.EditRole)
                    applied_count += 1
                    value_index += 1

            self.status_label.setText(f"Applied template to {applied_count} cells")
            self.is_modified = True
            self.update_window_title()

    def show_climate_presets(self):
        """Show climate adaptation preset configurations."""
        if not CLIMATE_FEATURES_AVAILABLE:
            return

        # Create preset dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Climate Adaptation Presets")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        # Preset selection
        preset_group = QGroupBox("Available Presets")
        preset_layout = QVBoxLayout(preset_group)

        templates = ClimateAdaptationTemplates.get_dimension_combinations()

        for key, template in templates.items():
            preset_btn = QPushButton(template['name'])
            preset_btn.setToolTip(template['description'])
            preset_btn.clicked.connect(
                lambda checked, k=key: self.apply_climate_preset(k, dialog)
            )
            preset_layout.addWidget(preset_btn)

        layout.addWidget(preset_group)

        # Info text
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(150)
        info_text.setText(
            "Climate Adaptation Presets:\n\n"
            "These presets configure the spreadsheet with common dimension "
            "combinations used in climate adaptation modeling. Select a preset "
            "to automatically set up the appropriate dimensions and variables."
        )
        layout.addWidget(info_text)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def apply_climate_preset(self, preset_key, dialog):
        """Apply a climate adaptation preset."""
        if not CLIMATE_FEATURES_AVAILABLE:
            return

        templates = ClimateAdaptationTemplates.get_dimension_combinations()
        template = templates.get(preset_key)

        if not template:
            return

        # Get preset dimensions
        dimensions = template['dimensions']

        if len(dimensions) >= 2:
            # Set up dimension data
            dim1_name = dimensions[0]
            dim2_name = dimensions[1]

            # Get dimension coordinates
            if dim1_name == 'parcel':
                dim1_coords = ClimateAdaptationTemplates.get_parcel_identifiers()
            elif dim1_name == 'building_type':
                dim1_coords = ClimateAdaptationTemplates.get_building_types()
            elif dim1_name == 'year_built_cohort':
                dim1_coords = ClimateAdaptationTemplates.get_cohort_periods()
            else:
                dim1_coords = [f"{dim1_name}_{i}" for i in range(3)]

            if dim2_name == 'time':
                time_dims = ClimateAdaptationTemplates.get_time_dimensions()
                dim2_coords = time_dims['annual']['labels']
            elif dim2_name == 'time_10yr':
                time_dims = ClimateAdaptationTemplates.get_time_dimensions()
                dim2_coords = time_dims['decadal']['labels']
            elif dim2_name == 'building_type':
                dim2_coords = ClimateAdaptationTemplates.get_building_types()
            elif dim2_name == 'year_built_cohort':
                dim2_coords = ClimateAdaptationTemplates.get_cohort_periods()
            else:
                dim2_coords = [f"{dim2_name}_{i}" for i in range(3)]

            # Update available dimensions
            available_dims = self.dimension_selector.available_dimensions.copy()
            available_dims[dim1_name] = {
                'labels': dim1_coords,
                'metadata': {
                    'description': f'Climate adaptation {dim1_name}',
                    'type': 'categorical',
                    'size': len(dim1_coords)
                }
            }
            available_dims[dim2_name] = {
                'labels': dim2_coords,
                'metadata': {
                    'description': f'Climate adaptation {dim2_name}',
                    'type': 'categorical',
                    'size': len(dim2_coords)
                }
            }

            self.dimension_selector.set_available_dimensions(available_dims)

            # Set selected dimensions
            self.dimension_selector.dim1_combo.setCurrentText(dim1_name)
            self.dimension_selector.dim2_combo.setCurrentText(dim2_name)

            # Update display
            self.on_dimensions_changed(dim1_name, dim2_name)

            self.status_label.setText(f"Applied {template['name']} preset")

        dialog.accept()

    def validate_climate_data(self, value, variable_name):
        """Validate data using climate adaptation rules."""
        if not CLIMATE_FEATURES_AVAILABLE:
            return True, ""

        # Determine validation type based on variable name
        if variable_name in ['basement_height_improvement_rate', 'offset_improvement_rate',
                           'structureBsmtHeight', 'structureOffsetFromGrnd']:
            return ClimateValidationRules.validate_flood_protection(value, variable_name)

        elif variable_name in ['albedoChange', 'albedoTempInt']:
            return ClimateValidationRules.validate_albedo_changes(value, variable_name)

        elif variable_name in ['population', 'housing_units']:
            return ClimateValidationRules.validate_population_data(value, variable_name)

        # Default validation
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, "Value must be a number"

    # ========== NEW ENHANCED FUNCTIONALITY ==========

    def toggle_data_lock(self):
        """Toggle data lock state."""
        self.is_locked = not self.is_locked

        # Update action text and icon
        if self.is_locked:
            self.action_lock.setText("🔓 Unlock Data")
            self.action_lock.setToolTip("Data is locked. Click to unlock and allow modifications.")
        else:
            self.action_lock.setText("🔒 Lock Data")
            self.action_lock.setToolTip("Data is unlocked. Click to lock and prevent modifications.")

        # Update table view to reflect lock state
        self.update_lock_visual_state()

        # Update status
        lock_status = "locked" if self.is_locked else "unlocked"
        self.status_label.setText(f"Data {lock_status}")

    def update_lock_visual_state(self):
        """Update visual indicators for lock state."""
        if self.is_locked:
            # Disable editing
            self.table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
            # Change appearance to indicate locked state
            self.table_view.setStyleSheet("""
                QTableView {
                    background-color: #f5f5f5;
                    color: #666666;
                }
                QTableView::item:selected {
                    background-color: #d0d0d0;
                }
            """)
        else:
            # Enable editing
            self.table_view.setEditTriggers(
                QTableView.EditTrigger.DoubleClicked |
                QTableView.EditTrigger.EditKeyPressed |
                QTableView.EditTrigger.AnyKeyPressed
            )
            # Restore normal appearance
            self.table_view.setStyleSheet("")

    def toggle_auto_save(self):
        """Toggle auto-save on close functionality."""
        self.auto_save_enabled = self.action_auto_save.isChecked()

        status = "enabled" if self.auto_save_enabled else "disabled"
        self.status_label.setText(f"Auto-save {status}")

    def show_horizontal_header_menu(self, position):
        """Show context menu for horizontal headers (column dimensions)."""
        if self.is_locked:
            return

        header = self.table_view.horizontalHeader()
        logical_index = header.logicalIndexAt(position)

        if logical_index < 0:
            return

        menu = QMenu(self)

        # Get current dimension info
        current_dim = self.table_model.dimension_2  # Horizontal = dimension 2
        if not current_dim:
            return

        # Add dimension editing actions
        edit_action = menu.addAction("Edit Dimension Labels...")
        edit_action.triggered.connect(lambda: self.edit_dimension_labels(current_dim, 'horizontal'))

        add_coord_action = menu.addAction("Add Coordinate...")
        add_coord_action.triggered.connect(lambda: self.add_dimension_coordinate(current_dim, 'horizontal'))

        if logical_index < len(self.table_model.headers_horizontal):
            remove_coord_action = menu.addAction("Remove This Coordinate")
            coord_name = self.table_model.headers_horizontal[logical_index]
            remove_coord_action.triggered.connect(lambda: self.remove_dimension_coordinate(current_dim, coord_name, 'horizontal'))

        menu.addSeparator()
        rename_action = menu.addAction("Rename Dimension...")
        rename_action.triggered.connect(lambda: self.rename_dimension(current_dim))

        menu.exec(header.mapToGlobal(position))

    def show_vertical_header_menu(self, position):
        """Show context menu for vertical headers (row dimensions)."""
        if self.is_locked:
            return

        header = self.table_view.verticalHeader()
        logical_index = header.logicalIndexAt(position)

        if logical_index < 0:
            return

        menu = QMenu(self)

        # Get current dimension info
        current_dim = self.table_model.dimension_1  # Vertical = dimension 1
        if not current_dim:
            return

        # Add dimension editing actions
        edit_action = menu.addAction("Edit Dimension Labels...")
        edit_action.triggered.connect(lambda: self.edit_dimension_labels(current_dim, 'vertical'))

        add_coord_action = menu.addAction("Add Coordinate...")
        add_coord_action.triggered.connect(lambda: self.add_dimension_coordinate(current_dim, 'vertical'))

        if logical_index < len(self.table_model.headers_vertical):
            remove_coord_action = menu.addAction("Remove This Coordinate")
            coord_name = self.table_model.headers_vertical[logical_index]
            remove_coord_action.triggered.connect(lambda: self.remove_dimension_coordinate(current_dim, coord_name, 'vertical'))

        menu.addSeparator()
        rename_action = menu.addAction("Rename Dimension...")
        rename_action.triggered.connect(lambda: self.rename_dimension(current_dim))

        menu.exec(header.mapToGlobal(position))

    def edit_dimension_labels(self, dimension_name, orientation):
        """Edit labels for a dimension."""
        if dimension_name not in self.dimension_selector.available_dimensions:
            return

        dim_data = self.dimension_selector.available_dimensions[dimension_name]
        current_labels = dim_data.get('labels', [])

        # Create dialog for editing labels
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit {dimension_name} Labels")
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # Instructions
        instructions = QLabel(f"Edit labels for dimension '{dimension_name}':")
        layout.addWidget(instructions)

        # Text area for labels (one per line)
        text_edit = QTextEdit()
        text_edit.setPlainText('\n'.join(current_labels))
        layout.addWidget(text_edit)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Parse new labels
            new_labels_text = text_edit.toPlainText().strip()
            new_labels = [label.strip() for label in new_labels_text.split('\n') if label.strip()]

            if new_labels:
                # Update dimension data
                self.update_dimension_labels(dimension_name, new_labels)

    def add_dimension_coordinate(self, dimension_name, orientation):
        """Add a new coordinate to a dimension."""
        if dimension_name not in self.dimension_selector.available_dimensions:
            return

        # Get new coordinate name
        text, ok = QInputDialog.getText(
            self,
            f"Add Coordinate to {dimension_name}",
            "Enter name for new coordinate:"
        )

        if ok and text.strip():
            coord_name = text.strip()

            # Check if coordinate already exists
            dim_data = self.dimension_selector.available_dimensions[dimension_name]
            current_labels = dim_data.get('labels', [])

            if coord_name in current_labels:
                QMessageBox.warning(self, "Duplicate Coordinate",
                                  f"Coordinate '{coord_name}' already exists in dimension '{dimension_name}'.")
                return

            # Add the new coordinate
            new_labels = current_labels + [coord_name]
            self.update_dimension_labels(dimension_name, new_labels)

    def remove_dimension_coordinate(self, dimension_name, coord_name, orientation):
        """Remove a coordinate from a dimension."""
        if dimension_name not in self.dimension_selector.available_dimensions:
            return

        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Remove Coordinate",
            f"Are you sure you want to remove coordinate '{coord_name}' from dimension '{dimension_name}'?\n\n"
            "This will delete all associated data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            dim_data = self.dimension_selector.available_dimensions[dimension_name]
            current_labels = dim_data.get('labels', [])

            if coord_name in current_labels:
                new_labels = [label for label in current_labels if label != coord_name]
                self.update_dimension_labels(dimension_name, new_labels)

    def rename_dimension(self, old_dimension_name):
        """Rename a dimension."""
        # Get new dimension name
        text, ok = QInputDialog.getText(
            self,
            f"Rename Dimension",
            f"Enter new name for dimension '{old_dimension_name}':",
            text=old_dimension_name
        )

        if ok and text.strip() and text.strip() != old_dimension_name:
            new_dimension_name = text.strip()

            # Check if new name already exists
            if new_dimension_name in self.dimension_selector.available_dimensions:
                QMessageBox.warning(self, "Duplicate Name",
                                  f"Dimension '{new_dimension_name}' already exists.")
                return

            # Perform the rename
            self.perform_dimension_rename(old_dimension_name, new_dimension_name)

    def update_dimension_labels(self, dimension_name, new_labels):
        """Update labels for a dimension and refresh the display."""
        if dimension_name not in self.dimension_selector.available_dimensions:
            return

        # Update dimension data
        dim_data = self.dimension_selector.available_dimensions[dimension_name]
        old_labels = dim_data.get('labels', [])
        dim_data['labels'] = new_labels
        dim_data['size'] = len(new_labels)

        # Mark as modified
        self.is_modified = True
        self.update_window_title()

        # Emit signal for dimension modification
        self.dimension_modified.emit(dimension_name, dim_data)

        # Rebuild table if this dimension is currently displayed
        current_dims = self.dimension_selector.get_selected_dimensions()
        if dimension_name in current_dims:
            self.rebuild_table()

        # Update status
        self.status_label.setText(f"Updated {dimension_name} labels: {len(old_labels)} → {len(new_labels)}")

    def perform_dimension_rename(self, old_name, new_name):
        """Perform dimension rename operation."""
        if old_name not in self.dimension_selector.available_dimensions:
            return

        # Get dimension data
        dim_data = self.dimension_selector.available_dimensions[old_name]

        # Update dimension selector
        del self.dimension_selector.available_dimensions[old_name]
        self.dimension_selector.available_dimensions[new_name] = dim_data

        # Update components that use this dimension
        for component in self.components:
            spatial_dims = component.properties.get('spatial_dims', [])
            if old_name in spatial_dims:
                # Replace old dimension name with new one
                new_spatial_dims = [new_name if dim == old_name else dim for dim in spatial_dims]
                component.properties['spatial_dims'] = new_spatial_dims

        # Update model dimensions if available
        if self.model and hasattr(self.model, 'dimensions') and old_name in self.model.dimensions:
            self.model.dimensions[new_name] = self.model.dimensions.pop(old_name)

        # Update current selection if needed
        current_dims = self.dimension_selector.get_selected_dimensions()
        if old_name in current_dims:
            new_dims = tuple(new_name if dim == old_name else dim for dim in current_dims)
            self.dimension_selector.set_selected_dimensions(*new_dims)

        # Update dimension filters
        self.dimension_filters.set_available_dimensions(self.dimension_selector.available_dimensions)

        # Mark as modified
        self.is_modified = True
        self.update_window_title()

        # Emit signal
        self.dimension_modified.emit(new_name, dim_data)

        # Rebuild table
        self.rebuild_table()

        # Update status
        self.status_label.setText(f"Renamed dimension: {old_name} → {new_name}")

    def set_yaml_model_info(self, gui_model, model_path=None, scenario_path=None):
        """Set YAML model information for auto-save functionality."""
        self.current_gui_model = gui_model
        self.current_model_path = model_path
        self.current_scenario_path = scenario_path

        # Update window title to show model name
        if gui_model and gui_model.name:
            self.setWindowTitle(f"Component Data Spreadsheet Editor - {gui_model.name}")

    def closeEvent(self, event):
        """Handle window close event with auto-save."""

        if self.auto_save_enabled and self.is_modified:
            try:
                # Update component data before closing
                self.update_component_data()

                # Try to auto-save
                if self.auto_save_to_yaml():
                    self.status_label.setText("Auto-saved changes before closing")
                    print("Auto-saved component data before closing editor")
                else:
                    print("Warning: Could not auto-save component data")

            except Exception as e:
                print(f"Error during auto-save on close: {e}")

        # Accept the close event
        event.accept()

    def sync_with_gui_model(self):
        """Synchronize current editor state with the GUI model."""
        if not self.current_gui_model:
            return

        # Update GUI model dimensions
        self.current_gui_model.dimensions = {}
        for dim_name, dim_data in self.dimension_selector.available_dimensions.items():
            self.current_gui_model.dimensions[dim_name] = {
                'labels': dim_data.get('labels', []),
                'size': dim_data.get('size', len(dim_data.get('labels', []))),
                'description': dim_data.get('description', f'Dimension {dim_name}'),
                'type': dim_data.get('type', 'categorical')
            }

        # Update component data in GUI model
        data_matrix = self.table_model.get_data_matrix()

        for component in self.components:
            # Find corresponding component in GUI model
            gui_component = self.current_gui_model.get_component(component.name)
            if gui_component:
                # Update component properties with current data
                component_data = {}
                for key, value in data_matrix.items():
                    if isinstance(key, tuple) and len(key) > 0 and key[0] == component.name:
                        # Only store non-empty values
                        if value is not None and value != "" and value != 0:
                            component_data[key] = value

                # Always update the multidimensional_data property
                gui_component.properties['multidimensional_data'] = component_data

                # Update spatial dimensions if they were modified
                gui_component.properties['spatial_dims'] = component.properties.get('spatial_dims', [])

                # Sync other properties that might have changed
                for prop_name in ['units', 'description', 'initial_value', 'rate', 'expression']:
                    if prop_name in component.properties:
                        gui_component.properties[prop_name] = component.properties[prop_name]
