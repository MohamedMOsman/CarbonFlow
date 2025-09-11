"""
Property Editors for Component Inspector

This module provides specialized editors for different types of component properties.
"""

from PyQt6.QtWidgets import (
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QCheckBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Any, List, Dict, Optional, Union


class PropertyEditorFactory:
    """Factory for creating property editors based on data type."""
    
    def create_editor(self, editor_type: str, value: Any) -> Optional[QWidget]:
        """Create an appropriate editor for the given type and value."""
        
        if editor_type == "text":
            return TextEditor(value)
        elif editor_type == "multiline_text":
            return MultilineTextEditor(value)
        elif editor_type == "spinbox":
            return SpinBoxEditor(value)
        elif editor_type == "double_spinbox":
            return DoubleSpinBoxEditor(value)
        elif editor_type == "checkbox":
            return CheckBoxEditor(value)
        elif editor_type == "combo":
            return ComboBoxEditor(value)
        elif editor_type == "list":
            return ListEditor(value)
        elif editor_type == "dict":
            return DictEditor(value)
        else:
            # Default to text editor
            return TextEditor(str(value))


class TextEditor(QLineEdit):
    """Simple text editor for string properties."""
    
    def __init__(self, value: Any):
        super().__init__()
        self.setText(str(value) if value is not None else "")
        self.setPlaceholderText("Enter text...")


class MultilineTextEditor(QTextEdit):
    """Multiline text editor for longer text properties."""
    
    def __init__(self, value: Any):
        super().__init__()
        self.setPlainText(str(value) if value is not None else "")
        self.setMaximumHeight(100)
        self.setPlaceholderText("Enter text...")


class SpinBoxEditor(QSpinBox):
    """Integer value editor."""
    
    def __init__(self, value: Any):
        super().__init__()
        self.setRange(-999999, 999999)
        try:
            self.setValue(int(value) if value is not None else 0)
        except (ValueError, TypeError):
            self.setValue(0)


class DoubleSpinBoxEditor(QDoubleSpinBox):
    """Float value editor."""
    
    def __init__(self, value: Any):
        super().__init__()
        self.setRange(-999999.0, 999999.0)
        self.setDecimals(6)
        try:
            self.setValue(float(value) if value is not None else 0.0)
        except (ValueError, TypeError):
            self.setValue(0.0)


class CheckBoxEditor(QCheckBox):
    """Boolean value editor."""
    
    def __init__(self, value: Any):
        super().__init__()
        try:
            self.setChecked(bool(value) if value is not None else False)
        except (ValueError, TypeError):
            self.setChecked(False)


class ComboBoxEditor(QComboBox):
    """Dropdown selection editor."""
    
    def __init__(self, value: Any, options: List[str] = None):
        super().__init__()
        
        if options:
            self.addItems(options)
            if value in options:
                self.setCurrentText(str(value))
        else:
            # If no options provided, make it editable
            self.setEditable(True)
            self.setCurrentText(str(value) if value is not None else "")


class ListEditor(QWidget):
    """Editor for list properties."""
    
    # Signal emitted when list changes
    listChanged = pyqtSignal()
    
    def __init__(self, value: List[Any]):
        super().__init__()
        
        self.setup_ui()
        self.set_value(value if value is not None else [])
        
    def setup_ui(self):
        """Set up the list editor UI."""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(120)
        layout.addWidget(self.list_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_item)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_item)
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_item)
        
        controls_layout.addWidget(self.add_btn)
        controls_layout.addWidget(self.remove_btn)
        controls_layout.addWidget(self.edit_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
    def set_value(self, value: List[Any]):
        """Set the list value."""
        
        self.list_widget.clear()
        for item in value:
            list_item = QListWidgetItem(str(item))
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.list_widget.addItem(list_item)
            
    def get_value(self) -> List[Any]:
        """Get the current list value."""
        
        result = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            result.append(item.data(Qt.ItemDataRole.UserRole))
        return result
        
    def add_item(self):
        """Add a new item to the list."""
        
        # Simple text input for now
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Add Item", "Enter value:")
        
        if ok and text:
            list_item = QListWidgetItem(text)
            list_item.setData(Qt.ItemDataRole.UserRole, text)
            self.list_widget.addItem(list_item)
            self.listChanged.emit()
            
    def remove_item(self):
        """Remove selected item from the list."""
        
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.takeItem(current_row)
            self.listChanged.emit()
            
    def edit_item(self):
        """Edit selected item."""
        
        current_item = self.list_widget.currentItem()
        if current_item:
            from PyQt6.QtWidgets import QInputDialog
            current_value = current_item.data(Qt.ItemDataRole.UserRole)
            text, ok = QInputDialog.getText(self, "Edit Item", "Enter value:", text=str(current_value))
            
            if ok:
                current_item.setText(text)
                current_item.setData(Qt.ItemDataRole.UserRole, text)
                self.listChanged.emit()


class DictEditor(QWidget):
    """Editor for dictionary properties."""
    
    # Signal emitted when dictionary changes
    dictChanged = pyqtSignal()
    
    def __init__(self, value: Dict[str, Any]):
        super().__init__()
        
        self.setup_ui()
        self.set_value(value if value is not None else {})
        
    def setup_ui(self):
        """Set up the dictionary editor UI."""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Key", "Value"])
        self.table_widget.setMaximumHeight(120)
        
        # Resize columns
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_item)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_item)
        
        controls_layout.addWidget(self.add_btn)
        controls_layout.addWidget(self.remove_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
    def set_value(self, value: Dict[str, Any]):
        """Set the dictionary value."""
        
        self.table_widget.setRowCount(len(value))
        
        for i, (key, val) in enumerate(value.items()):
            key_item = QTableWidgetItem(str(key))
            value_item = QTableWidgetItem(str(val))
            
            # Store original values
            key_item.setData(Qt.ItemDataRole.UserRole, key)
            value_item.setData(Qt.ItemDataRole.UserRole, val)
            
            self.table_widget.setItem(i, 0, key_item)
            self.table_widget.setItem(i, 1, value_item)
            
    def get_value(self) -> Dict[str, Any]:
        """Get the current dictionary value."""
        
        result = {}
        for i in range(self.table_widget.rowCount()):
            key_item = self.table_widget.item(i, 0)
            value_item = self.table_widget.item(i, 1)
            
            if key_item and value_item:
                key = key_item.data(Qt.ItemDataRole.UserRole)
                value = value_item.data(Qt.ItemDataRole.UserRole)
                result[key] = value
                
        return result
        
    def add_item(self):
        """Add a new key-value pair."""
        
        from PyQt6.QtWidgets import QInputDialog
        
        # Get key
        key, ok1 = QInputDialog.getText(self, "Add Item", "Enter key:")
        if not ok1 or not key:
            return
            
        # Get value
        value, ok2 = QInputDialog.getText(self, "Add Item", "Enter value:")
        if not ok2:
            return
            
        # Add to table
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)
        
        key_item = QTableWidgetItem(key)
        value_item = QTableWidgetItem(value)
        
        key_item.setData(Qt.ItemDataRole.UserRole, key)
        value_item.setData(Qt.ItemDataRole.UserRole, value)
        
        self.table_widget.setItem(row, 0, key_item)
        self.table_widget.setItem(row, 1, value_item)
        
        self.dictChanged.emit()
        
    def remove_item(self):
        """Remove selected key-value pair."""
        
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            self.table_widget.removeRow(current_row)
            self.dictChanged.emit()


