"""
Multidimensional Component Editor

This module provides interactive editors for defining and managing
multidimensional coordinates in system dynamics components.
"""

from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QDialog, QDialogButtonBox, QGroupBox, QFormLayout, QScrollArea,
    QSplitter, QTabWidget, QMessageBox, QInputDialog, QMenu, QApplication,
    QPushButton, QLabel, QHeaderView, QTextEdit, QLineEdit, QSpinBox,
    QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QAction, QKeySequence, QClipboard
from typing import Any, Dict, List, Optional, Union, Tuple
import json
import numpy as np
import copy


class DimensionTableEditor(QTableWidget):
    """
    Spreadsheet-like table editor for multidimensional coordinates.
    
    Provides Excel-like functionality for editing dimensional data:
    - Add/remove dimensions (columns)
    - Add/remove coordinate values (rows)
    - Cell editing with validation
    - Copy/paste support
    - Context menu operations
    """
    
    # Signals
    dimensions_changed = pyqtSignal()  # Emitted when dimensions are modified
    data_changed = pyqtSignal()  # Emitted when data is modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data storage
        self.dimension_names = []  # List of dimension names
        self.coordinate_data = {}  # {dim_name: [coord_values]}
        self.dimension_metadata = {}  # {dim_name: {'description': str, 'type': str}}
        
        # Setup table
        self.setup_table()
        self.setup_context_menu()
        self.setup_signals()
        
    def setup_table(self):
        """Set up table appearance and behavior."""
        
        # Table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        
        # Headers
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        # Enable sorting
        self.setSortingEnabled(True)
        
        # Initial empty state
        self.setRowCount(1)
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["Dimension"])
        
    def setup_context_menu(self):
        """Set up context menu for right-click operations."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def setup_signals(self):
        """Connect internal signals."""
        self.itemChanged.connect(self.on_item_changed)
        self.horizontalHeader().sectionDoubleClicked.connect(self.edit_dimension_name)
        
    def show_context_menu(self, position):
        """Show context menu at the given position."""
        
        menu = QMenu(self)
        
        # Dimension operations
        add_dim_action = QAction("Add Dimension", self)
        add_dim_action.triggered.connect(self.add_dimension)
        menu.addAction(add_dim_action)
        
        if self.columnCount() > 0:
            remove_dim_action = QAction("Remove Dimension", self)
            remove_dim_action.triggered.connect(self.remove_current_dimension)
            menu.addAction(remove_dim_action)
            
        menu.addSeparator()
        
        # Row operations
        add_row_action = QAction("Add Coordinate", self)
        add_row_action.triggered.connect(self.add_coordinate)
        menu.addAction(add_row_action)
        
        if self.rowCount() > 0:
            remove_row_action = QAction("Remove Coordinate", self)
            remove_row_action.triggered.connect(self.remove_current_coordinate)
            menu.addAction(remove_row_action)
            
        menu.addSeparator()
        
        # Edit operations
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_selection)
        menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_selection)
        menu.addAction(paste_action)
        
        menu.exec(self.mapToGlobal(position))
        
    def add_dimension(self):
        """Add a new dimension column."""
        
        # Get dimension name from user
        name, ok = QInputDialog.getText(
            self, "Add Dimension", "Dimension name:",
            text=f"dim_{self.columnCount() + 1}"
        )
        
        if ok and name.strip():
            name = name.strip()
            
            # Check for duplicate names
            if name in self.dimension_names:
                QMessageBox.warning(self, "Duplicate Name", 
                                  f"Dimension '{name}' already exists.")
                return
                
            # Add dimension
            self.dimension_names.append(name)
            self.coordinate_data[name] = [""] * self.rowCount()
            self.dimension_metadata[name] = {'description': '', 'type': 'categorical'}
            
            # Update table
            col_index = self.columnCount()
            self.setColumnCount(col_index + 1)
            self.setHorizontalHeaderLabels(self.dimension_names)
            
            # Fill column with empty values
            for row in range(self.rowCount()):
                self.setItem(row, col_index, QTableWidgetItem(""))
                
            self.dimensions_changed.emit()
            
    def remove_current_dimension(self):
        """Remove the currently selected dimension."""
        
        current_col = self.currentColumn()
        if current_col >= 0 and current_col < len(self.dimension_names):
            dim_name = self.dimension_names[current_col]
            
            # Confirm deletion
            reply = QMessageBox.question(
                self, "Remove Dimension",
                f"Remove dimension '{dim_name}'?\nThis will delete all coordinate data for this dimension.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Remove from data structures
                self.dimension_names.pop(current_col)
                del self.coordinate_data[dim_name]
                del self.dimension_metadata[dim_name]
                
                # Update table
                self.removeColumn(current_col)
                self.setHorizontalHeaderLabels(self.dimension_names)
                
                self.dimensions_changed.emit()
                
    def add_coordinate(self):
        """Add a new coordinate row."""
        
        row_index = self.rowCount()
        self.setRowCount(row_index + 1)
        
        # Add empty values to all dimensions
        for col, dim_name in enumerate(self.dimension_names):
            self.coordinate_data[dim_name].append("")
            self.setItem(row_index, col, QTableWidgetItem(""))
            
        self.data_changed.emit()
        
    def remove_current_coordinate(self):
        """Remove the currently selected coordinate row."""
        
        current_row = self.currentRow()
        if current_row >= 0:
            # Remove from data structures
            for dim_name in self.dimension_names:
                if current_row < len(self.coordinate_data[dim_name]):
                    self.coordinate_data[dim_name].pop(current_row)
                    
            # Update table
            self.removeRow(current_row)
            
            self.data_changed.emit()
            
    def edit_dimension_name(self, logical_index):
        """Edit dimension name when header is double-clicked."""
        
        if logical_index < len(self.dimension_names):
            old_name = self.dimension_names[logical_index]
            
            new_name, ok = QInputDialog.getText(
                self, "Edit Dimension Name", "Dimension name:",
                text=old_name
            )
            
            if ok and new_name.strip() and new_name.strip() != old_name:
                new_name = new_name.strip()
                
                # Check for duplicate names
                if new_name in self.dimension_names:
                    QMessageBox.warning(self, "Duplicate Name", 
                                      f"Dimension '{new_name}' already exists.")
                    return
                    
                # Update data structures
                self.dimension_names[logical_index] = new_name
                self.coordinate_data[new_name] = self.coordinate_data.pop(old_name)
                self.dimension_metadata[new_name] = self.dimension_metadata.pop(old_name)
                
                # Update header
                self.setHorizontalHeaderLabels(self.dimension_names)
                
                self.dimensions_changed.emit()
                
    def on_item_changed(self, item):
        """Handle item changes to update internal data."""
        
        row = item.row()
        col = item.column()
        
        if col < len(self.dimension_names):
            dim_name = self.dimension_names[col]
            value = item.text().strip()
            
            # Ensure coordinate_data list is long enough
            while len(self.coordinate_data[dim_name]) <= row:
                self.coordinate_data[dim_name].append("")
                
            self.coordinate_data[dim_name][row] = value
            
            self.data_changed.emit()
            
    def copy_selection(self):
        """Copy selected cells to clipboard."""
        
        selection = self.selectedRanges()
        if not selection:
            return
            
        # Get selected data
        clipboard_data = []
        for range_item in selection:
            for row in range(range_item.topRow(), range_item.bottomRow() + 1):
                row_data = []
                for col in range(range_item.leftColumn(), range_item.rightColumn() + 1):
                    item = self.item(row, col)
                    row_data.append(item.text() if item else "")
                clipboard_data.append("\t".join(row_data))
                
        # Copy to clipboard
        clipboard_text = "\n".join(clipboard_data)
        QApplication.clipboard().setText(clipboard_text)
        
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
        current_row = self.currentRow()
        current_col = self.currentColumn()
        
        if current_row < 0 or current_col < 0:
            return
            
        # Expand table if necessary
        needed_rows = current_row + len(data_rows)
        needed_cols = current_col + max(len(row) for row in data_rows)
        
        if needed_rows > self.rowCount():
            self.setRowCount(needed_rows)
            
        if needed_cols > self.columnCount():
            # Need to add dimensions
            for i in range(self.columnCount(), needed_cols):
                self.add_dimension()
                
        # Paste data
        for row_offset, row_data in enumerate(data_rows):
            for col_offset, cell_data in enumerate(row_data):
                target_row = current_row + row_offset
                target_col = current_col + col_offset
                
                if target_row < self.rowCount() and target_col < self.columnCount():
                    item = QTableWidgetItem(cell_data)
                    self.setItem(target_row, target_col, item)
                    
        self.data_changed.emit()
        
    def set_dimensional_data(self, dimensions: Dict[str, List[str]], 
                           metadata: Optional[Dict[str, Dict]] = None):
        """Set the dimensional data for editing."""
        
        self.dimension_names = list(dimensions.keys())
        self.coordinate_data = copy.deepcopy(dimensions)
        self.dimension_metadata = metadata or {}
        
        # Ensure all dimensions have metadata
        for dim_name in self.dimension_names:
            if dim_name not in self.dimension_metadata:
                self.dimension_metadata[dim_name] = {'description': '', 'type': 'categorical'}
                
        # Update table structure
        max_coords = max(len(coords) for coords in dimensions.values()) if dimensions else 1
        self.setRowCount(max_coords)
        self.setColumnCount(len(self.dimension_names))
        self.setHorizontalHeaderLabels(self.dimension_names)
        
        # Populate table
        for col, dim_name in enumerate(self.dimension_names):
            coords = self.coordinate_data[dim_name]
            for row in range(max_coords):
                value = coords[row] if row < len(coords) else ""
                self.setItem(row, col, QTableWidgetItem(value))
                
    def get_dimensional_data(self) -> Tuple[Dict[str, List[str]], Dict[str, Dict]]:
        """Get the current dimensional data."""
        
        # Clean up coordinate data (remove empty trailing entries)
        cleaned_data = {}
        for dim_name in self.dimension_names:
            coords = self.coordinate_data[dim_name]
            # Remove trailing empty strings
            while coords and coords[-1] == "":
                coords.pop()
            cleaned_data[dim_name] = coords
            
        return cleaned_data, self.dimension_metadata
        
    def validate_data(self) -> Dict[str, Any]:
        """Validate the current dimensional data."""
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check for empty dimension names
        for i, dim_name in enumerate(self.dimension_names):
            if not dim_name.strip():
                validation_result['errors'].append(f"Dimension {i+1} has empty name")
                validation_result['valid'] = False
                
        # Check for duplicate dimension names
        if len(set(self.dimension_names)) != len(self.dimension_names):
            validation_result['errors'].append("Duplicate dimension names found")
            validation_result['valid'] = False
            
        # Check for empty coordinates
        for dim_name, coords in self.coordinate_data.items():
            empty_coords = sum(1 for coord in coords if not coord.strip())
            if empty_coords > 0:
                validation_result['warnings'].append(
                    f"Dimension '{dim_name}' has {empty_coords} empty coordinates"
                )

        return validation_result

    def check_dimension_consistency(self, model_dimensions: Dict[str, Dict]) -> Dict[str, Any]:
        """Check consistency with model-level dimensions."""

        consistency_result = {
            'consistent': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }

        current_dims, current_metadata = self.get_dimensional_data()

        for dim_name, coords in current_dims.items():
            if dim_name in model_dimensions:
                model_dim = model_dimensions[dim_name]
                model_labels = model_dim.get('labels', [])

                # Check if coordinates match model labels
                missing_in_component = set(model_labels) - set(coords)
                extra_in_component = set(coords) - set(model_labels)

                if missing_in_component:
                    consistency_result['warnings'].append(
                        f"Dimension '{dim_name}': Missing coordinates from model: {', '.join(missing_in_component)}"
                    )

                if extra_in_component:
                    consistency_result['warnings'].append(
                        f"Dimension '{dim_name}': Extra coordinates not in model: {', '.join(extra_in_component)}"
                    )

                # Check type consistency
                model_type = model_dim.get('type', 'categorical')
                component_type = current_metadata.get(dim_name, {}).get('type', 'categorical')

                if model_type != component_type:
                    consistency_result['warnings'].append(
                        f"Dimension '{dim_name}': Type mismatch - model: {model_type}, component: {component_type}"
                    )

            else:
                # Dimension not in model
                consistency_result['suggestions'].append(
                    f"Consider adding dimension '{dim_name}' to the model dimensions"
                )

        return consistency_result


class MultidimensionalEditorDialog(QDialog):
    """
    Dialog for editing multidimensional component properties.

    Provides a comprehensive interface for:
    - Editing dimensional coordinates
    - Managing dimension metadata
    - Validating dimensional consistency
    - Previewing data structure
    """

    def __init__(self, component, model=None, parent=None):
        super().__init__(parent)

        self.component = component
        self.model = model
        self.original_data = None

        # Setup dialog
        self.setWindowTitle(f"Edit Dimensions - {component.name}")
        self.setModal(True)
        self.resize(800, 600)

        self.setup_ui()
        self.load_component_data()

    def setup_ui(self):
        """Set up the dialog user interface."""

        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel(f"Multidimensional Editor")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        component_label = QLabel(f"Component: {self.component.name} ({self.component.component_type})")
        component_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(component_label)

        layout.addLayout(header_layout)

        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Dimension editor
        left_panel = self.create_dimension_editor_panel()
        splitter.addWidget(left_panel)

        # Right panel - Metadata and preview
        right_panel = self.create_metadata_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([500, 300])

        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.accept_changes)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_changes)

        layout.addWidget(button_box)

    def create_dimension_editor_panel(self):
        """Create the dimension editor panel."""

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Panel title
        title_label = QLabel("Dimensional Coordinates")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # Instructions
        instructions = QLabel(
            "Define the dimensions and coordinate values for this component.\n"
            "Right-click for context menu options. Double-click column headers to rename dimensions."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { color: #666; margin-bottom: 10px; }")
        layout.addWidget(instructions)

        # Dimension table editor
        self.dimension_editor = DimensionTableEditor()
        self.dimension_editor.dimensions_changed.connect(self.on_dimensions_changed)
        self.dimension_editor.data_changed.connect(self.on_data_changed)
        layout.addWidget(self.dimension_editor)

        # Quick actions
        actions_layout = QHBoxLayout()

        add_dim_btn = QPushButton("Add Dimension")
        add_dim_btn.clicked.connect(self.dimension_editor.add_dimension)
        actions_layout.addWidget(add_dim_btn)

        add_coord_btn = QPushButton("Add Coordinate")
        add_coord_btn.clicked.connect(self.dimension_editor.add_coordinate)
        actions_layout.addWidget(add_coord_btn)

        actions_layout.addStretch()

        validate_btn = QPushButton("Validate")
        validate_btn.clicked.connect(self.validate_data)
        actions_layout.addWidget(validate_btn)

        layout.addLayout(actions_layout)

        return panel

    def create_metadata_panel(self):
        """Create the metadata and preview panel."""

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for different views
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Metadata tab
        metadata_tab = self.create_metadata_tab()
        tab_widget.addTab(metadata_tab, "Metadata")

        # Preview tab
        preview_tab = self.create_preview_tab()
        tab_widget.addTab(preview_tab, "Preview")

        # Validation tab
        validation_tab = self.create_validation_tab()
        tab_widget.addTab(validation_tab, "Validation")

        return panel

    def create_metadata_tab(self):
        """Create the metadata editing tab."""

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Metadata form
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)

        self.metadata_form_widget = QWidget()
        self.metadata_form_layout = QFormLayout(self.metadata_form_widget)

        form_scroll.setWidget(self.metadata_form_widget)
        layout.addWidget(form_scroll)

        return tab

    def create_preview_tab(self):
        """Create the data preview tab."""

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Preview text
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.preview_text)

        # Refresh button
        refresh_btn = QPushButton("Refresh Preview")
        refresh_btn.clicked.connect(self.update_preview)
        layout.addWidget(refresh_btn)

        return tab

    def create_validation_tab(self):
        """Create the validation results tab."""

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Validation results
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        layout.addWidget(self.validation_text)

        return tab

    def load_component_data(self):
        """Load component data into the editor."""

        # Get spatial dimensions from component
        spatial_dims = self.component.properties.get('spatial_dims', [])

        # Initialize dimensional data
        if spatial_dims and self.model and hasattr(self.model, 'dimensions'):
            # Load from model dimensions
            dimensions = {}
            metadata = {}

            for dim_name in spatial_dims:
                dim_info = self.model.dimensions.get(dim_name, {})
                labels = dim_info.get('labels', [])
                dimensions[dim_name] = labels
                metadata[dim_name] = {
                    'description': dim_info.get('description', ''),
                    'type': dim_info.get('type', 'categorical'),
                    'size': dim_info.get('size', len(labels))
                }
        else:
            # Create empty structure
            dimensions = {'dimension_1': []}
            metadata = {'dimension_1': {'description': '', 'type': 'categorical'}}

        # Store original data for comparison
        self.original_data = (copy.deepcopy(dimensions), copy.deepcopy(metadata))

        # Load into editor
        self.dimension_editor.set_dimensional_data(dimensions, metadata)

        # Update metadata form
        self.update_metadata_form()

        # Update preview
        self.update_preview()

    def update_metadata_form(self):
        """Update the metadata editing form."""

        # Clear existing form
        while self.metadata_form_layout.count():
            child = self.metadata_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get current dimensions
        dimensions, metadata = self.dimension_editor.get_dimensional_data()

        # Create form fields for each dimension
        for dim_name in dimensions.keys():
            dim_metadata = metadata.get(dim_name, {})

            # Dimension group
            group = QGroupBox(f"Dimension: {dim_name}")
            group_layout = QFormLayout(group)

            # Description
            desc_edit = QTextEdit()
            desc_edit.setMaximumHeight(60)
            desc_edit.setPlainText(dim_metadata.get('description', ''))
            desc_edit.textChanged.connect(lambda: self.on_metadata_changed())
            group_layout.addRow("Description:", desc_edit)

            # Type
            type_combo = QComboBox()
            type_combo.addItems(['categorical', 'numerical', 'temporal', 'spatial'])
            type_combo.setCurrentText(dim_metadata.get('type', 'categorical'))
            type_combo.currentTextChanged.connect(lambda: self.on_metadata_changed())
            group_layout.addRow("Type:", type_combo)

            self.metadata_form_layout.addRow(group)

    def update_preview(self):
        """Update the data preview."""

        dimensions, metadata = self.dimension_editor.get_dimensional_data()

        preview_text = "Dimensional Structure:\n"
        preview_text += "=" * 50 + "\n\n"

        for dim_name, coords in dimensions.items():
            dim_meta = metadata.get(dim_name, {})
            preview_text += f"Dimension: {dim_name}\n"
            preview_text += f"  Type: {dim_meta.get('type', 'categorical')}\n"
            preview_text += f"  Description: {dim_meta.get('description', 'No description')}\n"
            preview_text += f"  Coordinates ({len(coords)}): {', '.join(coords[:10])}"
            if len(coords) > 10:
                preview_text += f" ... and {len(coords) - 10} more"
            preview_text += "\n\n"

        # Add YAML preview
        preview_text += "YAML Configuration:\n"
        preview_text += "-" * 30 + "\n"

        yaml_config = {
            'spatial_dims': list(dimensions.keys()),
            'dimensions': {}
        }

        for dim_name, coords in dimensions.items():
            dim_meta = metadata.get(dim_name, {})
            yaml_config['dimensions'][dim_name] = {
                'labels': coords,
                'size': len(coords),
                'type': dim_meta.get('type', 'categorical'),
                'description': dim_meta.get('description', '')
            }

        try:
            import yaml
            preview_text += yaml.dump(yaml_config, default_flow_style=False, indent=2)
        except ImportError:
            # Fallback to JSON-like representation if yaml is not available
            preview_text += json.dumps(yaml_config, indent=2)

        self.preview_text.setPlainText(preview_text)

    def validate_data(self):
        """Validate the current dimensional data."""

        validation_result = self.dimension_editor.validate_data()

        # Display validation results
        validation_text = "Validation Results:\n"
        validation_text += "=" * 40 + "\n\n"

        if validation_result['valid']:
            validation_text += "✓ Data is valid!\n\n"
        else:
            validation_text += "✗ Data has errors:\n\n"

        if validation_result['errors']:
            validation_text += "Errors:\n"
            for error in validation_result['errors']:
                validation_text += f"  • {error}\n"
            validation_text += "\n"

        if validation_result['warnings']:
            validation_text += "Warnings:\n"
            for warning in validation_result['warnings']:
                validation_text += f"  • {warning}\n"
            validation_text += "\n"

        self.validation_text.setPlainText(validation_text)

        # Update status
        if validation_result['valid']:
            self.status_label.setText("✓ Data is valid")
            self.status_label.setStyleSheet("QLabel { color: green; }")
        else:
            self.status_label.setText("✗ Data has validation errors")
            self.status_label.setStyleSheet("QLabel { color: red; }")

        return validation_result

    def on_dimensions_changed(self):
        """Handle dimension structure changes."""
        self.update_metadata_form()
        self.update_preview()
        self.status_label.setText("Dimensions modified")
        self.status_label.setStyleSheet("QLabel { color: blue; }")

    def on_data_changed(self):
        """Handle data changes."""
        self.update_preview()
        self.status_label.setText("Data modified")
        self.status_label.setStyleSheet("QLabel { color: blue; }")

    def on_metadata_changed(self):
        """Handle metadata changes."""
        self.update_preview()
        self.status_label.setText("Metadata modified")
        self.status_label.setStyleSheet("QLabel { color: blue; }")

    def apply_changes(self):
        """Apply changes to the component."""

        # Validate first
        validation_result = self.validate_data()
        if not validation_result['valid']:
            QMessageBox.warning(self, "Validation Error",
                              "Cannot apply changes: data has validation errors.")
            return

        # Get current data
        dimensions, metadata = self.dimension_editor.get_dimensional_data()

        # Update component properties
        self.component.properties['spatial_dims'] = list(dimensions.keys())

        # Update model dimensions if available
        if self.model and hasattr(self.model, 'dimensions'):
            for dim_name, coords in dimensions.items():
                dim_meta = metadata.get(dim_name, {})
                self.model.dimensions[dim_name] = {
                    'labels': coords,
                    'size': len(coords),
                    'type': dim_meta.get('type', 'categorical'),
                    'description': dim_meta.get('description', '')
                }

        self.status_label.setText("✓ Changes applied")
        self.status_label.setStyleSheet("QLabel { color: green; }")

    def accept_changes(self):
        """Accept and apply changes, then close dialog."""
        self.apply_changes()
        self.accept()

    def has_changes(self):
        """Check if there are unsaved changes."""
        current_data = self.dimension_editor.get_dimensional_data()
        return current_data != self.original_data

    def check_model_consistency(self):
        """Check consistency with model-level dimensions."""
        if not self.model or not hasattr(self.model, 'dimensions'):
            return {'consistent': True, 'errors': [], 'warnings': [], 'suggestions': []}

        return self.dimension_editor.check_dimension_consistency(self.model.dimensions)
