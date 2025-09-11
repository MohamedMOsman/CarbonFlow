"""
Dynamic Dimension Management for Spreadsheet Editor

This module provides enhanced dimension management capabilities including
drag-and-drop dimension assignment and dynamic dimension creation.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QListWidget,
    QListWidgetItem, QGroupBox, QFormLayout, QSpinBox, QMessageBox,
    QFrame, QScrollArea, QGridLayout, QToolButton, QSplitter,
    QInputDialog, QTreeWidget, QTreeWidgetItem, QMenu, QTableWidget,
    QTableWidgetItem, QHeaderView, QRadioButton, QButtonGroup,
    QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint, QRect
from PyQt6.QtGui import QDrag, QPainter, QPixmap, QFont, QColor, QPalette, QBrush
from PyQt6.QtWidgets import QApplication
from typing import Dict, List, Any, Optional
import re


class DimensionManagerDialog(QDialog):
    """Dialog for managing component dimensions."""

    def __init__(self, component, model=None, parent=None):
        super().__init__(parent)

        self.component = component
        self.model = model

        self.setWindowTitle(f"Manage Dimensions - {component.name}")
        self.setModal(True)
        self.resize(600, 500)

        self.setup_ui()
        self.load_dimensions()

    def setup_ui(self):
        """Set up the dimension manager UI."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(f"Dimensions for {self.component.name}")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Current dimensions list
        dimensions_group = QGroupBox("Current Dimensions")
        dimensions_layout = QVBoxLayout(dimensions_group)

        self.dimensions_list = QListWidget()
        self.dimensions_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        dimensions_layout.addWidget(self.dimensions_list)

        # Dimension buttons
        dim_buttons_layout = QHBoxLayout()

        self.add_dim_btn = QPushButton("Add Dimension")
        self.add_dim_btn.clicked.connect(self.add_dimension)
        dim_buttons_layout.addWidget(self.add_dim_btn)

        self.edit_dim_btn = QPushButton("Edit Selected")
        self.edit_dim_btn.clicked.connect(self.edit_dimension)
        dim_buttons_layout.addWidget(self.edit_dim_btn)

        self.remove_dim_btn = QPushButton("Remove Selected")
        self.remove_dim_btn.clicked.connect(self.remove_dimension)
        dim_buttons_layout.addWidget(self.remove_dim_btn)

        dim_buttons_layout.addStretch()
        dimensions_layout.addLayout(dim_buttons_layout)

        layout.addWidget(dimensions_group)

        # Available model dimensions
        if self.model and hasattr(self.model, 'dimensions'):
            available_group = QGroupBox("Available Model Dimensions")
            available_layout = QVBoxLayout(available_group)

            self.available_list = QListWidget()
            available_layout.addWidget(self.available_list)

            add_existing_btn = QPushButton("Add Selected to Component")
            add_existing_btn.clicked.connect(self.add_existing_dimension)
            available_layout.addWidget(add_existing_btn)

            layout.addWidget(available_group)

            # Load available dimensions
            self.load_available_dimensions()

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_dimensions(self):
        """Load current component dimensions."""
        self.dimensions_list.clear()

        spatial_dims = self.component.properties.get('spatial_dims', [])
        for dim_name in spatial_dims:
            item = QListWidgetItem(dim_name)

            # Add dimension info if available
            if self.model and hasattr(self.model, 'dimensions'):
                dim_info = self.model.dimensions.get(dim_name, {})
                size = dim_info.get('size', 'Unknown')
                item.setText(f"{dim_name} (size: {size})")

            self.dimensions_list.addItem(item)

    def load_available_dimensions(self):
        """Load available model dimensions not in component."""
        if not self.model or not hasattr(self.model, 'dimensions'):
            return

        self.available_list.clear()
        spatial_dims = self.component.properties.get('spatial_dims', [])

        for dim_name, dim_info in self.model.dimensions.items():
            if dim_name not in spatial_dims:
                size = dim_info.get('size', 'Unknown')
                description = dim_info.get('description', '')
                item_text = f"{dim_name} (size: {size})"
                if description:
                    item_text += f" - {description}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, dim_name)
                self.available_list.addItem(item)

    def add_dimension(self):
        """Add a new dimension."""
        dialog = AddDimensionDialog(
            existing_dimensions=getattr(self.model, 'dimensions', {}) if self.model else {},
            parent=self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            dim_name = dialog.get_dimension_name()
            dim_data = dialog.get_dimension_data()

            # Add to component
            spatial_dims = self.component.properties.get('spatial_dims', [])
            if dim_name not in spatial_dims:
                spatial_dims = spatial_dims.copy()
                spatial_dims.append(dim_name)
                self.component.properties['spatial_dims'] = spatial_dims

            # Add to model if available
            if self.model and hasattr(self.model, 'dimensions'):
                self.model.dimensions[dim_name] = dim_data

            # Refresh lists
            self.load_dimensions()
            self.load_available_dimensions()

    def edit_dimension(self):
        """Edit the selected dimension with detailed editor."""
        current_item = self.dimensions_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a dimension to edit.")
            return

        dim_name = current_item.text().split(' (')[0]  # Extract name before size info

        if self.model and hasattr(self.model, 'dimensions') and dim_name in self.model.dimensions:
            dim_data = self.model.dimensions[dim_name]

            # Use the enhanced dimension details editor
            dialog = DimensionDetailsEditor(dim_name, dim_data, parent=self)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_updated_dimension_data()
                self.model.dimensions[dim_name] = updated_data
                self.load_dimensions()
                self.load_available_dimensions()

                QMessageBox.information(
                    self,
                    "Dimension Updated",
                    f"Dimension '{dim_name}' has been updated successfully.\n"
                    f"New size: {updated_data.get('size', 0)} items"
                )
        else:
            QMessageBox.information(
                self,
                "Cannot Edit",
                f"Dimension '{dim_name}' is not defined in the model.\n"
                f"You can remove it and add a new one instead."
            )

    def remove_dimension(self):
        """Remove the selected dimension."""
        current_item = self.dimensions_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a dimension to remove.")
            return

        dim_name = current_item.text().split(' (')[0]  # Extract name before size info

        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove dimension '{dim_name}' from {self.component.name}?\n\n"
            f"This will not delete the dimension from the model,\n"
            f"only remove it from this component.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            spatial_dims = self.component.properties.get('spatial_dims', [])
            if dim_name in spatial_dims:
                spatial_dims = spatial_dims.copy()
                spatial_dims.remove(dim_name)
                self.component.properties['spatial_dims'] = spatial_dims

            self.load_dimensions()
            self.load_available_dimensions()

    def add_existing_dimension(self):
        """Add an existing model dimension to the component."""
        current_item = self.available_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a dimension to add.")
            return

        dim_name = current_item.data(Qt.ItemDataRole.UserRole)

        spatial_dims = self.component.properties.get('spatial_dims', [])
        if dim_name not in spatial_dims:
            spatial_dims = spatial_dims.copy()
            spatial_dims.append(dim_name)
            self.component.properties['spatial_dims'] = spatial_dims

        self.load_dimensions()
        self.load_available_dimensions()


class AddDimensionDialog(QDialog):
    """Dialog for adding new dimensions to the model."""
    
    def __init__(self, existing_dimensions=None, parent=None):
        super().__init__(parent)
        
        self.existing_dimensions = existing_dimensions or {}
        
        self.setWindowTitle("Add New Dimension")
        self.setModal(True)
        self.resize(500, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the add dimension dialog UI."""
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Create New Dimension")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Basic info group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        # Dimension name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., building_age, income_level")
        self.name_edit.textChanged.connect(self.validate_name)
        basic_layout.addRow("Dimension Name:", self.name_edit)
        
        # Name validation label
        self.name_validation_label = QLabel("")
        self.name_validation_label.setStyleSheet("color: red; font-size: 12px;")
        basic_layout.addRow("", self.name_validation_label)
        
        # Dimension type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["categorical", "temporal", "numerical", "ordinal"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        basic_layout.addRow("Type:", self.type_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Brief description of this dimension...")
        basic_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(basic_group)
        
        # Labels group
        labels_group = QGroupBox("Dimension Labels/Values")
        labels_layout = QVBoxLayout(labels_group)
        
        # Labels input method
        input_method_layout = QHBoxLayout()
        
        self.manual_radio = QPushButton("Manual Entry")
        self.manual_radio.setCheckable(True)
        self.manual_radio.setChecked(True)
        self.manual_radio.clicked.connect(self.set_manual_mode)
        input_method_layout.addWidget(self.manual_radio)
        
        self.range_radio = QPushButton("Generate Range")
        self.range_radio.setCheckable(True)
        self.range_radio.clicked.connect(self.set_range_mode)
        input_method_layout.addWidget(self.range_radio)
        
        input_method_layout.addStretch()
        labels_layout.addLayout(input_method_layout)
        
        # Manual entry area
        self.manual_widget = QWidget()
        manual_layout = QVBoxLayout(self.manual_widget)
        
        manual_layout.addWidget(QLabel("Enter labels (one per line):"))
        self.labels_edit = QTextEdit()
        self.labels_edit.setMaximumHeight(150)
        self.labels_edit.setPlaceholderText("0-10 years\n10-20 years\n20-30 years\n30+ years")
        manual_layout.addWidget(self.labels_edit)
        
        labels_layout.addWidget(self.manual_widget)
        
        # Range generation area
        self.range_widget = QWidget()
        range_layout = QFormLayout(self.range_widget)
        
        self.start_spin = QSpinBox()
        self.start_spin.setRange(-9999, 9999)
        self.start_spin.setValue(2020)
        range_layout.addRow("Start Value:", self.start_spin)
        
        self.end_spin = QSpinBox()
        self.end_spin.setRange(-9999, 9999)
        self.end_spin.setValue(2030)
        range_layout.addRow("End Value:", self.end_spin)
        
        self.step_spin = QSpinBox()
        self.step_spin.setRange(1, 100)
        self.step_spin.setValue(1)
        range_layout.addRow("Step Size:", self.step_spin)
        
        generate_btn = QPushButton("Generate Labels")
        generate_btn.clicked.connect(self.generate_range_labels)
        range_layout.addRow("", generate_btn)
        
        labels_layout.addWidget(self.range_widget)
        self.range_widget.hide()
        
        # Preview area
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        
        self.preview_label = QLabel("No labels defined")
        self.preview_label.setStyleSheet("color: #666; font-style: italic;")
        preview_layout.addWidget(self.preview_label)
        
        labels_layout.addLayout(preview_layout)
        
        layout.addWidget(labels_group)
        
        # Connect text changes for preview
        self.labels_edit.textChanged.connect(self.update_preview)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initial setup
        self.set_manual_mode()
        self.update_preview()
        
    def validate_name(self):
        """Validate the dimension name."""
        name = self.name_edit.text().strip()
        
        if not name:
            self.name_validation_label.setText("")
            return False
            
        # Check naming convention (alphanumeric + underscore, no spaces)
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            self.name_validation_label.setText("Name must start with letter, contain only letters, numbers, and underscores")
            return False
            
        # Check if name already exists
        if name in self.existing_dimensions:
            self.name_validation_label.setText("Dimension name already exists")
            return False
            
        # Check reserved names
        reserved_names = ['index', 'time', 'id', 'name', 'value', 'data']
        if name.lower() in reserved_names:
            self.name_validation_label.setText("Name is reserved, please choose another")
            return False
            
        self.name_validation_label.setText("✓ Valid name")
        self.name_validation_label.setStyleSheet("color: green; font-size: 12px;")
        return True
        
    def on_type_changed(self):
        """Handle dimension type changes."""
        dim_type = self.type_combo.currentText()
        
        # Update placeholder text based on type
        if dim_type == "temporal":
            self.labels_edit.setPlaceholderText("2020\n2021\n2022\n2023")
            self.description_edit.setPlaceholderText("Time periods for the analysis...")
        elif dim_type == "categorical":
            self.labels_edit.setPlaceholderText("Category A\nCategory B\nCategory C")
            self.description_edit.setPlaceholderText("Categorical groupings...")
        elif dim_type == "numerical":
            self.labels_edit.setPlaceholderText("0-10\n10-20\n20-30\n30+")
            self.description_edit.setPlaceholderText("Numerical ranges...")
        elif dim_type == "ordinal":
            self.labels_edit.setPlaceholderText("Low\nMedium\nHigh")
            self.description_edit.setPlaceholderText("Ordered categories...")
            
    def set_manual_mode(self):
        """Set manual entry mode."""
        self.manual_radio.setChecked(True)
        self.range_radio.setChecked(False)
        self.manual_widget.show()
        self.range_widget.hide()
        
    def set_range_mode(self):
        """Set range generation mode."""
        self.manual_radio.setChecked(False)
        self.range_radio.setChecked(True)
        self.manual_widget.hide()
        self.range_widget.show()
        
    def generate_range_labels(self):
        """Generate labels from range parameters."""
        start = self.start_spin.value()
        end = self.end_spin.value()
        step = self.step_spin.value()
        
        if start >= end:
            QMessageBox.warning(self, "Invalid Range", "Start value must be less than end value")
            return
            
        labels = []
        current = start
        while current <= end:
            labels.append(str(current))
            current += step
            
        self.labels_edit.setText('\n'.join(labels))
        self.update_preview()
        
    def update_preview(self):
        """Update the labels preview."""
        labels = self.get_labels()
        
        if not labels:
            self.preview_label.setText("No labels defined")
            self.preview_label.setStyleSheet("color: #666; font-style: italic;")
        else:
            preview_text = f"{len(labels)} labels: {', '.join(labels[:5])}"
            if len(labels) > 5:
                preview_text += f", ... (+{len(labels)-5} more)"
            self.preview_label.setText(preview_text)
            self.preview_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
            
    def get_labels(self):
        """Get the current labels list."""
        text = self.labels_edit.toPlainText().strip()
        if not text:
            return []
            
        labels = [line.strip() for line in text.split('\n') if line.strip()]
        return labels
        
    def get_dimension_data(self):
        """Get the dimension data from the dialog."""
        if not self.validate_name():
            return None
            
        labels = self.get_labels()
        if not labels:
            QMessageBox.warning(self, "No Labels", "Please define at least one label for the dimension")
            return None
            
        return {
            'name': self.name_edit.text().strip(),
            'type': self.type_combo.currentText(),
            'description': self.description_edit.toPlainText().strip(),
            'labels': labels,
            'size': len(labels),
            'metadata': {
                'user_created': True,
                'creation_method': 'manual' if self.manual_radio.isChecked() else 'range'
            }
        }

    def load_dimension_data(self, name: str, data: Dict[str, Any]):
        """Load existing dimension data into the dialog for editing."""
        self.name_edit.setText(name)
        self.name_edit.setReadOnly(True)  # Don't allow changing name when editing

        # Set type
        dim_type = data.get('type', 'categorical')
        index = self.type_combo.findText(dim_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        # Set description
        description = data.get('description', '')
        self.description_edit.setPlainText(description)

        # Set labels
        labels = data.get('labels', [])
        if labels:
            self.manual_radio.setChecked(True)
            self.labels_edit.setPlainText('\n'.join(labels))
        else:
            # Try to generate from size
            size = data.get('size', 2)
            self.range_radio.setChecked(True)
            self.range_start_spin.setValue(1)
            self.range_end_spin.setValue(size)

        self.on_method_changed()  # Update UI based on selection

    def get_dimension_name(self) -> str:
        """Get the dimension name."""
        return self.name_edit.text().strip()


class DimensionDetailsEditor(QDialog):
    """Enhanced editor for detailed dimension management including labels, years, ages, etc."""

    def __init__(self, dimension_name: str, dimension_data: Dict[str, Any], parent=None):
        super().__init__(parent)

        self.dimension_name = dimension_name
        self.dimension_data = dimension_data.copy()
        self.original_data = dimension_data.copy()

        self.setWindowTitle(f"Edit Dimension Details - {dimension_name}")
        self.setModal(True)
        self.resize(700, 600)

        self.setup_ui()
        self.load_dimension_data()

    def setup_ui(self):
        """Set up the detailed dimension editor UI."""
        layout = QVBoxLayout(self)

        # Title and info
        title_label = QLabel(f"Editing: {self.dimension_name}")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Tab widget for different editing modes
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Labels editor tab
        self.setup_labels_tab()

        # Properties tab
        self.setup_properties_tab()

        # Quick actions tab
        self.setup_quick_actions_tab()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Reset
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self.reset_to_original)
        layout.addWidget(button_box)

    def setup_labels_tab(self):
        """Set up the labels editing tab."""
        labels_widget = QWidget()
        layout = QVBoxLayout(labels_widget)

        # Instructions
        instructions = QLabel(
            "Edit dimension labels below. You can add, remove, or reorder items.\n"
            "Each label represents one category or value in this dimension."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Labels table
        self.labels_table = QTableWidget()
        self.labels_table.setColumnCount(2)
        self.labels_table.setHorizontalHeaderLabels(["Index", "Label"])
        self.labels_table.horizontalHeader().setStretchLastSection(True)
        self.labels_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.labels_table)

        # Buttons for label management
        buttons_layout = QHBoxLayout()

        add_label_btn = QPushButton("➕ Add Label")
        add_label_btn.clicked.connect(self.add_label)
        buttons_layout.addWidget(add_label_btn)

        insert_label_btn = QPushButton("📝 Insert Above")
        insert_label_btn.clicked.connect(self.insert_label)
        buttons_layout.addWidget(insert_label_btn)

        remove_label_btn = QPushButton("❌ Remove Selected")
        remove_label_btn.clicked.connect(self.remove_label)
        buttons_layout.addWidget(remove_label_btn)

        buttons_layout.addStretch()

        move_up_btn = QPushButton("⬆️ Move Up")
        move_up_btn.clicked.connect(self.move_label_up)
        buttons_layout.addWidget(move_up_btn)

        move_down_btn = QPushButton("⬇️ Move Down")
        move_down_btn.clicked.connect(self.move_label_down)
        buttons_layout.addWidget(move_down_btn)

        layout.addLayout(buttons_layout)

        self.tabs.addTab(labels_widget, "📝 Labels")

    def setup_properties_tab(self):
        """Set up the properties editing tab."""
        props_widget = QWidget()
        layout = QFormLayout(props_widget)

        # Dimension type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["categorical", "temporal", "spatial", "ordinal", "numerical"])
        layout.addRow("Type:", self.type_combo)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        layout.addRow("Description:", self.description_edit)

        # Units (if applicable)
        self.units_edit = QLineEdit()
        layout.addRow("Units:", self.units_edit)

        # Additional metadata
        metadata_group = QGroupBox("Additional Properties")
        metadata_layout = QFormLayout(metadata_group)

        self.min_value_edit = QLineEdit()
        metadata_layout.addRow("Minimum Value:", self.min_value_edit)

        self.max_value_edit = QLineEdit()
        metadata_layout.addRow("Maximum Value:", self.max_value_edit)

        self.default_value_edit = QLineEdit()
        metadata_layout.addRow("Default Value:", self.default_value_edit)

        layout.addRow(metadata_group)

        self.tabs.addTab(props_widget, "⚙️ Properties")

    def setup_quick_actions_tab(self):
        """Set up the quick actions tab for common operations."""
        actions_widget = QWidget()
        layout = QVBoxLayout(actions_widget)

        # Time series actions
        time_group = QGroupBox("📅 Time Series Actions")
        time_layout = QVBoxLayout(time_group)

        # Add years
        years_layout = QHBoxLayout()
        years_layout.addWidget(QLabel("Add Years:"))

        self.start_year_spin = QSpinBox()
        self.start_year_spin.setRange(1900, 2100)
        self.start_year_spin.setValue(2020)
        years_layout.addWidget(self.start_year_spin)

        years_layout.addWidget(QLabel("to"))

        self.end_year_spin = QSpinBox()
        self.end_year_spin.setRange(1900, 2100)
        self.end_year_spin.setValue(2030)
        years_layout.addWidget(self.end_year_spin)

        add_years_btn = QPushButton("Add Years")
        add_years_btn.clicked.connect(self.add_year_range)
        years_layout.addWidget(add_years_btn)

        years_layout.addStretch()
        time_layout.addLayout(years_layout)

        # Add months
        months_btn = QPushButton("Add All Months (Jan-Dec)")
        months_btn.clicked.connect(self.add_months)
        time_layout.addWidget(months_btn)

        layout.addWidget(time_group)

        # Age groups actions
        age_group = QGroupBox("👥 Age Groups Actions")
        age_layout = QVBoxLayout(age_group)

        # Standard age groups
        standard_ages_layout = QHBoxLayout()

        child_ages_btn = QPushButton("Add Child Ages (0-17)")
        child_ages_btn.clicked.connect(lambda: self.add_age_groups("child"))
        standard_ages_layout.addWidget(child_ages_btn)

        adult_ages_btn = QPushButton("Add Adult Ages (18-64)")
        adult_ages_btn.clicked.connect(lambda: self.add_age_groups("adult"))
        standard_ages_layout.addWidget(adult_ages_btn)

        senior_ages_btn = QPushButton("Add Senior Ages (65+)")
        senior_ages_btn.clicked.connect(lambda: self.add_age_groups("senior"))
        standard_ages_layout.addWidget(senior_ages_btn)

        age_layout.addLayout(standard_ages_layout)

        # Custom age range
        custom_age_layout = QHBoxLayout()
        custom_age_layout.addWidget(QLabel("Custom Age Range:"))

        self.age_start_spin = QSpinBox()
        self.age_start_spin.setRange(0, 120)
        self.age_start_spin.setValue(0)
        custom_age_layout.addWidget(self.age_start_spin)

        custom_age_layout.addWidget(QLabel("to"))

        self.age_end_spin = QSpinBox()
        self.age_end_spin.setRange(0, 120)
        self.age_end_spin.setValue(100)
        custom_age_layout.addWidget(self.age_end_spin)

        self.age_step_spin = QSpinBox()
        self.age_step_spin.setRange(1, 20)
        self.age_step_spin.setValue(5)
        custom_age_layout.addWidget(QLabel("Step:"))
        custom_age_layout.addWidget(self.age_step_spin)

        add_custom_ages_btn = QPushButton("Add Age Range")
        add_custom_ages_btn.clicked.connect(self.add_custom_age_range)
        custom_age_layout.addWidget(add_custom_ages_btn)

        age_layout.addLayout(custom_age_layout)

        layout.addWidget(age_group)

        # Categories actions
        categories_group = QGroupBox("📊 Categories Actions")
        categories_layout = QVBoxLayout(categories_group)

        # Common categories
        common_cats_layout = QHBoxLayout()

        income_btn = QPushButton("Add Income Levels")
        income_btn.clicked.connect(lambda: self.add_common_categories("income"))
        common_cats_layout.addWidget(income_btn)

        education_btn = QPushButton("Add Education Levels")
        education_btn.clicked.connect(lambda: self.add_common_categories("education"))
        common_cats_layout.addWidget(education_btn)

        regions_btn = QPushButton("Add Geographic Regions")
        regions_btn.clicked.connect(lambda: self.add_common_categories("regions"))
        common_cats_layout.addWidget(regions_btn)

        categories_layout.addLayout(common_cats_layout)

        layout.addWidget(categories_group)

        layout.addStretch()

        self.tabs.addTab(actions_widget, "⚡ Quick Actions")

    def load_dimension_data(self):
        """Load dimension data into the editor."""
        # Load properties
        self.type_combo.setCurrentText(self.dimension_data.get('type', 'categorical'))
        self.description_edit.setPlainText(self.dimension_data.get('description', ''))
        self.units_edit.setText(self.dimension_data.get('units', ''))

        # Load metadata
        metadata = self.dimension_data.get('metadata', {})
        self.min_value_edit.setText(str(metadata.get('min_value', '')))
        self.max_value_edit.setText(str(metadata.get('max_value', '')))
        self.default_value_edit.setText(str(metadata.get('default_value', '')))

        # Load labels
        self.load_labels_table()

    def load_labels_table(self):
        """Load labels into the table."""
        labels = self.dimension_data.get('labels', [])
        self.labels_table.setRowCount(len(labels))

        for i, label in enumerate(labels):
            # Index column (read-only)
            index_item = QTableWidgetItem(str(i))
            index_item.setFlags(index_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.labels_table.setItem(i, 0, index_item)

            # Label column (editable)
            label_item = QTableWidgetItem(str(label))
            self.labels_table.setItem(i, 1, label_item)

    def add_label(self):
        """Add a new label to the dimension."""
        text, ok = QInputDialog.getText(self, "Add Label", "Enter new label:")
        if ok and text.strip():
            row = self.labels_table.rowCount()
            self.labels_table.insertRow(row)

            # Index column
            index_item = QTableWidgetItem(str(row))
            index_item.setFlags(index_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.labels_table.setItem(row, 0, index_item)

            # Label column
            label_item = QTableWidgetItem(text.strip())
            self.labels_table.setItem(row, 1, label_item)

            self.update_indices()

    def insert_label(self):
        """Insert a new label above the selected row."""
        current_row = self.labels_table.currentRow()
        if current_row < 0:
            current_row = 0

        text, ok = QInputDialog.getText(self, "Insert Label", "Enter new label:")
        if ok and text.strip():
            self.labels_table.insertRow(current_row)

            # Index column
            index_item = QTableWidgetItem(str(current_row))
            index_item.setFlags(index_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.labels_table.setItem(current_row, 0, index_item)

            # Label column
            label_item = QTableWidgetItem(text.strip())
            self.labels_table.setItem(current_row, 1, label_item)

            self.update_indices()

    def remove_label(self):
        """Remove the selected label."""
        current_row = self.labels_table.currentRow()
        if current_row >= 0:
            label_item = self.labels_table.item(current_row, 1)
            label_text = label_item.text() if label_item else "Unknown"

            reply = QMessageBox.question(
                self, "Remove Label",
                f"Remove label '{label_text}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.labels_table.removeRow(current_row)
                self.update_indices()

    def move_label_up(self):
        """Move the selected label up."""
        current_row = self.labels_table.currentRow()
        if current_row > 0:
            self.swap_rows(current_row, current_row - 1)
            self.labels_table.setCurrentCell(current_row - 1, 1)
            self.update_indices()

    def move_label_down(self):
        """Move the selected label down."""
        current_row = self.labels_table.currentRow()
        if current_row >= 0 and current_row < self.labels_table.rowCount() - 1:
            self.swap_rows(current_row, current_row + 1)
            self.labels_table.setCurrentCell(current_row + 1, 1)
            self.update_indices()

    def swap_rows(self, row1: int, row2: int):
        """Swap two rows in the labels table."""
        # Get items from both rows
        item1 = self.labels_table.item(row1, 1)
        item2 = self.labels_table.item(row2, 1)

        if item1 and item2:
            text1 = item1.text()
            text2 = item2.text()

            # Swap the text
            item1.setText(text2)
            item2.setText(text1)

    def update_indices(self):
        """Update the index column after changes."""
        for i in range(self.labels_table.rowCount()):
            index_item = self.labels_table.item(i, 0)
            if index_item:
                index_item.setText(str(i))

    def add_year_range(self):
        """Add a range of years to the labels."""
        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()

        if start_year > end_year:
            QMessageBox.warning(self, "Invalid Range", "Start year must be less than or equal to end year.")
            return

        years_to_add = []
        for year in range(start_year, end_year + 1):
            years_to_add.append(str(year))

        self.add_multiple_labels(years_to_add)
        QMessageBox.information(self, "Years Added", f"Added {len(years_to_add)} years ({start_year}-{end_year})")

    def add_months(self):
        """Add all months to the labels."""
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.add_multiple_labels(months)
        QMessageBox.information(self, "Months Added", "Added all 12 months")

    def add_age_groups(self, group_type: str):
        """Add standard age groups."""
        if group_type == "child":
            ages = ["0-4", "5-9", "10-14", "15-17"]
            message = "Added child age groups (0-17)"
        elif group_type == "adult":
            ages = ["18-24", "25-34", "35-44", "45-54", "55-64"]
            message = "Added adult age groups (18-64)"
        elif group_type == "senior":
            ages = ["65-74", "75-84", "85+"]
            message = "Added senior age groups (65+)"
        else:
            return

        self.add_multiple_labels(ages)
        QMessageBox.information(self, "Age Groups Added", message)

    def add_custom_age_range(self):
        """Add custom age range."""
        start_age = self.age_start_spin.value()
        end_age = self.age_end_spin.value()
        step = self.age_step_spin.value()

        if start_age > end_age:
            QMessageBox.warning(self, "Invalid Range", "Start age must be less than or equal to end age.")
            return

        ages = []
        current = start_age
        while current < end_age:
            next_age = min(current + step - 1, end_age)
            if current == next_age:
                ages.append(str(current))
            else:
                ages.append(f"{current}-{next_age}")
            current += step

        self.add_multiple_labels(ages)
        QMessageBox.information(self, "Age Range Added", f"Added {len(ages)} age groups")

    def add_common_categories(self, category_type: str):
        """Add common category sets."""
        if category_type == "income":
            categories = ["Low Income", "Lower Middle Income", "Upper Middle Income", "High Income"]
            message = "Added income level categories"
        elif category_type == "education":
            categories = ["No Formal Education", "Primary Education", "Secondary Education", "Higher Education"]
            message = "Added education level categories"
        elif category_type == "regions":
            categories = ["Urban", "Suburban", "Rural", "Remote"]
            message = "Added geographic region categories"
        else:
            return

        self.add_multiple_labels(categories)
        QMessageBox.information(self, "Categories Added", message)

    def add_multiple_labels(self, labels: List[str]):
        """Add multiple labels at once."""
        start_row = self.labels_table.rowCount()

        for i, label in enumerate(labels):
            row = start_row + i
            self.labels_table.insertRow(row)

            # Index column
            index_item = QTableWidgetItem(str(row))
            index_item.setFlags(index_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.labels_table.setItem(row, 0, index_item)

            # Label column
            label_item = QTableWidgetItem(label)
            self.labels_table.setItem(row, 1, label_item)

        self.update_indices()

    def reset_to_original(self):
        """Reset dimension data to original values."""
        reply = QMessageBox.question(
            self, "Reset Changes",
            "Reset all changes to original values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.dimension_data = self.original_data.copy()
            self.load_dimension_data()

    def get_updated_dimension_data(self) -> Dict[str, Any]:
        """Get the updated dimension data."""
        # Collect labels from table
        labels = []
        for i in range(self.labels_table.rowCount()):
            label_item = self.labels_table.item(i, 1)
            if label_item and label_item.text().strip():
                labels.append(label_item.text().strip())

        # Update dimension data
        updated_data = {
            'labels': labels,
            'size': len(labels),
            'type': self.type_combo.currentText(),
            'description': self.description_edit.toPlainText().strip(),
            'units': self.units_edit.text().strip()
        }

        # Add metadata if provided
        metadata = {}
        if self.min_value_edit.text().strip():
            try:
                metadata['min_value'] = float(self.min_value_edit.text())
            except ValueError:
                metadata['min_value'] = self.min_value_edit.text()

        if self.max_value_edit.text().strip():
            try:
                metadata['max_value'] = float(self.max_value_edit.text())
            except ValueError:
                metadata['max_value'] = self.max_value_edit.text()

        if self.default_value_edit.text().strip():
            try:
                metadata['default_value'] = float(self.default_value_edit.text())
            except ValueError:
                metadata['default_value'] = self.default_value_edit.text()

        if metadata:
            updated_data['metadata'] = metadata

        return updated_data


class DraggableDimensionItem(QLabel):
    """A draggable dimension item for the dimensions panel."""
    
    def __init__(self, dimension_name, dimension_info, parent=None):
        super().__init__(parent)
        
        self.dimension_name = dimension_name
        self.dimension_info = dimension_info
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the draggable item UI."""
        
        # Create display text
        size = self.dimension_info.get('size', 0)
        dim_type = self.dimension_info.get('type', 'unknown')
        
        display_text = f"{self.dimension_name}\n({dim_type}, {size} values)"
        
        self.setText(display_text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Styling
        self.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                border: 2px solid #2980b9;
                border-radius: 8px;
                padding: 8px;
                margin: 2px;
                font-weight: bold;
                min-height: 40px;
            }
            QLabel:hover {
                background-color: #2980b9;
                border-color: #1f5f8b;
            }
        """)
        
        # Enable dragging
        self.setAcceptDrops(False)
        
        # Set tooltip
        description = self.dimension_info.get('description', 'No description')
        labels = self.dimension_info.get('labels', [])
        tooltip = f"<b>{self.dimension_name}</b><br/>"
        tooltip += f"Type: {dim_type}<br/>"
        tooltip += f"Size: {size} values<br/>"
        tooltip += f"Description: {description}<br/>"
        if labels:
            tooltip += f"Labels: {', '.join(labels[:5])}"
            if len(labels) > 5:
                tooltip += f" (+{len(labels)-5} more)"
        
        self.setToolTip(tooltip)
        
    def mousePressEvent(self, event):
        """Handle mouse press for drag initiation."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for drag operation."""
        try:
            if not (event.buttons() & Qt.MouseButton.LeftButton):
                return

            if not hasattr(self, 'drag_start_position'):
                return

            if ((event.pos() - self.drag_start_position).manhattanLength() <
                QApplication.startDragDistance()):
                return

            # Validate dimension name before starting drag
            if not self.dimension_name or not isinstance(self.dimension_name, str):
                print(f"Warning: Invalid dimension name for drag: {self.dimension_name}")
                return

            # Start drag operation
            drag = QDrag(self)
            mime_data = QMimeData()

            # Set drag data with validation
            try:
                mime_data.setText(self.dimension_name)
                mime_data.setData("application/x-dimension", self.dimension_name.encode('utf-8'))
            except Exception as e:
                print(f"Error setting drag data: {str(e)}")
                return

            drag.setMimeData(mime_data)

            # Create drag pixmap with error handling
            try:
                pixmap = QPixmap(self.size())
                if pixmap.isNull():
                    print("Warning: Failed to create drag pixmap")
                    # Execute drag without pixmap
                    drop_action = drag.exec(Qt.DropAction.MoveAction)
                    return

                pixmap.fill(Qt.GlobalColor.transparent)

                painter = QPainter(pixmap)
                if painter.isActive():
                    painter.setOpacity(0.8)
                    self.render(painter)
                    painter.end()

                    drag.setPixmap(pixmap)
                    drag.setHotSpot(self.drag_start_position)
                else:
                    print("Warning: QPainter failed to activate")

            except Exception as e:
                print(f"Error creating drag pixmap: {str(e)}")
                # Continue without pixmap

            # Execute drag
            try:
                drop_action = drag.exec(Qt.DropAction.MoveAction)
            except Exception as e:
                print(f"Error executing drag operation: {str(e)}")

        except Exception as e:
            print(f"Error in mouseMoveEvent: {str(e)}")
            import traceback
            traceback.print_exc()


class DropZone(QFrame):
    """A drop zone for dimension assignment."""
    
    dimension_dropped = pyqtSignal(str, str)  # zone_name, dimension_name
    
    def __init__(self, zone_name, zone_label, parent=None):
        super().__init__(parent)
        
        self.zone_name = zone_name
        self.zone_label = zone_label
        self.current_dimension = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the drop zone UI."""
        
        self.setAcceptDrops(True)
        self.setMinimumHeight(80)
        self.setMinimumWidth(200)
        
        layout = QVBoxLayout(self)
        
        # Zone label
        label = QLabel(self.zone_label)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(label)
        
        # Current dimension display
        self.dimension_display = QLabel("Drop dimension here")
        self.dimension_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dimension_display.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.dimension_display)
        
        # Default styling
        self.update_styling()
        
    def update_styling(self, drag_active=False):
        """Update the drop zone styling."""
        
        if drag_active:
            # Highlight during drag
            style = """
                QFrame {
                    border: 3px dashed #27ae60;
                    border-radius: 10px;
                    background-color: #d5f4e6;
                }
            """
        elif self.current_dimension:
            # Has dimension assigned
            style = """
                QFrame {
                    border: 2px solid #3498db;
                    border-radius: 10px;
                    background-color: #ebf3fd;
                }
            """
        else:
            # Empty drop zone
            style = """
                QFrame {
                    border: 2px dashed #bdc3c7;
                    border-radius: 10px;
                    background-color: #f8f9fa;
                }
            """
            
        self.setStyleSheet(style)
        
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        try:
            if event.mimeData().hasFormat("application/x-dimension"):
                event.acceptProposedAction()
                self.update_styling(drag_active=True)
        except Exception as e:
            print(f"Error in dragEnterEvent: {str(e)}")

    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        try:
            self.update_styling(drag_active=False)
        except Exception as e:
            print(f"Error in dragLeaveEvent: {str(e)}")

    def dropEvent(self, event):
        """Handle drop event."""
        try:
            if event.mimeData().hasFormat("application/x-dimension"):
                # Safely extract dimension name
                try:
                    dimension_data = event.mimeData().data("application/x-dimension")
                    if dimension_data.isNull():
                        print("Warning: Empty dimension data in drop event")
                        return

                    dimension_name = dimension_data.data().decode('utf-8')

                    if not dimension_name or not isinstance(dimension_name, str):
                        print(f"Warning: Invalid dimension name in drop: {dimension_name}")
                        return

                except Exception as e:
                    print(f"Error extracting dimension name from drop: {str(e)}")
                    return

                # Set dimension and emit signal
                try:
                    self.set_dimension(dimension_name)
                    self.dimension_dropped.emit(self.zone_name, dimension_name)
                    event.acceptProposedAction()
                except Exception as e:
                    print(f"Error processing drop for dimension {dimension_name}: {str(e)}")

        except Exception as e:
            print(f"Error in dropEvent: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Always reset styling
            try:
                self.update_styling(drag_active=False)
            except Exception as e:
                print(f"Error resetting styling after drop: {str(e)}")
        
    def set_dimension(self, dimension_name):
        """Set the current dimension for this drop zone."""
        try:
            self.current_dimension = dimension_name

            if dimension_name:
                # Ensure dimension_name is a string
                display_name = str(dimension_name) if dimension_name is not None else ""
                self.dimension_display.setText(display_name)
                self.dimension_display.setStyleSheet("color: #2c3e50; font-weight: bold;")
            else:
                self.dimension_display.setText("Drop dimension here")
                self.dimension_display.setStyleSheet("color: #7f8c8d; font-style: italic;")

            self.update_styling()

            # Force a repaint to ensure the display is updated
            self.dimension_display.repaint()

        except Exception as e:
            print(f"Error setting dimension in drop zone {self.zone_name}: {str(e)}")
            # Set a safe fallback
            self.current_dimension = None
            self.dimension_display.setText("Error")
            self.dimension_display.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
    def clear_dimension(self):
        """Clear the current dimension."""
        self.set_dimension(None)
