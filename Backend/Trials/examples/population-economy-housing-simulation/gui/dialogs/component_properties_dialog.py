"""
Component Properties Dialog

This module provides a comprehensive dialog for editing component properties
including dimensions, data, and other settings directly from the component.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QMessageBox,
    QDialogButtonBox, QTabWidget, QWidget, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from typing import Dict, List, Any, Optional

from yaml_integration.yaml_loader import ModelComponent, GuiModel


class ComponentPropertiesDialog(QDialog):
    """
    Comprehensive dialog for editing component properties including dimensions.
    
    This dialog provides:
    - Basic component properties (name, description, units, etc.)
    - Dimension management (add, edit, remove dimensions)
    - Data editing capabilities
    - Integration with dimension editors
    """
    
    # Signals
    component_modified = pyqtSignal(object)  # Emitted when component is modified
    
    def __init__(self, component: ModelComponent, model: GuiModel = None, parent=None):
        super().__init__(parent)
        
        self.component = component
        self.model = model
        self.original_properties = component.properties.copy()
        
        self.setWindowTitle(f"Properties - {component.name}")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_component_data()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(f"Editing: {self.component.name} ({self.component.component_type.title()})")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Main content area
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Properties tab
        self.setup_properties_tab()
        
        # Dimensions tab
        self.setup_dimensions_tab()
        
        # Data tab
        self.setup_data_tab()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_changes)
        layout.addWidget(button_box)
    
    def setup_properties_tab(self):
        """Set up the basic properties tab."""
        props_widget = QWidget()
        layout = QFormLayout(props_widget)
        
        # Component name
        self.name_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        layout.addRow("Description:", self.description_edit)
        
        # Component-specific properties
        if self.component.component_type == 'stock':
            self.setup_stock_properties(layout)
        elif self.component.component_type == 'flow':
            self.setup_flow_properties(layout)
        elif self.component.component_type == 'calculator':
            self.setup_calculator_properties(layout)
        
        self.tabs.addTab(props_widget, "📝 Properties")
    
    def setup_stock_properties(self, layout: QFormLayout):
        """Set up stock-specific properties."""
        # Initial value
        self.initial_value_edit = QDoubleSpinBox()
        self.initial_value_edit.setRange(-999999999, 999999999)
        self.initial_value_edit.setDecimals(2)
        layout.addRow("Initial Value:", self.initial_value_edit)
        
        # Units
        self.units_edit = QLineEdit()
        layout.addRow("Units:", self.units_edit)
        
        # Min/Max values
        self.min_value_edit = QDoubleSpinBox()
        self.min_value_edit.setRange(-999999999, 999999999)
        self.min_value_edit.setSpecialValueText("No minimum")
        self.min_value_edit.setValue(self.min_value_edit.minimum())
        layout.addRow("Minimum Value:", self.min_value_edit)
        
        self.max_value_edit = QDoubleSpinBox()
        self.max_value_edit.setRange(-999999999, 999999999)
        self.max_value_edit.setSpecialValueText("No maximum")
        self.max_value_edit.setValue(self.max_value_edit.maximum())
        layout.addRow("Maximum Value:", self.max_value_edit)
    
    def setup_flow_properties(self, layout: QFormLayout):
        """Set up flow-specific properties."""
        # Rate
        self.rate_edit = QDoubleSpinBox()
        self.rate_edit.setRange(-999999999, 999999999)
        self.rate_edit.setDecimals(4)
        layout.addRow("Rate:", self.rate_edit)
        
        # Units
        self.units_edit = QLineEdit()
        layout.addRow("Units:", self.units_edit)
    
    def setup_calculator_properties(self, layout: QFormLayout):
        """Set up calculator-specific properties."""
        # Expression
        self.expression_edit = QTextEdit()
        self.expression_edit.setMaximumHeight(60)
        layout.addRow("Expression:", self.expression_edit)
        
        # Units
        self.units_edit = QLineEdit()
        layout.addRow("Units:", self.units_edit)
    
    def setup_dimensions_tab(self):
        """Set up the dimensions management tab."""
        dims_widget = QWidget()
        layout = QVBoxLayout(dims_widget)
        
        # Instructions
        instructions = QLabel(
            "Manage the dimensions for this component. Dimensions define the multidimensional "
            "structure of your data (e.g., age groups, regions, time periods)."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Current dimensions list
        current_dims_group = QGroupBox("Current Dimensions")
        current_dims_layout = QVBoxLayout(current_dims_group)
        
        self.dimensions_list = QListWidget()
        self.dimensions_list.setMaximumHeight(150)
        current_dims_layout.addWidget(self.dimensions_list)
        
        # Dimension management buttons
        dims_buttons_layout = QHBoxLayout()
        
        self.add_dimension_btn = QPushButton("➕ Add Dimension")
        self.add_dimension_btn.clicked.connect(self.add_dimension)
        dims_buttons_layout.addWidget(self.add_dimension_btn)
        
        self.edit_dimension_btn = QPushButton("✏️ Edit Dimension")
        self.edit_dimension_btn.clicked.connect(self.edit_dimension)
        dims_buttons_layout.addWidget(self.edit_dimension_btn)
        
        self.remove_dimension_btn = QPushButton("❌ Remove Dimension")
        self.remove_dimension_btn.clicked.connect(self.remove_dimension)
        dims_buttons_layout.addWidget(self.remove_dimension_btn)
        
        dims_buttons_layout.addStretch()
        current_dims_layout.addLayout(dims_buttons_layout)
        
        layout.addWidget(current_dims_group)
        
        # Available model dimensions
        if self.model and hasattr(self.model, 'dimensions') and self.model.dimensions:
            available_dims_group = QGroupBox("Available Model Dimensions")
            available_dims_layout = QVBoxLayout(available_dims_group)
            
            self.available_dimensions_list = QListWidget()
            self.available_dimensions_list.setMaximumHeight(120)
            available_dims_layout.addWidget(self.available_dimensions_list)
            
            add_existing_btn = QPushButton("⬇️ Add Selected to Component")
            add_existing_btn.clicked.connect(self.add_existing_dimension)
            available_dims_layout.addWidget(add_existing_btn)
            
            layout.addWidget(available_dims_group)
            
            # Load available dimensions
            self.load_available_dimensions()
        
        # Manage Dimensions button
        manage_dims_btn = QPushButton("📐 Manage All Dimensions")
        manage_dims_btn.clicked.connect(self.open_dimension_manager)
        layout.addWidget(manage_dims_btn)
        
        layout.addStretch()
        
        self.tabs.addTab(dims_widget, "📊 Dimensions")
    
    def setup_data_tab(self):
        """Set up the data editing tab."""
        data_widget = QWidget()
        layout = QVBoxLayout(data_widget)
        
        # Data info
        self.data_info_label = QLabel("Data editing options will appear here based on component dimensions.")
        self.data_info_label.setWordWrap(True)
        self.data_info_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(self.data_info_label)
        
        # Data editing buttons
        data_buttons_layout = QHBoxLayout()
        
        self.edit_data_btn = QPushButton("📊 Edit Data")
        self.edit_data_btn.setToolTip("Open spreadsheet-style editor for multidimensional data")
        self.edit_data_btn.clicked.connect(self.edit_data)
        data_buttons_layout.addWidget(self.edit_data_btn)
        
        data_buttons_layout.addStretch()
        layout.addLayout(data_buttons_layout)
        
        layout.addStretch()
        
        self.tabs.addTab(data_widget, "💾 Data")
    
    def load_component_data(self):
        """Load component data into the dialog."""
        # Basic properties
        self.name_edit.setText(self.component.name)
        self.description_edit.setPlainText(self.component.properties.get('description', ''))
        
        # Component-specific properties
        if self.component.component_type == 'stock':
            self.initial_value_edit.setValue(self.component.properties.get('initial_value', 0))
            self.units_edit.setText(self.component.properties.get('units', ''))
            
            min_val = self.component.properties.get('min_value')
            if min_val is not None:
                self.min_value_edit.setValue(min_val)
            
            max_val = self.component.properties.get('max_value')
            if max_val is not None:
                self.max_value_edit.setValue(max_val)
                
        elif self.component.component_type == 'flow':
            self.rate_edit.setValue(self.component.properties.get('rate', 0))
            self.units_edit.setText(self.component.properties.get('units', ''))
            
        elif self.component.component_type == 'calculator':
            self.expression_edit.setPlainText(self.component.properties.get('expression', ''))
            self.units_edit.setText(self.component.properties.get('units', ''))
        
        # Load dimensions
        self.load_dimensions_list()
        self.update_data_tab()
    
    def load_dimensions_list(self):
        """Load the current component dimensions."""
        self.dimensions_list.clear()
        
        spatial_dims = self.component.properties.get('spatial_dims', [])
        for dim_name in spatial_dims:
            item = QListWidgetItem(dim_name)
            
            # Add dimension info if available
            if self.model and hasattr(self.model, 'dimensions') and dim_name in self.model.dimensions:
                dim_info = self.model.dimensions[dim_name]
                size = dim_info.get('size', 'Unknown')
                item.setText(f"{dim_name} (size: {size})")
            
            self.dimensions_list.addItem(item)
    
    def load_available_dimensions(self):
        """Load available model dimensions not in component."""
        if not hasattr(self, 'available_dimensions_list'):
            return
            
        self.available_dimensions_list.clear()
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
                self.available_dimensions_list.addItem(item)

    def add_dimension(self):
        """Add a new dimension to the component."""
        from PyQt6.QtWidgets import QInputDialog

        # Get dimension name
        name, ok = QInputDialog.getText(
            self,
            "Add Dimension",
            "Enter dimension name:",
            text="new_dimension"
        )

        if not ok or not name.strip():
            return

        name = name.strip()

        # Validate dimension name
        if not name.replace('_', '').isalnum():
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Dimension name must contain only letters, numbers, and underscores."
            )
            return

        # Check if dimension already exists in component
        spatial_dims = self.component.properties.get('spatial_dims', [])
        if name in spatial_dims:
            QMessageBox.warning(
                self,
                "Dimension Exists",
                f"Dimension '{name}' already exists in this component."
            )
            return

        # Get dimension size
        size, ok = QInputDialog.getInt(
            self,
            "Dimension Size",
            f"Enter size for dimension '{name}':",
            value=3,
            min=1,
            max=1000
        )

        if not ok:
            return

        # Add dimension to component
        spatial_dims = spatial_dims.copy()
        spatial_dims.append(name)
        self.component.properties['spatial_dims'] = spatial_dims

        # Add dimension to model if it doesn't exist
        if self.model and hasattr(self.model, 'dimensions'):
            if name not in self.model.dimensions:
                self.model.dimensions[name] = {
                    'size': size,
                    'labels': [f"{name}_{i+1}" for i in range(size)],
                    'description': f"Dimension: {name}",
                    'type': 'categorical'
                }

        # Update display
        self.load_dimensions_list()
        self.load_available_dimensions()
        self.update_data_tab()

        QMessageBox.information(
            self,
            "Dimension Added",
            f"Dimension '{name}' with size {size} has been added to {self.component.name}."
        )

    def edit_dimension(self):
        """Edit the selected dimension."""
        current_item = self.dimensions_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a dimension to edit.")
            return

        dim_name = current_item.text().split(' (')[0]  # Extract name before size info

        if not self.model or not hasattr(self.model, 'dimensions') or dim_name not in self.model.dimensions:
            QMessageBox.warning(
                self,
                "Cannot Edit",
                f"Dimension '{dim_name}' is not defined in the model.\n"
                f"You can remove it and add a new one instead."
            )
            return

        try:
            from inspector.dimension_management import DimensionDetailsEditor

            dim_data = self.model.dimensions[dim_name]
            editor = DimensionDetailsEditor(dim_name, dim_data, parent=self)

            if editor.exec() == QDialog.DialogCode.Accepted:
                updated_data = editor.get_updated_dimension_data()
                self.model.dimensions[dim_name] = updated_data

                # Update display
                self.load_dimensions_list()
                self.load_available_dimensions()
                self.update_data_tab()

                QMessageBox.information(
                    self,
                    "Dimension Updated",
                    f"Dimension '{dim_name}' has been updated successfully!\n"
                    f"New size: {updated_data.get('size', 0)} items"
                )

        except ImportError as e:
            QMessageBox.warning(
                self,
                "Feature Not Available",
                f"The dimension editor is not available.\n\nError: {e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Editor Error",
                f"Error opening dimension editor:\n\n{e}"
            )

    def remove_dimension(self):
        """Remove the selected dimension from the component."""
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

            # Update display
            self.load_dimensions_list()
            self.load_available_dimensions()
            self.update_data_tab()

    def add_existing_dimension(self):
        """Add an existing model dimension to the component."""
        if not hasattr(self, 'available_dimensions_list'):
            return

        current_item = self.available_dimensions_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "No Selection", "Please select a dimension to add.")
            return

        dim_name = current_item.data(Qt.ItemDataRole.UserRole)

        spatial_dims = self.component.properties.get('spatial_dims', [])
        if dim_name not in spatial_dims:
            spatial_dims = spatial_dims.copy()
            spatial_dims.append(dim_name)
            self.component.properties['spatial_dims'] = spatial_dims

        # Update display
        self.load_dimensions_list()
        self.load_available_dimensions()
        self.update_data_tab()

    def open_dimension_manager(self):
        """Open the comprehensive dimension manager."""
        try:
            from inspector.dimension_management import DimensionManagerDialog

            manager = DimensionManagerDialog(
                self.component,
                self.model,
                parent=self
            )

            if manager.exec() == QDialog.DialogCode.Accepted:
                # Update display
                self.load_dimensions_list()
                self.load_available_dimensions()
                self.update_data_tab()

        except ImportError as e:
            QMessageBox.warning(
                self,
                "Feature Not Available",
                f"The dimension manager is not available.\n\nError: {e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Manager Error",
                f"Error opening dimension manager:\n\n{e}"
            )

    def edit_data(self):
        """Open the data editor."""
        try:
            from inspector.spreadsheet_editor import SpreadsheetDataEditor

            editor = SpreadsheetDataEditor(
                [self.component],
                self.model,
                parent=self
            )
            editor.show()

        except ImportError as e:
            QMessageBox.information(
                self,
                "Data Editor",
                f"The data editor requires additional components.\n\nError: {e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Editor Error",
                f"Error opening data editor:\n\n{e}"
            )

    def update_data_tab(self):
        """Update the data tab based on current dimensions."""
        spatial_dims = self.component.properties.get('spatial_dims', [])

        if not spatial_dims:
            self.data_info_label.setText("This component does not have any dimensions. Add dimensions to enable data editing.")
            self.edit_data_btn.setEnabled(False)
        else:
            dims_text = f"Component has {len(spatial_dims)} dimension(s): {', '.join(spatial_dims)}"

            if self.model and hasattr(self.model, 'dimensions'):
                dim_details = []
                for dim_name in spatial_dims:
                    if dim_name in self.model.dimensions:
                        dim_info = self.model.dimensions[dim_name]
                        size = dim_info.get('size', 'Unknown')
                        dim_details.append(f"{dim_name} ({size})")
                    else:
                        dim_details.append(f"{dim_name} (undefined)")

                dims_text += f"\n\nDimension details: {', '.join(dim_details)}"

            self.data_info_label.setText(dims_text)
            self.edit_data_btn.setEnabled(True)

    def apply_changes(self):
        """Apply changes without closing the dialog."""
        self.save_component_data()
        self.component_modified.emit(self.component)
        QMessageBox.information(self, "Changes Applied", "Component changes have been applied.")

    def save_component_data(self):
        """Save the component data from the dialog."""
        # Basic properties
        self.component.name = self.name_edit.text().strip()
        self.component.properties['description'] = self.description_edit.toPlainText().strip()

        # Component-specific properties
        if self.component.component_type == 'stock':
            self.component.properties['initial_value'] = self.initial_value_edit.value()
            self.component.properties['units'] = self.units_edit.text().strip()

            if self.min_value_edit.value() != self.min_value_edit.minimum():
                self.component.properties['min_value'] = self.min_value_edit.value()
            else:
                self.component.properties.pop('min_value', None)

            if self.max_value_edit.value() != self.max_value_edit.maximum():
                self.component.properties['max_value'] = self.max_value_edit.value()
            else:
                self.component.properties.pop('max_value', None)

        elif self.component.component_type == 'flow':
            self.component.properties['rate'] = self.rate_edit.value()
            self.component.properties['units'] = self.units_edit.text().strip()

        elif self.component.component_type == 'calculator':
            self.component.properties['expression'] = self.expression_edit.toPlainText().strip()
            self.component.properties['units'] = self.units_edit.text().strip()

    def accept(self):
        """Accept the dialog and save changes."""
        self.save_component_data()
        self.component_modified.emit(self.component)
        super().accept()

    def reject(self):
        """Reject the dialog and restore original properties."""
        # Restore original properties
        self.component.properties = self.original_properties
        super().reject()
