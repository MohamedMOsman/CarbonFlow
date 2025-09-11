"""
Component Inspector for Property Inspection and Editing

This module provides a properties panel for inspecting and editing
system dynamics components, including multidimensional data display.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QTableWidget, QTableWidgetItem, QTabWidget, QScrollArea,
    QGroupBox, QFormLayout, QPushButton, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QSplitter, QHeaderView, QMessageBox,
    QInputDialog, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette
from typing import Dict, List, Optional, Any, Union
import numpy as np

from yaml_integration.yaml_loader import ModelComponent, GuiModel
from components.component_types import get_component_type, validate_component_properties
from inspector.property_editors import PropertyEditorFactory


class ComponentInspector(QWidget):
    """
    Component inspector widget for viewing and editing component properties.
    
    Provides:
    - Basic property editing (name, description, units)
    - Multidimensional data display in tabular format
    - Connection and dependency visualization
    - Runtime value monitoring during simulation
    """
    
    # Signals
    component_modified = pyqtSignal(object)  # Emitted when component is modified
    property_changed = pyqtSignal(str, str, object)  # component_name, property_name, new_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumWidth(250)
        self.setMaximumWidth(400)
        
        # Current state
        self.current_component = None
        self.current_model = None
        self.is_runtime_mode = False  # Whether showing runtime values
        self.simulation_results = None
        
        # Property editors
        self.property_editors = {}
        self.editor_factory = PropertyEditorFactory()
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the inspector user interface."""
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Title
        title_label = QLabel("Component Inspector")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("QLabel { color: #333; padding: 5px; }")
        layout.addWidget(title_label)
        
        # Mode toggle
        mode_layout = QHBoxLayout()
        self.design_mode_btn = QPushButton("Design Mode")
        self.design_mode_btn.setCheckable(True)
        self.design_mode_btn.setChecked(True)
        self.design_mode_btn.clicked.connect(self.set_design_mode)
        
        self.runtime_mode_btn = QPushButton("Runtime Mode")
        self.runtime_mode_btn.setCheckable(True)
        self.runtime_mode_btn.clicked.connect(self.set_runtime_mode)
        
        mode_layout.addWidget(self.design_mode_btn)
        mode_layout.addWidget(self.runtime_mode_btn)
        layout.addLayout(mode_layout)
        
        # Create tabbed interface
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Properties tab
        self.properties_tab = self.create_properties_tab()
        self.tab_widget.addTab(self.properties_tab, "Properties")
        
        # Data tab (for multidimensional data)
        self.data_tab = self.create_data_tab()
        self.tab_widget.addTab(self.data_tab, "Data")
        
        # Connections tab
        self.connections_tab = self.create_connections_tab()
        self.tab_widget.addTab(self.connections_tab, "Connections")
        
        # No selection message
        self.no_selection_label = QLabel("No component selected.\n\nSelect a component on the canvas to view its properties.")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_selection_label.setStyleSheet("QLabel { color: #666; padding: 20px; }")
        layout.addWidget(self.no_selection_label)
        
        # Initially hide tabs
        self.tab_widget.hide()
        
    def create_properties_tab(self) -> QWidget:
        """Create the properties editing tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Properties form widget
        self.properties_form_widget = QWidget()
        self.properties_form_layout = QFormLayout(self.properties_form_widget)
        self.properties_form_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(self.properties_form_widget)
        layout.addWidget(scroll_area)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.apply_property_changes)
        self.apply_btn.setEnabled(False)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_property_changes)
        self.reset_btn.setEnabled(False)
        
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)
        
        return widget
        
    def create_data_tab(self) -> QWidget:
        """Create the multidimensional data display tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Data info
        self.data_info_label = QLabel("Multidimensional data will be displayed here.")
        self.data_info_label.setStyleSheet("QLabel { color: #666; padding: 10px; }")
        layout.addWidget(self.data_info_label)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        layout.addWidget(self.data_table)
        
        # Data controls
        controls_layout = QHBoxLayout()
        
        self.refresh_data_btn = QPushButton("Refresh Data")
        self.refresh_data_btn.clicked.connect(self.refresh_data_display)
        
        self.export_data_btn = QPushButton("Export Data")
        self.export_data_btn.clicked.connect(self.export_data)
        
        controls_layout.addWidget(self.refresh_data_btn)
        controls_layout.addWidget(self.export_data_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        return widget
        
    def create_connections_tab(self) -> QWidget:
        """Create the connections display tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Incoming connections
        incoming_group = QGroupBox("Incoming Connections")
        incoming_layout = QVBoxLayout(incoming_group)
        self.incoming_connections_list = QTableWidget()
        self.incoming_connections_list.setColumnCount(3)
        self.incoming_connections_list.setHorizontalHeaderLabels(["From", "Type", "Description"])
        incoming_layout.addWidget(self.incoming_connections_list)
        layout.addWidget(incoming_group)
        
        # Outgoing connections
        outgoing_group = QGroupBox("Outgoing Connections")
        outgoing_layout = QVBoxLayout(outgoing_group)
        self.outgoing_connections_list = QTableWidget()
        self.outgoing_connections_list.setColumnCount(3)
        self.outgoing_connections_list.setHorizontalHeaderLabels(["To", "Type", "Description"])
        outgoing_layout.addWidget(self.outgoing_connections_list)
        layout.addWidget(outgoing_group)
        
        return widget
        
    def set_model(self, model: GuiModel):
        """Set the current model."""
        self.current_model = model
        
    def set_component(self, component: ModelComponent):
        """Set the component to inspect."""
        
        self.current_component = component
        
        if component:
            # Show tabs and hide no selection message
            self.tab_widget.show()
            self.no_selection_label.hide()
            
            # Update all tabs
            self.update_properties_tab()
            self.update_data_tab()
            self.update_connections_tab()

            # Update button states
            self.update_dimension_button_states()
            
        else:
            # Hide tabs and show no selection message
            self.tab_widget.hide()
            self.no_selection_label.show()
            
    def update_properties_tab(self):
        """Update the properties tab with current component data."""
        
        if not self.current_component:
            return
            
        # Clear existing editors
        self.clear_property_editors()
        
        # Get component type definition
        comp_type = get_component_type(self.current_component.component_type)
        if not comp_type:
            return
            
        # Create editors for all properties
        properties = self.current_component.properties
        
        # Basic properties (always shown)
        self.add_property_editor("name", "Name", self.current_component.name, "text")
        self.add_property_editor("description", "Description", 
                                properties.get("description", ""), "text")
        
        # Type-specific properties
        for prop_name in comp_type.required_properties + comp_type.optional_properties:
            if prop_name in ["name", "description"]:
                continue  # Already handled
                
            prop_value = properties.get(prop_name)
            if prop_value is not None:
                # Determine editor type based on property
                editor_type = self.get_editor_type_for_property(prop_name, prop_value)
                display_name = prop_name.replace("_", " ").title()
                self.add_property_editor(prop_name, display_name, prop_value, editor_type)
                
    def add_property_editor(self, prop_name: str, display_name: str, 
                           value: Any, editor_type: str):
        """Add a property editor to the form."""
        
        editor = self.editor_factory.create_editor(editor_type, value)
        if editor:
            # Connect change signal
            if hasattr(editor, 'textChanged'):
                editor.textChanged.connect(self.on_property_changed)
            elif hasattr(editor, 'valueChanged'):
                editor.valueChanged.connect(self.on_property_changed)
            elif hasattr(editor, 'currentTextChanged'):
                editor.currentTextChanged.connect(self.on_property_changed)
                
            # Store editor reference
            self.property_editors[prop_name] = editor
            
            # Add to form
            self.properties_form_layout.addRow(display_name + ":", editor)
            
    def get_editor_type_for_property(self, prop_name: str, value: Any) -> str:
        """Determine the appropriate editor type for a property."""
        
        if isinstance(value, bool):
            return "checkbox"
        elif isinstance(value, int):
            return "spinbox"
        elif isinstance(value, float):
            return "double_spinbox"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        else:
            return "text"
            
    def clear_property_editors(self):
        """Clear all property editors."""
        
        # Remove all widgets from form layout
        while self.properties_form_layout.count():
            child = self.properties_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        self.property_editors.clear()
        
    def update_data_tab(self):
        """Update the data tab with multidimensional data."""
        
        if not self.current_component:
            return
            
        # Check if component has multidimensional data
        spatial_dims = self.current_component.properties.get('spatial_dims', [])

        if not spatial_dims:
            self.data_info_label.setText("This component does not have multidimensional data.")
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return

        # Display dimensional structure
        dims_text = f"Dimensions: {', '.join(spatial_dims)}"

        if self.current_model and self.current_model.dimensions:
            # Add dimension details
            dim_details = []
            for dim_name in spatial_dims:
                dim_info = self.current_model.dimensions.get(dim_name, {})
                labels = dim_info.get('labels', [])
                size = dim_info.get('size', len(labels))
                dim_details.append(f"{dim_name} ({size}): {', '.join(labels[:5])}")
                if len(labels) > 5:
                    dim_details[-1] += f" ... and {len(labels) - 5} more"

            dims_text += "\n\n" + "\n".join(dim_details)

        self.data_info_label.setText(dims_text)

        # Add buttons for multidimensional data management
        if not hasattr(self, 'data_buttons_widget'):
            self.data_buttons_widget = QWidget()
            buttons_layout = QHBoxLayout(self.data_buttons_widget)
            buttons_layout.setContentsMargins(0, 5, 0, 5)

            # Edit Data button
            self.edit_data_btn = QPushButton("📊 Edit Data")
            self.edit_data_btn.setToolTip("Open spreadsheet-style editor for multidimensional data")
            self.edit_data_btn.clicked.connect(self.open_spreadsheet_editor)
            buttons_layout.addWidget(self.edit_data_btn)

            # Manage Dimensions button
            self.manage_dims_btn = QPushButton("📐 Manage Dimensions")
            self.manage_dims_btn.setToolTip("Add, remove, or modify component dimensions")
            self.manage_dims_btn.clicked.connect(self.open_dimension_manager)
            buttons_layout.addWidget(self.manage_dims_btn)

            # Quick Add Dimension button
            self.add_dim_btn = QPushButton("➕ Add Dimension")
            self.add_dim_btn.setToolTip("Quickly add a new dimension to this component")
            self.add_dim_btn.clicked.connect(self.quick_add_dimension)
            buttons_layout.addWidget(self.add_dim_btn)

            # Quick Edit Dimension button
            self.edit_dim_btn = QPushButton("✏️ Edit Dimension")
            self.edit_dim_btn.setToolTip("Edit details of an existing dimension (labels, years, ages, etc.)")
            self.edit_dim_btn.clicked.connect(self.quick_edit_dimension)
            buttons_layout.addWidget(self.edit_dim_btn)

            buttons_layout.addStretch()

            # Insert buttons after data_info_label
            data_tab_layout = self.data_tab.layout()
            data_tab_layout.insertWidget(1, self.data_buttons_widget)

        # Display actual data values if available
        self.display_current_data_values()

        # Update button states based on available dimensions
        self.update_dimension_button_states()
        # This would require integration with simulation results
        
    def update_connections_tab(self):
        """Update the connections tab."""
        
        if not self.current_component or not self.current_model:
            return
            
        # Clear tables
        self.incoming_connections_list.setRowCount(0)
        self.outgoing_connections_list.setRowCount(0)
        
        component_name = self.current_component.name
        
        # Find incoming connections
        incoming = []
        outgoing = []
        
        for from_name, to_name, conn_type in self.current_model.connections:
            if to_name == component_name:
                incoming.append((from_name, conn_type))
            elif from_name == component_name:
                outgoing.append((to_name, conn_type))
                
        # Populate incoming connections table
        self.incoming_connections_list.setRowCount(len(incoming))
        for i, (from_name, conn_type) in enumerate(incoming):
            self.incoming_connections_list.setItem(i, 0, QTableWidgetItem(from_name))
            self.incoming_connections_list.setItem(i, 1, QTableWidgetItem(conn_type))
            self.incoming_connections_list.setItem(i, 2, QTableWidgetItem(""))  # Description
            
        # Populate outgoing connections table
        self.outgoing_connections_list.setRowCount(len(outgoing))
        for i, (to_name, conn_type) in enumerate(outgoing):
            self.outgoing_connections_list.setItem(i, 0, QTableWidgetItem(to_name))
            self.outgoing_connections_list.setItem(i, 1, QTableWidgetItem(conn_type))
            self.outgoing_connections_list.setItem(i, 2, QTableWidgetItem(""))  # Description
            
        # Resize columns
        self.incoming_connections_list.resizeColumnsToContents()
        self.outgoing_connections_list.resizeColumnsToContents()
        
    def set_design_mode(self):
        """Switch to design mode."""
        self.is_runtime_mode = False
        self.design_mode_btn.setChecked(True)
        self.runtime_mode_btn.setChecked(False)
        self.update_properties_tab()
        
    def set_runtime_mode(self):
        """Switch to runtime mode."""
        self.is_runtime_mode = True
        self.design_mode_btn.setChecked(False)
        self.runtime_mode_btn.setChecked(True)
        # TODO: Update display for runtime values
        
    def on_property_changed(self):
        """Handle property value changes."""
        self.apply_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        
    def apply_property_changes(self):
        """Apply property changes to the component."""
        
        if not self.current_component:
            return
            
        # Collect values from editors
        changes = {}
        
        for prop_name, editor in self.property_editors.items():
            if prop_name == "name":
                new_value = editor.text() if hasattr(editor, 'text') else str(editor.value())
                if new_value != self.current_component.name:
                    changes[prop_name] = new_value
            else:
                if hasattr(editor, 'text'):
                    new_value = editor.text()
                elif hasattr(editor, 'value'):
                    new_value = editor.value()
                elif hasattr(editor, 'currentText'):
                    new_value = editor.currentText()
                else:
                    continue
                    
                old_value = self.current_component.properties.get(prop_name)
                if new_value != old_value:
                    changes[prop_name] = new_value
                    
        # Apply changes
        if changes:
            if "name" in changes:
                self.current_component.name = changes["name"]
                
            for prop_name, new_value in changes.items():
                if prop_name != "name":
                    self.current_component.properties[prop_name] = new_value
                    
            # Emit signals
            self.component_modified.emit(self.current_component)
            for prop_name, new_value in changes.items():
                self.property_changed.emit(self.current_component.name, prop_name, new_value)
                
        self.apply_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        
    def reset_property_changes(self):
        """Reset property changes."""
        self.update_properties_tab()
        self.apply_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        
    def refresh_data_display(self):
        """Refresh the data display."""
        self.update_data_tab()
        
    def export_data(self):
        """Export component data."""
        # TODO: Implement data export functionality
        pass
        
    def set_simulation_results(self, results):
        """Set simulation results for runtime inspection."""
        self.simulation_results = results
        if self.is_runtime_mode:
            self.update_data_tab()

    def open_spreadsheet_editor(self):
        """Open the spreadsheet-style component data editor."""
        if not self.current_component:
            return

        try:
            from inspector.spreadsheet_editor import SpreadsheetDataEditor

            # Open the spreadsheet editor
            editor = SpreadsheetDataEditor(
                [self.current_component],
                self.current_model,
                parent=self
            )
            editor.show()

            # Connect to modification signal
            editor.component_modified.connect(self.on_component_modified_from_editor)

        except ImportError as e:
            QMessageBox.information(
                self,
                "Spreadsheet Editor",
                f"The spreadsheet editor requires additional components.\n\n"
                f"Error: {e}\n\n"
                f"Please ensure all GUI dependencies are installed:\n"
                f"pip install PyQt6 PyYAML\n\n"
                f"You can still edit component properties using the basic inspector."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Editor Error",
                f"Error opening spreadsheet editor:\n\n{e}\n\n"
                f"Component: {self.current_component.name}\n"
                f"Type: {self.current_component.component_type}\n\n"
                f"Please check the console for more details."
            )

    def on_component_modified_from_editor(self, component):
        """Handle component modification from the spreadsheet editor."""
        if component == self.current_component:
            # Update display
            self.update_data_tab()

            # Emit signal
            self.component_modified.emit(self.current_component)

    def open_dimension_manager(self):
        """Open the dimension management dialog."""
        if not self.current_component:
            return

        try:
            from inspector.dimension_management import DimensionManagerDialog

            # Open the dimension manager
            manager = DimensionManagerDialog(
                self.current_component,
                self.current_model,
                parent=self
            )

            if manager.exec() == QDialog.DialogCode.Accepted:
                # Update component with new dimensions
                self.update_data_tab()
                self.update_properties_tab()
                self.component_modified.emit(self.current_component)

        except ImportError as e:
            QMessageBox.information(
                self,
                "Dimension Manager",
                f"The dimension manager requires additional components.\n\n"
                f"Error: {e}\n\n"
                f"You can still edit dimensions using the basic property editor."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Manager Error",
                f"Error opening dimension manager:\n\n{e}"
            )

    def quick_add_dimension(self):
        """Quickly add a new dimension to the current component."""
        if not self.current_component:
            return

        # Get dimension name from user
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
        spatial_dims = self.current_component.properties.get('spatial_dims', [])
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
            value=2,
            min=1,
            max=1000
        )

        if not ok:
            return

        # Add dimension to component
        spatial_dims = spatial_dims.copy()
        spatial_dims.append(name)
        self.current_component.properties['spatial_dims'] = spatial_dims

        # Add dimension to model if it doesn't exist
        if self.current_model and hasattr(self.current_model, 'dimensions'):
            if name not in self.current_model.dimensions:
                self.current_model.dimensions[name] = {
                    'size': size,
                    'labels': [f"{name}_{i+1}" for i in range(size)],
                    'description': f"Auto-generated dimension: {name}",
                    'type': 'categorical'
                }

        # Update display
        self.update_data_tab()
        self.update_properties_tab()
        self.component_modified.emit(self.current_component)

        QMessageBox.information(
            self,
            "Dimension Added",
            f"Dimension '{name}' with size {size} has been added to {self.current_component.name}.\n\n"
            f"You can now use the 'Edit Data' button to set values for this dimension."
        )

    def quick_edit_dimension(self):
        """Quick edit of an existing dimension."""
        if not self.current_component:
            return

        # Get component's spatial dimensions
        spatial_dims = self.current_component.properties.get('spatial_dims', [])
        if not spatial_dims:
            QMessageBox.information(
                self,
                "No Dimensions",
                "This component doesn't have any dimensions to edit.\n"
                "Use 'Add Dimension' to create one first."
            )
            return

        # Let user choose which dimension to edit
        if len(spatial_dims) == 1:
            dim_name = spatial_dims[0]
        else:
            dim_name, ok = QInputDialog.getItem(
                self,
                "Select Dimension",
                "Choose dimension to edit:",
                spatial_dims,
                0,
                False
            )
            if not ok:
                return

        # Check if dimension exists in model
        if not self.current_model or not hasattr(self.current_model, 'dimensions'):
            QMessageBox.warning(
                self,
                "No Model Dimensions",
                f"Dimension '{dim_name}' is not defined in the model.\n"
                f"Use 'Manage Dimensions' for more advanced editing."
            )
            return

        if dim_name not in self.current_model.dimensions:
            QMessageBox.warning(
                self,
                "Dimension Not Found",
                f"Dimension '{dim_name}' is not defined in the model.\n"
                f"Use 'Manage Dimensions' to add it to the model first."
            )
            return

        # Open the detailed dimension editor
        try:
            from inspector.dimension_management import DimensionDetailsEditor

            dim_data = self.current_model.dimensions[dim_name]
            editor = DimensionDetailsEditor(dim_name, dim_data, parent=self)

            if editor.exec() == QDialog.DialogCode.Accepted:
                # Update the model with new dimension data
                updated_data = editor.get_updated_dimension_data()
                self.current_model.dimensions[dim_name] = updated_data

                # Update display
                self.update_data_tab()
                self.update_properties_tab()
                self.component_modified.emit(self.current_component)

                QMessageBox.information(
                    self,
                    "Dimension Updated",
                    f"Dimension '{dim_name}' has been updated successfully!\n"
                    f"New size: {updated_data.get('size', 0)} items\n\n"
                    f"You can now use 'Edit Data' to set values for the updated dimension."
                )

        except ImportError as e:
            QMessageBox.warning(
                self,
                "Feature Not Available",
                f"The detailed dimension editor is not available.\n\n"
                f"Error: {e}\n\n"
                f"Use 'Manage Dimensions' for basic editing."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Editor Error",
                f"Error opening dimension editor:\n\n{e}"
            )

    def update_dimension_button_states(self):
        """Update the state of dimension-related buttons based on current component."""
        if not hasattr(self, 'data_buttons_widget'):
            return

        has_component = self.current_component is not None
        has_dimensions = False
        has_model_dimensions = False

        if has_component:
            spatial_dims = self.current_component.properties.get('spatial_dims', [])
            has_dimensions = len(spatial_dims) > 0

            if self.current_model and hasattr(self.current_model, 'dimensions'):
                has_model_dimensions = len(self.current_model.dimensions) > 0

        # Enable/disable buttons based on state
        if hasattr(self, 'edit_data_btn'):
            self.edit_data_btn.setEnabled(has_component and has_dimensions)

        if hasattr(self, 'manage_dims_btn'):
            self.manage_dims_btn.setEnabled(has_component)

        if hasattr(self, 'add_dim_btn'):
            self.add_dim_btn.setEnabled(has_component)

        if hasattr(self, 'edit_dim_btn'):
            self.edit_dim_btn.setEnabled(has_component and has_dimensions and has_model_dimensions)

            # Update tooltip based on state
            if not has_component:
                self.edit_dim_btn.setToolTip("Select a component first")
            elif not has_dimensions:
                self.edit_dim_btn.setToolTip("Component has no dimensions - add one first")
            elif not has_model_dimensions:
                self.edit_dim_btn.setToolTip("No model dimensions available - use 'Manage Dimensions' first")
            else:
                self.edit_dim_btn.setToolTip("Edit details of an existing dimension (labels, years, ages, etc.)")

    def display_current_data_values(self):
        """Display current data values in the data table."""
        if not self.current_component:
            return

        # Clear existing table
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)

        # Get spatial dimensions
        spatial_dims = self.current_component.properties.get('spatial_dims', [])
        if not spatial_dims:
            return

        # Get initial value or rate data
        data_key = None
        if self.current_component.component_type == 'stock':
            data_key = 'initial_value'
        elif self.current_component.component_type == 'flow':
            data_key = 'rate'
        elif self.current_component.component_type == 'calculator':
            # Calculators don't typically have initial data
            return

        if not data_key:
            return

        data_value = self.current_component.properties.get(data_key)
        if data_value is None:
            return

        try:
            # Handle different data formats
            if isinstance(data_value, dict) and 'array' in data_value:
                # Multidimensional array format
                array_data = data_value['array']
                if 'values' in array_data:
                    values = array_data['values']
                    shape = array_data.get('shape', [])

                    # Display array data in table format
                    self._display_array_data(values, shape, spatial_dims)

            elif isinstance(data_value, (list, tuple)):
                # Simple list/tuple
                self._display_simple_list(data_value, spatial_dims)

            elif isinstance(data_value, (int, float)):
                # Scalar value
                self._display_scalar_value(data_value, spatial_dims)

        except Exception as e:
            # If there's an error displaying data, show a message
            self.data_table.setRowCount(1)
            self.data_table.setColumnCount(1)
            self.data_table.setHorizontalHeaderLabels(["Value"])
            item = QTableWidgetItem(f"Error displaying data: {e}")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.data_table.setItem(0, 0, item)

    def _display_array_data(self, values, shape, spatial_dims):
        """Display multidimensional array data."""
        if not values or not shape:
            return

        try:
            # Convert to numpy array for easier handling
            import numpy as np
            arr = np.array(values).reshape(shape)

            if len(shape) == 1:
                # 1D array
                self.data_table.setRowCount(1)
                self.data_table.setColumnCount(shape[0])

                # Set headers
                if self.current_model and spatial_dims:
                    dim_name = spatial_dims[0]
                    dim_info = self.current_model.dimensions.get(dim_name, {})
                    labels = dim_info.get('labels', [f"{dim_name}_{i+1}" for i in range(shape[0])])
                    self.data_table.setHorizontalHeaderLabels(labels[:shape[0]])

                # Set values
                for j in range(shape[0]):
                    item = QTableWidgetItem(str(arr[j]))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.data_table.setItem(0, j, item)

            elif len(shape) == 2:
                # 2D array
                self.data_table.setRowCount(shape[0])
                self.data_table.setColumnCount(shape[1])

                # Set headers if available
                if self.current_model and len(spatial_dims) >= 2:
                    # Column headers (second dimension)
                    dim_name = spatial_dims[1]
                    dim_info = self.current_model.dimensions.get(dim_name, {})
                    col_labels = dim_info.get('labels', [f"{dim_name}_{i+1}" for i in range(shape[1])])
                    self.data_table.setHorizontalHeaderLabels(col_labels[:shape[1]])

                    # Row headers (first dimension)
                    dim_name = spatial_dims[0]
                    dim_info = self.current_model.dimensions.get(dim_name, {})
                    row_labels = dim_info.get('labels', [f"{dim_name}_{i+1}" for i in range(shape[0])])
                    self.data_table.setVerticalHeaderLabels(row_labels[:shape[0]])

                # Set values
                for i in range(shape[0]):
                    for j in range(shape[1]):
                        item = QTableWidgetItem(str(arr[i, j]))
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.data_table.setItem(i, j, item)
            else:
                # Higher dimensional - show flattened with info
                flat_values = arr.flatten()
                self.data_table.setRowCount(1)
                self.data_table.setColumnCount(len(flat_values))
                self.data_table.setHorizontalHeaderLabels([f"Pos_{i}" for i in range(len(flat_values))])

                for j, val in enumerate(flat_values):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.data_table.setItem(0, j, item)

        except ImportError:
            # Fallback without numpy
            self.data_table.setRowCount(1)
            self.data_table.setColumnCount(1)
            self.data_table.setHorizontalHeaderLabels(["Values"])
            item = QTableWidgetItem(str(values))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.data_table.setItem(0, 0, item)

    def _display_simple_list(self, values, spatial_dims):
        """Display simple list data."""
        self.data_table.setRowCount(1)
        self.data_table.setColumnCount(len(values))

        # Set headers if available
        if self.current_model and spatial_dims:
            dim_name = spatial_dims[0]
            dim_info = self.current_model.dimensions.get(dim_name, {})
            labels = dim_info.get('labels', [f"{dim_name}_{i+1}" for i in range(len(values))])
            self.data_table.setHorizontalHeaderLabels(labels[:len(values)])

        # Set values
        for j, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.data_table.setItem(0, j, item)

    def _display_scalar_value(self, value, spatial_dims):
        """Display scalar value."""
        self.data_table.setRowCount(1)
        self.data_table.setColumnCount(1)
        self.data_table.setHorizontalHeaderLabels(["Value"])

        item = QTableWidgetItem(str(value))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.data_table.setItem(0, 0, item)