class DimensionalDataEditor(QWidget):
    """Specialized editor for multidimensional data."""
    
    def __init__(self, value: Any, dimensions: List[str], dimension_info: Dict[str, Any]):
        super().__init__()
        
        self.dimensions = dimensions
        self.dimension_info = dimension_info
        
        self.setup_ui()
        self.set_value(value)
        
    def setup_ui(self):
        """Set up the dimensional data editor UI."""
        
        layout = QVBoxLayout(self)
        
        # Dimension info
        info_label = QLabel(f"Dimensions: {', '.join(self.dimensions)}")
        info_label.setFont(QFont("Arial", 9))
        layout.addWidget(info_label)
        
        # Data table
        self.data_table = QTableWidget()
        layout.addWidget(self.data_table)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_display)
        
        controls_layout.addWidget(self.refresh_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
    def set_value(self, value: Any):
        """Set the dimensional data value."""
        
        # TODO: Implement proper multidimensional data display
        # This would require parsing the dimensional structure and
        # displaying it in a meaningful tabular format
        
        if hasattr(value, 'shape') and hasattr(value, 'ndim'):
            # NumPy array
            self.display_numpy_array(value)
        elif isinstance(value, list):
            # List data
            self.display_list_data(value)
        else:
            # Scalar or other
            self.display_scalar_data(value)
            
    def display_numpy_array(self, array):
        """Display NumPy array data."""
        
        if array.ndim == 1:
            # 1D array - single column
            self.data_table.setRowCount(len(array))
            self.data_table.setColumnCount(1)
            self.data_table.setHorizontalHeaderLabels(["Value"])
            
            for i, val in enumerate(array):
                item = QTableWidgetItem(str(val))
                self.data_table.setItem(i, 0, item)
                
        elif array.ndim == 2:
            # 2D array - matrix
            rows, cols = array.shape
            self.data_table.setRowCount(rows)
            self.data_table.setColumnCount(cols)
            
            for i in range(rows):
                for j in range(cols):
                    item = QTableWidgetItem(str(array[i, j]))
                    self.data_table.setItem(i, j, item)
                    
        else:
            # Higher dimensions - flatten for display
            flat_array = array.flatten()
            self.display_numpy_array(flat_array)
            
    def display_list_data(self, data):
        """Display list data."""
        
        if not data:
            return
            
        # Check if nested list
        if isinstance(data[0], list):
            # 2D list
            self.data_table.setRowCount(len(data))
            self.data_table.setColumnCount(len(data[0]) if data else 0)
            
            for i, row in enumerate(data):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    self.data_table.setItem(i, j, item)
        else:
            # 1D list
            self.data_table.setRowCount(len(data))
            self.data_table.setColumnCount(1)
            self.data_table.setHorizontalHeaderLabels(["Value"])
            
            for i, val in enumerate(data):
                item = QTableWidgetItem(str(val))
                self.data_table.setItem(i, 0, item)
                
    def display_scalar_data(self, data):
        """Display scalar data."""
        
        self.data_table.setRowCount(1)
        self.data_table.setColumnCount(1)
        self.data_table.setHorizontalHeaderLabels(["Value"])
        
        item = QTableWidgetItem(str(data))
        self.data_table.setItem(0, 0, item)
        
    def refresh_display(self):
        """Refresh the data display."""
        # TODO: Implement refresh functionality
        pass
