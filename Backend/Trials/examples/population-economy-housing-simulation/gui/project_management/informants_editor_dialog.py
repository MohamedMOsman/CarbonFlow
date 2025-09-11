"""
Informants Editor Dialog

Provides a comprehensive interface for managing dimensional data and informants
separately from component definitions, with validation and integrity checking.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QLabel, QTextEdit, QComboBox, QSpinBox, QLineEdit,
    QGroupBox, QFormLayout, QMessageBox, QSplitter,
    QTreeWidget, QTreeWidgetItem, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import numpy as np
from typing import Dict, List, Optional, Any, Tuple

from .project_manager import SystemModel, Project
from .informants_manager import InformantsManager, DimensionDefinition, InformantData
from ..inspector.multidimensional_editor import DimensionTableEditor


class DimensionDefinitionWidget(QWidget):
    """Widget for editing dimension definitions."""
    
    dimension_changed = pyqtSignal()
    
    def __init__(self, dimension_def: Optional[DimensionDefinition] = None, parent=None):
        super().__init__(parent)
        self.dimension_def = dimension_def or DimensionDefinition("new_dimension", 1)
        self.setup_ui()
        self.load_dimension()
    
    def setup_ui(self):
        """Set up the dimension definition UI."""
        layout = QFormLayout(self)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_changed)
        layout.addRow("Name:", self.name_edit)
        
        # Size
        self.size_spin = QSpinBox()
        self.size_spin.setMinimum(1)
        self.size_spin.setMaximum(1000)
        self.size_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Size:", self.size_spin)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["categorical", "temporal", "spatial", "ordinal"])
        self.type_combo.currentTextChanged.connect(self.on_changed)
        layout.addRow("Type:", self.type_combo)
        
        # Units
        self.units_edit = QLineEdit()
        self.units_edit.textChanged.connect(self.on_changed)
        layout.addRow("Units:", self.units_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.textChanged.connect(self.on_changed)
        layout.addRow("Description:", self.description_edit)
        
        # Labels table
        self.labels_table = QTableWidget(0, 1)
        self.labels_table.setHorizontalHeaderLabels(["Label"])
        self.labels_table.horizontalHeader().setStretchLastSection(True)
        self.labels_table.itemChanged.connect(self.on_changed)
        layout.addRow("Labels:", self.labels_table)
        
        # Buttons for labels
        labels_buttons = QHBoxLayout()
        add_label_btn = QPushButton("Add Label")
        add_label_btn.clicked.connect(self.add_label)
        remove_label_btn = QPushButton("Remove Label")
        remove_label_btn.clicked.connect(self.remove_label)
        labels_buttons.addWidget(add_label_btn)
        labels_buttons.addWidget(remove_label_btn)
        labels_buttons.addStretch()
        layout.addRow("", labels_buttons)
    
    def load_dimension(self):
        """Load dimension definition into UI."""
        self.name_edit.setText(self.dimension_def.name)
        self.size_spin.setValue(self.dimension_def.size)
        self.type_combo.setCurrentText(self.dimension_def.dimension_type)
        self.units_edit.setText(self.dimension_def.units or "")
        self.description_edit.setPlainText(self.dimension_def.description)
        
        # Load labels
        self.labels_table.setRowCount(len(self.dimension_def.labels))
        for i, label in enumerate(self.dimension_def.labels):
            self.labels_table.setItem(i, 0, QTableWidgetItem(label))
    
    def save_dimension(self):
        """Save UI values to dimension definition."""
        self.dimension_def.name = self.name_edit.text()
        self.dimension_def.size = self.size_spin.value()
        self.dimension_def.dimension_type = self.type_combo.currentText()
        self.dimension_def.units = self.units_edit.text() or None
        self.dimension_def.description = self.description_edit.toPlainText()
        
        # Save labels
        labels = []
        for i in range(self.labels_table.rowCount()):
            item = self.labels_table.item(i, 0)
            if item and item.text():
                labels.append(item.text())
        self.dimension_def.labels = labels
    
    def add_label(self):
        """Add a new label row."""
        row = self.labels_table.rowCount()
        self.labels_table.insertRow(row)
        self.labels_table.setItem(row, 0, QTableWidgetItem(f"label_{row+1}"))
        self.on_changed()
    
    def remove_label(self):
        """Remove selected label row."""
        current_row = self.labels_table.currentRow()
        if current_row >= 0:
            self.labels_table.removeRow(current_row)
            self.on_changed()
    
    def on_changed(self):
        """Handle changes to dimension definition."""
        self.save_dimension()
        self.dimension_changed.emit()


class InformantsEditorDialog(QDialog):
    """
    Comprehensive dialog for managing system informants and dimensional data.
    
    Provides separate management of:
    - Dimension definitions with labels and metadata
    - Informant data with dimensional structure
    - Validation and integrity checking
    - Integration with component spatial_dims
    """
    
    def __init__(self, system: SystemModel, project: Project, parent=None):
        super().__init__(parent)
        
        self.system = system
        self.project = project
        self.informants_manager = InformantsManager()
        
        # Track changes
        self.modified = False
        
        self.setWindowTitle(f"Informants Manager - {system.name}")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        self.setup_ui()
        self.load_system_data()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Main tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Dimensions tab
        self.setup_dimensions_tab()
        
        # Informants tab
        self.setup_informants_tab()
        
        # Validation tab
        self.setup_validation_tab()
        
        # Preview tab
        self.setup_preview_tab()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        validate_btn = QPushButton("Validate")
        validate_btn.clicked.connect(self.validate_system)
        buttons_layout.addWidget(validate_btn)
        
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_and_accept)
        save_btn.setDefault(True)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def setup_dimensions_tab(self):
        """Set up the dimensions management tab."""
        dimensions_widget = QWidget()
        layout = QHBoxLayout(dimensions_widget)
        
        # Left panel: Dimensions list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("System Dimensions:"))
        
        self.dimensions_tree = QTreeWidget()
        self.dimensions_tree.setHeaderLabel("Dimensions")
        self.dimensions_tree.itemSelectionChanged.connect(self.on_dimension_selected)
        left_layout.addWidget(self.dimensions_tree)
        
        # Dimension buttons
        dim_buttons = QHBoxLayout()
        add_dim_btn = QPushButton("Add")
        add_dim_btn.clicked.connect(self.add_dimension)
        remove_dim_btn = QPushButton("Remove")
        remove_dim_btn.clicked.connect(self.remove_dimension)
        dim_buttons.addWidget(add_dim_btn)
        dim_buttons.addWidget(remove_dim_btn)
        dim_buttons.addStretch()
        left_layout.addLayout(dim_buttons)
        
        layout.addWidget(left_panel)
        
        # Right panel: Dimension editor
        self.dimension_editor = DimensionDefinitionWidget()
        self.dimension_editor.dimension_changed.connect(self.on_dimension_changed)
        layout.addWidget(self.dimension_editor)
        
        layout.setStretchFactor(left_panel, 1)
        layout.setStretchFactor(self.dimension_editor, 2)
        
        self.tabs.addTab(dimensions_widget, "Dimensions")
    
    def setup_informants_tab(self):
        """Set up the informants data management tab."""
        informants_widget = QWidget()
        layout = QVBoxLayout(informants_widget)
        
        # Instructions
        instructions = QLabel(
            "Informants are data containers that provide values for model parameters and initial conditions.\n"
            "They can be scalar values, arrays with dimensional structure, or function references."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { color: #666; margin-bottom: 10px; }")
        layout.addWidget(instructions)
        
        # Informants table
        self.informants_table = QTableWidget()
        self.informants_table.setColumnCount(5)
        self.informants_table.setHorizontalHeaderLabels([
            "Name", "Type", "Dimensions", "Units", "Description"
        ])
        self.informants_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.informants_table)
        
        # Informants buttons
        inf_buttons = QHBoxLayout()
        add_inf_btn = QPushButton("Add Informant")
        add_inf_btn.clicked.connect(self.add_informant)
        edit_inf_btn = QPushButton("Edit Data")
        edit_inf_btn.clicked.connect(self.edit_informant_data)
        remove_inf_btn = QPushButton("Remove")
        remove_inf_btn.clicked.connect(self.remove_informant)
        
        inf_buttons.addWidget(add_inf_btn)
        inf_buttons.addWidget(edit_inf_btn)
        inf_buttons.addWidget(remove_inf_btn)
        inf_buttons.addStretch()
        layout.addLayout(inf_buttons)
        
        self.tabs.addTab(informants_widget, "Informants")
    
    def setup_validation_tab(self):
        """Set up the validation results tab."""
        validation_widget = QWidget()
        layout = QVBoxLayout(validation_widget)
        
        layout.addWidget(QLabel("Validation Results:"))
        
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.validation_text)
        
        refresh_btn = QPushButton("Refresh Validation")
        refresh_btn.clicked.connect(self.validate_system)
        layout.addWidget(refresh_btn)
        
        self.tabs.addTab(validation_widget, "Validation")
    
    def setup_preview_tab(self):
        """Set up the YAML preview tab."""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)
        
        layout.addWidget(QLabel("YAML Preview:"))
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.preview_text)
        
        refresh_preview_btn = QPushButton("Refresh Preview")
        refresh_preview_btn.clicked.connect(self.update_preview)
        layout.addWidget(refresh_preview_btn)
        
        self.tabs.addTab(preview_widget, "Preview")
    
    def load_system_data(self):
        """Load system dimensions and informants into the UI."""
        # Load dimensions
        self.dimensions_tree.clear()
        for dim_name, dim_data in self.system.dimensions.items():
            item = QTreeWidgetItem(self.dimensions_tree)
            item.setText(0, dim_name)
            item.setData(0, Qt.ItemDataRole.UserRole, dim_data)
        
        # Load informants (extracted from system)
        self.load_informants_table()
        
        # Initial validation
        self.validate_system()
        self.update_preview()
    
    def load_informants_table(self):
        """Load informants into the table."""
        # Extract informants from system
        informants = self.informants_manager._extract_informants_from_system(self.system)
        
        self.informants_table.setRowCount(len(informants))
        
        for row, (name, data) in enumerate(informants.items()):
            self.informants_table.setItem(row, 0, QTableWidgetItem(name))
            self.informants_table.setItem(row, 1, QTableWidgetItem(data.get('data_type', 'scalar')))
            self.informants_table.setItem(row, 2, QTableWidgetItem(', '.join(data.get('dimensions', []))))
            self.informants_table.setItem(row, 3, QTableWidgetItem(data.get('units', '')))
            self.informants_table.setItem(row, 4, QTableWidgetItem(data.get('description', '')))
    
    def on_dimension_selected(self):
        """Handle dimension selection."""
        current_item = self.dimensions_tree.currentItem()
        if current_item:
            dim_name = current_item.text(0)
            dim_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            
            # Create dimension definition from data
            if isinstance(dim_data, dict):
                dim_def = DimensionDefinition(
                    name=dim_name,
                    size=dim_data.get('size', 1),
                    labels=dim_data.get('labels', []),
                    description=dim_data.get('description', ''),
                    dimension_type=dim_data.get('type', 'categorical'),
                    units=dim_data.get('units')
                )
            else:
                dim_def = DimensionDefinition(dim_name, 1)
            
            self.dimension_editor.dimension_def = dim_def
            self.dimension_editor.load_dimension()
    
    def on_dimension_changed(self):
        """Handle dimension changes."""
        current_item = self.dimensions_tree.currentItem()
        if current_item:
            dim_def = self.dimension_editor.dimension_def
            
            # Update system dimensions
            self.system.dimensions[dim_def.name] = {
                'size': dim_def.size,
                'labels': dim_def.labels,
                'description': dim_def.description,
                'type': dim_def.dimension_type
            }
            
            if dim_def.units:
                self.system.dimensions[dim_def.name]['units'] = dim_def.units
            
            # Update tree item
            current_item.setText(0, dim_def.name)
            current_item.setData(0, Qt.ItemDataRole.UserRole, self.system.dimensions[dim_def.name])
            
            self.modified = True
    
    def add_dimension(self):
        """Add a new dimension."""
        dim_def = self.informants_manager.create_dimension_template("new_dimension", 2)
        
        # Add to system
        self.system.dimensions[dim_def.name] = {
            'size': dim_def.size,
            'labels': dim_def.labels,
            'description': dim_def.description,
            'type': dim_def.dimension_type
        }
        
        # Add to tree
        item = QTreeWidgetItem(self.dimensions_tree)
        item.setText(0, dim_def.name)
        item.setData(0, Qt.ItemDataRole.UserRole, self.system.dimensions[dim_def.name])
        
        # Select new item
        self.dimensions_tree.setCurrentItem(item)
        self.modified = True
    
    def remove_dimension(self):
        """Remove selected dimension."""
        current_item = self.dimensions_tree.currentItem()
        if current_item:
            dim_name = current_item.text(0)
            
            # Check if dimension is used by components
            used_by = []
            for component in self.system.get_all_components().values():
                spatial_dims = component.properties.get('spatial_dims', [])
                if dim_name in spatial_dims:
                    used_by.append(component.name)
            
            if used_by:
                QMessageBox.warning(
                    self, "Dimension In Use",
                    f"Dimension '{dim_name}' is used by components: {', '.join(used_by)}\n"
                    f"Remove references before deleting dimension."
                )
                return
            
            # Remove from system
            if dim_name in self.system.dimensions:
                del self.system.dimensions[dim_name]
            
            # Remove from tree
            index = self.dimensions_tree.indexOfTopLevelItem(current_item)
            self.dimensions_tree.takeTopLevelItem(index)
            
            self.modified = True
    
    def add_informant(self):
        """Add a new informant."""
        # This would open an informant creation dialog
        QMessageBox.information(self, "Add Informant", "Informant creation dialog would open here")
    
    def edit_informant_data(self):
        """Edit informant data."""
        current_row = self.informants_table.currentRow()
        if current_row >= 0:
            name_item = self.informants_table.item(current_row, 0)
            if name_item:
                informant_name = name_item.text()
                QMessageBox.information(self, "Edit Informant", 
                                      f"Data editor for '{informant_name}' would open here")
    
    def remove_informant(self):
        """Remove selected informant."""
        current_row = self.informants_table.currentRow()
        if current_row >= 0:
            self.informants_table.removeRow(current_row)
            self.modified = True
    
    def validate_system(self):
        """Validate the system and display results."""
        validation_results = self.informants_manager.validate_system_informants(self.system)
        
        if validation_results:
            text_lines = ["❌ Validation found issues:\n"]
            for component_name, errors in validation_results.items():
                text_lines.append(f"Component: {component_name}")
                for error in errors:
                    text_lines.append(f"  • {error}")
                text_lines.append("")
        else:
            text_lines = ["✅ All validation checks passed!"]
        
        self.validation_text.setPlainText("\n".join(text_lines))
    
    def update_preview(self):
        """Update the YAML preview."""
        try:
            import yaml
            from collections import OrderedDict
            
            # Create preview structure
            preview_data = OrderedDict()
            
            # Dimensions
            if self.system.dimensions:
                preview_data['dimensions'] = self.system.dimensions
            
            # Sample informants structure
            informants = self.informants_manager._extract_informants_from_system(self.system)
            if informants:
                preview_data['informants'] = informants
            
            yaml_text = yaml.dump(preview_data, default_flow_style=False, sort_keys=False)
            self.preview_text.setPlainText(yaml_text)
            
        except Exception as e:
            self.preview_text.setPlainText(f"Error generating preview: {e}")
    
    def save_and_accept(self):
        """Save changes and accept dialog."""
        if self.modified:
            # Save informants to file if needed
            # This would typically save to the system's informants directory
            pass
        
        self.accept()
