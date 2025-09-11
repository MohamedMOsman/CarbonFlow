#!/usr/bin/env python3
"""
Simple Enhanced Main Window

A simplified version that adds basic project management features
to the existing GUI without complex dependencies.
"""

import sys
from pathlib import Path

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'sd_toolkit'))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTreeWidget, QTreeWidgetItem, QMessageBox, QFileDialog,
    QInputDialog, QMenu, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

# Import existing GUI components
from yaml_integration.yaml_loader import YAMLModelLoader, GuiModel
from yaml_integration.yaml_saver import YAMLModelSaver
from canvas.model_canvas import ModelCanvas
from components.palette import ComponentPalette
from inspector.component_inspector import ComponentInspector
from simulation.simulation_controller import SimulationController


class SimpleProjectTreeWidget(QWidget):
    """Simple project tree widget with basic functionality."""
    
    project_selected = pyqtSignal(str)  # project_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the simple project tree UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Project Explorer")
        header.setStyleSheet("QLabel { font-weight: bold; font-size: 12px; margin: 5px; }")
        layout.addWidget(header)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Projects & Models")
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.tree)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.create_project)
        buttons_layout.addWidget(new_project_btn)
        
        load_model_btn = QPushButton("Load Model")
        load_model_btn.clicked.connect(self.load_model)
        buttons_layout.addWidget(load_model_btn)
        
        layout.addLayout(buttons_layout)
        
        # Add some sample projects
        self.add_sample_projects()
    
    def add_sample_projects(self):
        """Add some sample projects to demonstrate the tree."""
        # Sample Project 1
        project1 = QTreeWidgetItem(self.tree)
        project1.setText(0, "Climate Adaptation Study")
        project1.setData(0, Qt.ItemDataRole.UserRole, {"type": "project", "name": "Climate Adaptation Study"})
        
        system1 = QTreeWidgetItem(project1)
        system1.setText(0, "Population Dynamics")
        system1.setData(0, Qt.ItemDataRole.UserRole, {"type": "system", "name": "Population Dynamics"})
        
        system2 = QTreeWidgetItem(project1)
        system2.setText(0, "Flood Protection")
        system2.setData(0, Qt.ItemDataRole.UserRole, {"type": "system", "name": "Flood Protection"})
        
        # Sample Project 2
        project2 = QTreeWidgetItem(self.tree)
        project2.setText(0, "Urban Planning Model")
        project2.setData(0, Qt.ItemDataRole.UserRole, {"type": "project", "name": "Urban Planning Model"})
        
        system3 = QTreeWidgetItem(project2)
        system3.setText(0, "Transportation System")
        system3.setData(0, Qt.ItemDataRole.UserRole, {"type": "system", "name": "Transportation System"})
        
        # Expand all items
        self.tree.expandAll()
    
    def create_project(self):
        """Create a new project."""
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if ok and name:
            project_item = QTreeWidgetItem(self.tree)
            project_item.setText(0, name)
            project_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "project", "name": name})
            
            # Add a default system
            system_item = QTreeWidgetItem(project_item)
            system_item.setText(0, "Main System")
            system_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "system", "name": "Main System"})
            
            project_item.setExpanded(True)
            QMessageBox.information(self, "Success", f"Project '{name}' created!")
    
    def load_model(self):
        """Load a YAML model file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open YAML Model", "", "YAML Files (*.yaml *.yml)"
        )
        if file_path:
            model_name = Path(file_path).stem
            model_item = QTreeWidgetItem(self.tree)
            model_item.setText(0, f"📄 {model_name}")
            model_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "model", "name": model_name, "path": file_path})
            QMessageBox.information(self, "Success", f"Model '{model_name}' added to tree!")
    
    def show_context_menu(self, position):
        """Show context menu for tree items."""
        item = self.tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if data and data.get("type") == "project":
            menu.addAction("Add System", lambda: self.add_system(item))
            menu.addAction("Remove Project", lambda: self.remove_item(item))
        elif data and data.get("type") == "system":
            menu.addAction("Remove System", lambda: self.remove_item(item))
        elif data and data.get("type") == "model":
            menu.addAction("Load Model", lambda: self.load_model_file(data.get("path")))
            menu.addAction("Remove Model", lambda: self.remove_item(item))
        
        if menu.actions():
            menu.exec(self.tree.mapToGlobal(position))
    
    def add_system(self, project_item):
        """Add a system to a project."""
        name, ok = QInputDialog.getText(self, "New System", "System name:")
        if ok and name:
            system_item = QTreeWidgetItem(project_item)
            system_item.setText(0, name)
            system_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "system", "name": name})
            project_item.setExpanded(True)
    
    def remove_item(self, item):
        """Remove an item from the tree."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        name = data.get("name", "Unknown") if data else "Unknown"
        
        reply = QMessageBox.question(
            self, "Confirm Removal", 
            f"Remove '{name}'?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
    
    def load_model_file(self, file_path):
        """Signal to load a model file."""
        if file_path:
            self.project_selected.emit(file_path)


class SimpleEnhancedMainWindow(QMainWindow):
    """Enhanced main window with simple project management."""
    
    def __init__(self):
        super().__init__()
        
        # Window properties
        self.setWindowTitle("System Dynamics Modeler - Enhanced")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Initialize components
        self.current_gui_model = None
        self.current_sd_model = None
        self.current_model_path = None
        self.simulation_results = None
        
        # Initialize YAML integration
        self.yaml_loader = YAMLModelLoader()
        self.yaml_saver = YAMLModelSaver()
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_connections()
        
        self.statusBar().showMessage("Enhanced System Dynamics Modeler Ready")
    
    def setup_ui(self):
        """Set up the enhanced user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitters
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel: Project tree
        self.project_tree = SimpleProjectTreeWidget()
        main_splitter.addWidget(self.project_tree)
        
        # Center panel: Canvas
        self.model_canvas = ModelCanvas()
        main_splitter.addWidget(self.model_canvas)
        
        # Right panel: Palette and Inspector
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.component_palette = ComponentPalette()
        right_layout.addWidget(self.component_palette)
        
        self.component_inspector = ComponentInspector()
        right_layout.addWidget(self.component_inspector)
        
        main_splitter.addWidget(right_widget)
        
        # Set splitter proportions
        main_splitter.setSizes([300, 800, 300])
        
        # Create simulation controller
        self.simulation_controller = SimulationController()
    
    def setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_project_action = QAction("New &Project", self)
        new_project_action.setShortcut("Ctrl+Shift+N")
        new_project_action.triggered.connect(self.project_tree.create_project)
        file_menu.addAction(new_project_action)
        
        load_model_action = QAction("&Load Model", self)
        load_model_action.setShortcut("Ctrl+O")
        load_model_action.triggered.connect(self.project_tree.load_model)
        file_menu.addAction(load_model_action)
        
        file_menu.addSeparator()
        
        new_model_action = QAction("&New Model", self)
        new_model_action.setShortcut("Ctrl+N")
        new_model_action.triggered.connect(self.new_model)
        file_menu.addAction(new_model_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.statusBar().showMessage("Ready")
    
    def setup_connections(self):
        """Set up signal connections."""
        self.project_tree.project_selected.connect(self.load_model_from_path)
        
        if self.model_canvas:
            self.model_canvas.component_selected.connect(self.on_component_selected)
            self.model_canvas.model_modified.connect(self.on_model_modified)
    
    def new_model(self):
        """Create a new model."""
        try:
            self.current_gui_model = GuiModel("New Model", "A new system dynamics model")
            self.current_sd_model = None
            
            if self.component_palette:
                self.component_palette.setEnabled(True)
            
            self.statusBar().showMessage("New model created")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create new model: {e}")
    
    def load_model_from_path(self, file_path):
        """Load a model from file path."""
        try:
            self.statusBar().showMessage(f"Loading model from {file_path}...")
            
            gui_model, sd_model = self.yaml_loader.load_model_from_file(file_path)
            self.current_gui_model = gui_model
            self.current_sd_model = sd_model
            self.current_model_path = file_path
            
            if self.model_canvas:
                self.model_canvas.load_model(gui_model)
            
            if self.component_inspector:
                self.component_inspector.set_model(gui_model)
            
            self.statusBar().showMessage(f"Loaded model: {gui_model.name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load model: {e}")
            self.statusBar().showMessage("Failed to load model")
    
    def on_component_selected(self, component):
        """Handle component selection."""
        if self.component_inspector:
            self.component_inspector.set_current_component(component)
    
    def on_model_modified(self):
        """Handle model modification."""
        self.statusBar().showMessage("Model modified")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About", 
            "Enhanced System Dynamics Modeler\n\n"
            "Features:\n"
            "• Hierarchical project organization\n"
            "• Multi-system support\n"
            "• Enhanced component management\n"
            "• Backward compatibility\n\n"
            "Version 1.0"
        )


def main():
    """Main function."""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced System Dynamics Modeler")
    
    # Create and show main window
    main_window = SimpleEnhancedMainWindow()
    main_window.show()
    
    # Show welcome message
    QMessageBox.information(
        main_window,
        "Enhanced GUI",
        "Welcome to the Enhanced System Dynamics Modeler!\n\n"
        "New features:\n"
        "• Project tree on the left with sample projects\n"
        "• Right-click context menus\n"
        "• Create new projects and systems\n"
        "• Load YAML models into the tree\n"
        "• All existing functionality preserved\n\n"
        "Try right-clicking items in the project tree!"
    )
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
