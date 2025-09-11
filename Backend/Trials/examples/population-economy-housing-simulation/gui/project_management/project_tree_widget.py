"""
Project Tree Widget

Provides a QTreeWidget-based hierarchical view of projects, systems, and components
with support for drag-and-drop, context menus, and in-place editing.
"""

from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QInputDialog,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QIcon, QDrag, QAction

from typing import Dict, List, Optional, Any
import json

from .project_manager import ProjectManager, Project, SystemModel
from .component_manager import ComponentManager
from .informants_manager import InformantsManager
from ..yaml_integration.yaml_loader import ModelComponent


class ProjectTreeItem(QTreeWidgetItem):
    """Custom tree item with additional metadata and functionality."""
    
    def __init__(self, parent=None, item_type: str = "unknown", data: Any = None):
        super().__init__(parent)
        self.item_type = item_type  # project, system, category, component, informant
        self.item_data = data
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)
    
    def get_full_path(self) -> List[str]:
        """Get the full path from root to this item."""
        path = []
        item = self
        while item:
            path.insert(0, item.text(0))
            item = item.parent()
        return path


class ProjectTreeWidget(QWidget):
    """
    Hierarchical tree view for project management.
    
    Displays projects, systems, and components in a tree structure with:
    - Expandable nodes for projects and systems
    - Component categories (Stocks, Flows, Calculators, Informants)
    - Context menus for operations
    - Drag-and-drop support
    - In-place editing capabilities
    """
    
    # Signals
    project_selected = pyqtSignal(object)  # Project
    system_selected = pyqtSignal(object, object)  # Project, SystemModel
    component_selected = pyqtSignal(object, object, object)  # Project, SystemModel, ModelComponent
    item_renamed = pyqtSignal(str, str, str)  # item_type, old_name, new_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.project_manager = ProjectManager()
        self.component_manager = ComponentManager()
        self.informants_manager = InformantsManager()
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Project Explorer")
        header_label.setStyleSheet("QLabel { font-weight: bold; font-size: 12px; }")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Action buttons
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.create_new_project)
        header_layout.addWidget(new_project_btn)
        
        layout.addLayout(header_layout)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Projects")
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        
        layout.addWidget(self.tree)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemChanged.connect(self.on_item_renamed)
    
    def load_project(self, project_path: str):
        """Load a project into the tree view."""
        try:
            project = self.project_manager.load_project(project_path)
            self.add_project_to_tree(project)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project: {e}")
    
    def add_project_to_tree(self, project: Project):
        """Add a project and its contents to the tree."""
        # Create project item
        project_item = ProjectTreeItem(self.tree, "project", project)
        project_item.setText(0, project.name)
        project_item.setToolTip(0, project.description)
        
        # Add systems
        for system in project.systems.values():
            self.add_system_to_tree(system, project_item, project)
        
        # Expand project by default
        project_item.setExpanded(True)
    
    def add_system_to_tree(self, system: SystemModel, project_item: ProjectTreeItem, project: Project):
        """Add a system and its components to the tree."""
        # Create system item
        system_item = ProjectTreeItem(project_item, "system", system)
        system_item.setText(0, system.name)
        system_item.setToolTip(0, system.description)
        
        # Add component categories
        self.add_component_category(system_item, "Stocks", system.stocks, project, system)
        self.add_component_category(system_item, "Flows", system.flows, project, system)
        self.add_component_category(system_item, "Calculators", system.calculators, project, system)
        
        # Add informants category
        informants_item = ProjectTreeItem(system_item, "category", "informants")
        informants_item.setText(0, "Informants")
        informants_item.setToolTip(0, "Dimensional data and informants")
        
        # Expand system by default
        system_item.setExpanded(True)
    
    def add_component_category(self, system_item: ProjectTreeItem, category_name: str, 
                             components: Dict[str, ModelComponent], project: Project, system: SystemModel):
        """Add a component category with its components."""
        category_item = ProjectTreeItem(system_item, "category", category_name.lower())
        category_item.setText(0, category_name)
        category_item.setToolTip(0, f"{category_name} components")
        
        # Add individual components
        for component in components.values():
            component_item = ProjectTreeItem(category_item, "component", component)
            component_item.setText(0, component.name)
            
            # Create tooltip with component details
            tooltip_lines = [
                f"Type: {component.component_type}",
                f"Description: {component.properties.get('description', 'No description')}"
            ]
            
            if 'spatial_dims' in component.properties:
                spatial_dims = component.properties['spatial_dims']
                if spatial_dims:
                    tooltip_lines.append(f"Dimensions: {', '.join(spatial_dims)}")
            
            if 'units' in component.properties:
                tooltip_lines.append(f"Units: {component.properties['units']}")
            
            component_item.setToolTip(0, "\n".join(tooltip_lines))
        
        # Show component count
        count = len(components)
        category_item.setText(0, f"{category_name} ({count})")
    
    def create_new_project(self):
        """Create a new project through dialog."""
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if ok and name:
            description, ok = QInputDialog.getText(self, "New Project", "Project description (optional):")
            if ok:
                try:
                    project = self.project_manager.create_project(name, description)
                    self.add_project_to_tree(project)
                    QMessageBox.information(self, "Success", f"Project '{name}' created successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
    
    def create_new_system(self, project: Project):
        """Create a new system in the given project."""
        name, ok = QInputDialog.getText(self, "New System", "System name:")
        if ok and name:
            description, ok = QInputDialog.getText(self, "New System", "System description (optional):")
            if ok:
                try:
                    system = SystemModel(name=name, description=description)
                    project.add_system(system)
                    
                    # Save project
                    self.project_manager.save_project(project)
                    
                    # Refresh tree
                    self.refresh_project_in_tree(project)
                    
                    QMessageBox.information(self, "Success", f"System '{name}' created successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create system: {e}")
    
    def on_item_clicked(self, item: ProjectTreeItem, column: int):
        """Handle item click events."""
        if item.item_type == "project":
            self.project_selected.emit(item.item_data)
        elif item.item_type == "system":
            project = self.get_project_for_item(item)
            self.system_selected.emit(project, item.item_data)
        elif item.item_type == "component":
            project = self.get_project_for_item(item)
            system = self.get_system_for_item(item)
            self.component_selected.emit(project, system, item.item_data)
    
    def on_item_double_clicked(self, item: ProjectTreeItem, column: int):
        """Handle item double-click events."""
        if item.item_type == "component":
            # Open component editor
            project = self.get_project_for_item(item)
            system = self.get_system_for_item(item)
            component = item.item_data
            
            # This would open the multidimensional editor
            # For now, just show a message
            QMessageBox.information(self, "Component Editor", 
                                  f"Opening editor for {component.name}\n"
                                  f"Type: {component.component_type}\n"
                                  f"System: {system.name}\n"
                                  f"Project: {project.name}")
    
    def show_context_menu(self, position):
        """Show context menu for tree items."""
        item = self.tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        if item.item_type == "project":
            menu.addAction("New System", lambda: self.create_new_system(item.item_data))
            menu.addAction("Save Project", lambda: self.save_project(item.item_data))
            menu.addSeparator()
            menu.addAction("Remove Project", lambda: self.remove_project(item.item_data))
        
        elif item.item_type == "system":
            project = self.get_project_for_item(item)
            menu.addAction("New Component", lambda: self.create_new_component(project, item.item_data))
            menu.addAction("Save System", lambda: self.save_system(project, item.item_data))
            menu.addSeparator()
            menu.addAction("Remove System", lambda: self.remove_system(project, item.item_data))
        
        elif item.item_type == "component":
            menu.addAction("Edit Component", lambda: self.edit_component(item))
            menu.addAction("Duplicate Component", lambda: self.duplicate_component(item))
            menu.addSeparator()
            menu.addAction("Remove Component", lambda: self.remove_component(item))
        
        elif item.item_type == "category":
            if item.item_data == "informants":
                menu.addAction("Manage Informants", lambda: self.manage_informants(item))
            else:
                project = self.get_project_for_item(item)
                system = self.get_system_for_item(item)
                component_type = item.item_data.rstrip('s')  # Remove 's' from category name
                menu.addAction(f"New {component_type.title()}", 
                             lambda: self.create_new_component(project, system, component_type))
        
        if menu.actions():
            menu.exec(self.tree.mapToGlobal(position))
    
    def on_item_renamed(self, item: ProjectTreeItem, column: int):
        """Handle item rename events."""
        if item.item_type in ["project", "system", "component"]:
            old_name = getattr(item.item_data, 'name', '')
            new_name = item.text(0)
            
            if old_name != new_name and new_name:
                # Update the data object
                if hasattr(item.item_data, 'name'):
                    item.item_data.name = new_name
                
                # Emit signal
                self.item_renamed.emit(item.item_type, old_name, new_name)
    
    def get_project_for_item(self, item: ProjectTreeItem) -> Optional[Project]:
        """Get the project that contains the given item."""
        while item:
            if item.item_type == "project":
                return item.item_data
            item = item.parent()
        return None
    
    def get_system_for_item(self, item: ProjectTreeItem) -> Optional[SystemModel]:
        """Get the system that contains the given item."""
        while item:
            if item.item_type == "system":
                return item.item_data
            item = item.parent()
        return None
    
    def refresh_project_in_tree(self, project: Project):
        """Refresh a project's display in the tree."""
        # Find and remove existing project item
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.item_type == "project" and item.item_data.name == project.name:
                self.tree.takeTopLevelItem(i)
                break
        
        # Add updated project
        self.add_project_to_tree(project)
    
    # Placeholder methods for future implementation
    def save_project(self, project: Project):
        """Save project to disk."""
        try:
            self.project_manager.save_project(project)
            QMessageBox.information(self, "Success", f"Project '{project.name}' saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {e}")
    
    def save_system(self, project: Project, system: SystemModel):
        """Save system to disk."""
        try:
            self.component_manager.save_system(system, project)
            QMessageBox.information(self, "Success", f"System '{system.name}' saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save system: {e}")
    
    def create_new_component(self, project: Project, system: SystemModel, component_type: str = "stock"):
        """Create a new component in the system."""
        # This would open a component creation dialog
        QMessageBox.information(self, "Create Component", 
                              f"Creating new {component_type} in {system.name}")
    
    def edit_component(self, item: ProjectTreeItem):
        """Edit the selected component."""
        # This would open the multidimensional editor
        QMessageBox.information(self, "Edit Component", f"Editing {item.item_data.name}")
    
    def manage_informants(self, item: ProjectTreeItem):
        """Manage informants for the system."""
        system = self.get_system_for_item(item)
        QMessageBox.information(self, "Manage Informants", f"Managing informants for {system.name}")
    
    def remove_project(self, project: Project):
        """Remove project (with confirmation)."""
        reply = QMessageBox.question(self, "Confirm Removal", 
                                   f"Remove project '{project.name}'?\nThis cannot be undone.")
        if reply == QMessageBox.StandardButton.Yes:
            # Implementation would remove from disk and tree
            QMessageBox.information(self, "Removed", f"Project '{project.name}' removed")
    
    def remove_system(self, project: Project, system: SystemModel):
        """Remove system (with confirmation)."""
        reply = QMessageBox.question(self, "Confirm Removal", 
                                   f"Remove system '{system.name}'?\nThis cannot be undone.")
        if reply == QMessageBox.StandardButton.Yes:
            # Implementation would remove from project and disk
            QMessageBox.information(self, "Removed", f"System '{system.name}' removed")
    
    def remove_component(self, item: ProjectTreeItem):
        """Remove component (with confirmation)."""
        component = item.item_data
        reply = QMessageBox.question(self, "Confirm Removal", 
                                   f"Remove component '{component.name}'?\nThis cannot be undone.")
        if reply == QMessageBox.StandardButton.Yes:
            # Implementation would remove from system
            QMessageBox.information(self, "Removed", f"Component '{component.name}' removed")
    
    def duplicate_component(self, item: ProjectTreeItem):
        """Duplicate the selected component."""
        component = item.item_data
        QMessageBox.information(self, "Duplicate Component", f"Duplicating {component.name}")
