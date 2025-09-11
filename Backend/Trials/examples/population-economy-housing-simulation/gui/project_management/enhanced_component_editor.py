"""
Enhanced Component Editor

Extends the existing multidimensional editor with project management integration,
validation, integrity checks, and enhanced dimension editing capabilities.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QPushButton, QLabel, QMessageBox, QGroupBox, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from typing import Dict, List, Optional, Any

from .project_manager import SystemModel, Project
from .informants_manager import InformantsManager
from .informants_editor_dialog import InformantsEditorDialog
from ..yaml_integration.yaml_loader import ModelComponent
from ..inspector.multidimensional_editor import MultidimensionalEditorDialog, DimensionTableEditor


class EnhancedComponentEditor(QDialog):
    """
    Enhanced component editor with project management integration.
    
    Features:
    - Integration with project/system hierarchy
    - Validation against system dimensions
    - Integrity checking with informants
    - Enhanced multidimensional editing
    - Real-time validation feedback
    """
    
    component_modified = pyqtSignal(object)  # ModelComponent
    
    def __init__(self, component: ModelComponent, system: SystemModel, 
                 project: Project, parent=None):
        super().__init__(parent)
        
        self.component = component
        self.system = system
        self.project = project
        self.informants_manager = InformantsManager()
        
        # Track changes
        self.modified = False
        self.original_properties = component.properties.copy()
        
        self.setWindowTitle(f"Enhanced Component Editor - {component.name}")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)
        
        self.setup_ui()
        self.load_component_data()
        self.validate_component()
    
    def setup_ui(self):
        """Set up the enhanced editor UI."""
        layout = QVBoxLayout(self)
        
        # Header with component info
        header = self.create_header()
        layout.addWidget(header)
        
        # Main tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Basic properties tab
        self.setup_basic_properties_tab()
        
        # Dimensions tab
        self.setup_dimensions_tab()
        
        # Validation tab
        self.setup_validation_tab()
        
        # Advanced tab
        self.setup_advanced_tab()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        # Informants button
        informants_btn = QPushButton("Manage Informants")
        informants_btn.clicked.connect(self.open_informants_manager)
        buttons_layout.addWidget(informants_btn)
        
        # Validate button
        validate_btn = QPushButton("Validate")
        validate_btn.clicked.connect(self.validate_component)
        buttons_layout.addWidget(validate_btn)
        
        buttons_layout.addStretch()
        
        # Standard buttons
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_and_accept)
        save_btn.setDefault(True)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_header(self) -> QWidget:
        """Create the header with component information."""
        header = QGroupBox("Component Information")
        layout = QFormLayout(header)
        
        # Component name
        self.name_edit = QLineEdit(self.component.name)
        self.name_edit.textChanged.connect(self.on_modified)
        layout.addRow("Name:", self.name_edit)
        
        # Component type (read-only)
        type_label = QLabel(self.component.component_type.title())
        type_label.setStyleSheet("QLabel { font-weight: bold; }")
        layout.addRow("Type:", type_label)
        
        # System and project info
        system_label = QLabel(f"{self.system.name} (Project: {self.project.name})")
        system_label.setStyleSheet("QLabel { color: #666; }")
        layout.addRow("System:", system_label)
        
        return header
    
    def setup_basic_properties_tab(self):
        """Set up the basic properties editing tab."""
        basic_widget = QWidget()
        layout = QVBoxLayout(basic_widget)
        
        # Core properties group
        core_group = QGroupBox("Core Properties")
        core_layout = QFormLayout(core_group)
        
        # Units
        self.units_edit = QLineEdit()
        self.units_edit.textChanged.connect(self.on_modified)
        core_layout.addRow("Units:", self.units_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.textChanged.connect(self.on_modified)
        core_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(core_group)
        
        # Type-specific properties
        self.type_specific_group = QGroupBox(f"{self.component.component_type.title()} Properties")
        self.type_specific_layout = QFormLayout(self.type_specific_group)
        self.setup_type_specific_properties()
        layout.addWidget(self.type_specific_group)
        
        # Constraints group (for stocks)
        if self.component.component_type == 'stock':
            constraints_group = QGroupBox("Constraints")
            constraints_layout = QFormLayout(constraints_group)
            
            self.min_value_edit = QLineEdit()
            self.min_value_edit.textChanged.connect(self.on_modified)
            constraints_layout.addRow("Minimum Value:", self.min_value_edit)
            
            self.max_value_edit = QLineEdit()
            self.max_value_edit.textChanged.connect(self.on_modified)
            constraints_layout.addRow("Maximum Value:", self.max_value_edit)
            
            layout.addWidget(constraints_group)
        
        layout.addStretch()
        self.tabs.addTab(basic_widget, "Basic Properties")
    
    def setup_type_specific_properties(self):
        """Set up properties specific to the component type."""
        if self.component.component_type == 'stock':
            # Initial value
            self.initial_value_edit = QLineEdit()
            self.initial_value_edit.textChanged.connect(self.on_modified)
            self.type_specific_layout.addRow("Initial Value:", self.initial_value_edit)
            
        elif self.component.component_type == 'flow':
            # Rate
            self.rate_edit = QLineEdit()
            self.rate_edit.textChanged.connect(self.on_modified)
            self.type_specific_layout.addRow("Rate:", self.rate_edit)
            
        elif self.component.component_type == 'calculator':
            # Expression
            self.expression_edit = QTextEdit()
            self.expression_edit.setMaximumHeight(60)
            self.expression_edit.textChanged.connect(self.on_modified)
            self.type_specific_layout.addRow("Expression:", self.expression_edit)
    
    def setup_dimensions_tab(self):
        """Set up the dimensions editing tab."""
        dimensions_widget = QWidget()
        layout = QVBoxLayout(dimensions_widget)
        
        # Instructions
        instructions = QLabel(
            "Configure the spatial dimensions for this component. "
            "Dimensions must be defined in the system before they can be used."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { color: #666; margin-bottom: 10px; }")
        layout.addWidget(instructions)
        
        # Available dimensions
        available_group = QGroupBox("Available System Dimensions")
        available_layout = QVBoxLayout(available_group)
        
        self.available_dimensions_list = QWidget()
        self.available_dimensions_layout = QVBoxLayout(self.available_dimensions_list)
        available_layout.addWidget(self.available_dimensions_list)
        
        layout.addWidget(available_group)
        
        # Selected dimensions
        selected_group = QGroupBox("Component Spatial Dimensions")
        selected_layout = QVBoxLayout(selected_group)
        
        self.selected_dimensions_list = QWidget()
        self.selected_dimensions_layout = QVBoxLayout(self.selected_dimensions_list)
        selected_layout.addWidget(self.selected_dimensions_list)
        
        layout.addWidget(selected_group)
        
        # Multidimensional data editor button
        if self.component.component_type in ['stock', 'flow']:
            data_button = QPushButton("Edit Multidimensional Data")
            data_button.clicked.connect(self.open_multidimensional_editor)
            layout.addWidget(data_button)
        
        self.tabs.addTab(dimensions_widget, "Dimensions")
    
    def setup_validation_tab(self):
        """Set up the validation results tab."""
        validation_widget = QWidget()
        layout = QVBoxLayout(validation_widget)
        
        layout.addWidget(QLabel("Component Validation Results:"))
        
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        layout.addWidget(self.validation_text)
        
        refresh_btn = QPushButton("Refresh Validation")
        refresh_btn.clicked.connect(self.validate_component)
        layout.addWidget(refresh_btn)
        
        self.tabs.addTab(validation_widget, "Validation")
    
    def setup_advanced_tab(self):
        """Set up the advanced properties tab."""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        
        # Parameters group (for flows and calculators)
        if self.component.component_type in ['flow', 'calculator']:
            params_group = QGroupBox("Parameters")
            params_layout = QVBoxLayout(params_group)
            
            self.parameters_edit = QTextEdit()
            self.parameters_edit.setMaximumHeight(100)
            self.parameters_edit.textChanged.connect(self.on_modified)
            params_layout.addWidget(self.parameters_edit)
            
            layout.addWidget(params_group)
        
        # Dependencies group (for calculators)
        if self.component.component_type == 'calculator':
            deps_group = QGroupBox("Dependencies")
            deps_layout = QVBoxLayout(deps_group)
            
            self.dependencies_edit = QTextEdit()
            self.dependencies_edit.setMaximumHeight(80)
            self.dependencies_edit.textChanged.connect(self.on_modified)
            deps_layout.addWidget(self.dependencies_edit)
            
            layout.addWidget(deps_group)
        
        layout.addStretch()
        self.tabs.addTab(advanced_widget, "Advanced")
    
    def load_component_data(self):
        """Load component data into the UI."""
        props = self.component.properties
        
        # Basic properties
        self.units_edit.setText(props.get('units', ''))
        self.description_edit.setPlainText(props.get('description', ''))
        
        # Type-specific properties
        if self.component.component_type == 'stock':
            initial_value = props.get('initial_value', '')
            if isinstance(initial_value, dict):
                # Handle array format
                self.initial_value_edit.setText(str(initial_value))
            else:
                self.initial_value_edit.setText(str(initial_value))
            
            self.min_value_edit.setText(str(props.get('min_value', '')))
            self.max_value_edit.setText(str(props.get('max_value', '')))
            
        elif self.component.component_type == 'flow':
            self.rate_edit.setText(str(props.get('rate', '')))
            
        elif self.component.component_type == 'calculator':
            self.expression_edit.setPlainText(props.get('expression', ''))
        
        # Advanced properties
        if hasattr(self, 'parameters_edit'):
            params = props.get('parameters', {})
            self.parameters_edit.setPlainText(str(params) if params else '')
        
        if hasattr(self, 'dependencies_edit'):
            deps = props.get('dependencies', [])
            self.dependencies_edit.setPlainText('\n'.join(deps) if deps else '')
        
        # Load dimensions
        self.load_dimensions()
    
    def load_dimensions(self):
        """Load dimension information."""
        # Clear existing dimension widgets
        for i in reversed(range(self.available_dimensions_layout.count())):
            self.available_dimensions_layout.itemAt(i).widget().setParent(None)
        
        for i in reversed(range(self.selected_dimensions_layout.count())):
            self.selected_dimensions_layout.itemAt(i).widget().setParent(None)
        
        # Get component's spatial dimensions
        spatial_dims = self.component.properties.get('spatial_dims', [])
        
        # Show available dimensions
        for dim_name, dim_data in self.system.dimensions.items():
            checkbox = QCheckBox(f"{dim_name} (size: {dim_data.get('size', 1)})")
            checkbox.setChecked(dim_name in spatial_dims)
            checkbox.toggled.connect(self.on_dimension_toggled)
            checkbox.setProperty('dimension_name', dim_name)
            self.available_dimensions_layout.addWidget(checkbox)
        
        # Show selected dimensions info
        for dim_name in spatial_dims:
            if dim_name in self.system.dimensions:
                dim_data = self.system.dimensions[dim_name]
                info_label = QLabel(
                    f"{dim_name}: {dim_data.get('description', 'No description')} "
                    f"(Labels: {', '.join(dim_data.get('labels', [])[:3])}{'...' if len(dim_data.get('labels', [])) > 3 else ''})"
                )
                info_label.setWordWrap(True)
                info_label.setStyleSheet("QLabel { color: #333; margin: 2px; }")
                self.selected_dimensions_layout.addWidget(info_label)
    
    def on_dimension_toggled(self, checked: bool):
        """Handle dimension selection changes."""
        sender = self.sender()
        dim_name = sender.property('dimension_name')
        
        spatial_dims = self.component.properties.get('spatial_dims', [])
        
        if checked and dim_name not in spatial_dims:
            spatial_dims.append(dim_name)
        elif not checked and dim_name in spatial_dims:
            spatial_dims.remove(dim_name)
        
        self.component.properties['spatial_dims'] = spatial_dims
        self.load_dimensions()  # Refresh display
        self.on_modified()
    
    def validate_component(self):
        """Validate the component and display results."""
        # Create a temporary system with just this component for validation
        temp_system = SystemModel("temp", "Temporary system for validation")
        temp_system.dimensions = self.system.dimensions.copy()
        temp_system.add_component(self.component)
        
        validation_results = self.informants_manager.validate_system_informants(temp_system)
        
        if validation_results:
            text_lines = ["❌ Component validation found issues:\n"]
            for component_name, errors in validation_results.items():
                for error in errors:
                    text_lines.append(f"• {error}")
        else:
            text_lines = ["✅ Component validation passed!"]
        
        self.validation_text.setPlainText("\n".join(text_lines))
    
    def open_multidimensional_editor(self):
        """Open the multidimensional data editor."""
        try:
            # Use the existing multidimensional editor
            dialog = MultidimensionalEditorDialog(self.component, self.system, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.on_modified()
                self.validate_component()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open multidimensional editor: {e}")
    
    def open_informants_manager(self):
        """Open the informants manager for the system."""
        try:
            dialog = InformantsEditorDialog(self.system, self.project, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Refresh dimensions display
                self.load_dimensions()
                self.validate_component()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open informants manager: {e}")
    
    def on_modified(self):
        """Handle component modifications."""
        self.modified = True
        
        # Update component properties from UI
        self.save_ui_to_component()
        
        # Real-time validation (optional)
        # self.validate_component()
    
    def save_ui_to_component(self):
        """Save UI values to component properties."""
        # Update name
        self.component.name = self.name_edit.text()
        
        # Basic properties
        self.component.properties['units'] = self.units_edit.text()
        self.component.properties['description'] = self.description_edit.toPlainText()
        
        # Type-specific properties
        if self.component.component_type == 'stock':
            initial_value_text = self.initial_value_edit.text()
            try:
                # Try to evaluate as Python literal
                self.component.properties['initial_value'] = eval(initial_value_text) if initial_value_text else 0
            except:
                self.component.properties['initial_value'] = initial_value_text
            
            min_val = self.min_value_edit.text()
            self.component.properties['min_value'] = float(min_val) if min_val else None
            
            max_val = self.max_value_edit.text()
            self.component.properties['max_value'] = float(max_val) if max_val else None
            
        elif self.component.component_type == 'flow':
            rate_text = self.rate_edit.text()
            try:
                self.component.properties['rate'] = float(rate_text) if rate_text else 0
            except:
                self.component.properties['rate'] = rate_text
                
        elif self.component.component_type == 'calculator':
            self.component.properties['expression'] = self.expression_edit.toPlainText()
        
        # Advanced properties
        if hasattr(self, 'parameters_edit'):
            params_text = self.parameters_edit.toPlainText()
            try:
                self.component.properties['parameters'] = eval(params_text) if params_text else {}
            except:
                self.component.properties['parameters'] = {}
        
        if hasattr(self, 'dependencies_edit'):
            deps_text = self.dependencies_edit.toPlainText()
            deps = [line.strip() for line in deps_text.split('\n') if line.strip()]
            self.component.properties['dependencies'] = deps
    
    def save_and_accept(self):
        """Save changes and accept dialog."""
        self.save_ui_to_component()
        
        # Final validation
        self.validate_component()
        
        # Emit signal
        self.component_modified.emit(self.component)
        
        self.accept()
