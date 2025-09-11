"""
Main Window for System Dynamics GUI Application

This module provides the primary application window with:
- Menu bar and toolbar
- Docked panels for component palette and inspector
- Central canvas for visual model editing
- Status bar for application feedback
"""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QToolBar, QStatusBar, QDockWidget,
    QMessageBox, QFileDialog, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QIcon

# Import GUI components
from yaml_integration.yaml_loader import YAMLModelLoader, GuiModel
from yaml_integration.yaml_saver import YAMLModelSaver
from canvas.model_canvas import ModelCanvas
from components.palette import ComponentPalette
from inspector.component_inspector import ComponentInspector
from simulation.simulation_controller import SimulationController

# Simple project management without external dependencies
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QInputDialog, QMenu, QLabel, QPushButton
import json
from pathlib import Path

PROJECT_MANAGEMENT_AVAILABLE = True  # Always available with simple implementation


class SimpleProjectTreeWidget(QWidget):
    """Simple project tree widget with basic functionality."""

    project_selected = pyqtSignal(str)  # project_name
    system_selected = pyqtSignal(str, str)  # project_name, system_name
    component_selected = pyqtSignal(str, str, str)  # project_name, system_name, component_name

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
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)

        # Buttons
        buttons_layout = QHBoxLayout()

        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.create_new_project)
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
        project1.setText(0, "🏗️ Climate Adaptation Study")
        project1.setData(0, Qt.ItemDataRole.UserRole, {"type": "project", "name": "Climate Adaptation Study"})

        system1 = QTreeWidgetItem(project1)
        system1.setText(0, "📊 Population Dynamics")
        system1.setData(0, Qt.ItemDataRole.UserRole, {"type": "system", "name": "Population Dynamics"})

        system2 = QTreeWidgetItem(project1)
        system2.setText(0, "🌊 Flood Protection")
        system2.setData(0, Qt.ItemDataRole.UserRole, {"type": "system", "name": "Flood Protection"})

        # Sample Project 2
        project2 = QTreeWidgetItem(self.tree)
        project2.setText(0, "🏙️ Urban Planning Model")
        project2.setData(0, Qt.ItemDataRole.UserRole, {"type": "project", "name": "Urban Planning Model"})

        system3 = QTreeWidgetItem(project2)
        system3.setText(0, "🚌 Transportation System")
        system3.setData(0, Qt.ItemDataRole.UserRole, {"type": "system", "name": "Transportation System"})

        # Expand all items
        self.tree.expandAll()

    def create_new_project(self):
        """Create a new project."""
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if ok and name:
            project_item = QTreeWidgetItem(self.tree)
            project_item.setText(0, f"🏗️ {name}")
            project_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "project", "name": name})

            # Add a default system
            system_item = QTreeWidgetItem(project_item)
            system_item.setText(0, "📊 Main System")
            system_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "system", "name": "Main System"})

            project_item.setExpanded(True)

            # Automatically select the new system and create a model for it
            self.tree.setCurrentItem(system_item)
            self.on_item_clicked(system_item, 0)

            QMessageBox.information(self, "Success", f"Project '{name}' created!\nThe Main System is now active and ready for modeling.")

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

            # Emit signal to load the model
            self.project_selected.emit(file_path)

    def on_item_clicked(self, item, column):
        """Handle item clicks."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")
        if item_type == "project":
            self.project_selected.emit(data.get("name", ""))
        elif item_type == "system":
            project_item = item.parent()
            if project_item:
                project_data = project_item.data(0, Qt.ItemDataRole.UserRole)
                project_name = project_data.get("name", "") if project_data else ""
                system_name = data.get("name", "")
                # Emit the signal which will be handled by the main window
                self.system_selected.emit(project_name, system_name)
        elif item_type == "model":
            # Load model file
            file_path = data.get("path")
            if file_path:
                self.project_selected.emit(file_path)

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
            system_item.setText(0, f"📊 {name}")
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


class SystemDynamicsMainWindow(QMainWindow):
    """Main application window for the System Dynamics GUI."""
    
    # Signals
    model_loaded = pyqtSignal(object)  # Emitted when a model is loaded
    simulation_started = pyqtSignal()
    simulation_finished = pyqtSignal(object)  # Emitted with results
    
    def __init__(self):
        super().__init__()
        
        # Window properties
        self.setWindowTitle("System Dynamics Modeler")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # Initialize components
        self.current_gui_model = None  # GUI representation
        self.current_sd_model = None   # sd_toolkit model for simulation
        self.current_model_path = None
        self.current_scenario_path = None
        self.simulation_results = None

        # Initialize YAML integration
        self.yaml_loader = YAMLModelLoader()
        self.yaml_saver = YAMLModelSaver()

        # Initialize project management (simple implementation)
        if PROJECT_MANAGEMENT_AVAILABLE:
            self.current_project = None
            self.current_system = None
        else:
            self.current_project = None
            self.current_system = None

        # Initialize components (will be created in setup_ui)
        self.model_canvas = None
        self.component_palette = None
        self.component_inspector = None
        self.simulation_controller = None
        self.project_tree = None  # New project tree widget
        
        # Set up UI
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_status_bar()
        
        # Initialize with default state
        self.update_window_title()
        
    def setup_ui(self):
        """Set up the main user interface layout."""

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create splitter for resizable panels
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        # Add project tree if project management is available
        if PROJECT_MANAGEMENT_AVAILABLE:
            self.project_tree = SimpleProjectTreeWidget()
            main_splitter.addWidget(self.project_tree)

            # Connect project tree signals
            self.project_tree.project_selected.connect(self.on_project_selected)
            self.project_tree.system_selected.connect(self.on_system_selected)
            self.project_tree.component_selected.connect(self.on_component_selected_from_tree)

        # Create model canvas
        self.model_canvas = ModelCanvas()
        main_splitter.addWidget(self.model_canvas)

        # Connect canvas signals
        self.model_canvas.component_selected.connect(self.on_component_selected)
        self.model_canvas.model_modified.connect(self.on_model_modified)

        # Set splitter proportions based on whether project tree is present
        if PROJECT_MANAGEMENT_AVAILABLE:
            main_splitter.setSizes([250, 800, 200])  # project_tree, canvas, inspector
        else:
            main_splitter.setSizes([800, 200])  # canvas, inspector
        
        # Create docked panels
        self.setup_docked_panels()
        
    def setup_docked_panels(self):
        """Set up docked panels for component palette and inspector."""
        
        # Component Palette (left dock)
        palette_dock = QDockWidget("Component Palette", self)
        palette_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                   Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Create component palette
        self.component_palette = ComponentPalette()
        palette_dock.setWidget(self.component_palette)
        
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, palette_dock)
        
        # Component Inspector (right dock)
        inspector_dock = QDockWidget("Component Inspector", self)
        inspector_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                     Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Create component inspector
        self.component_inspector = ComponentInspector()
        inspector_dock.setWidget(self.component_inspector)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, inspector_dock)

        # Create simulation controller
        self.simulation_controller = SimulationController()

        # Connect component signals after they are created
        self.setup_connections()

    def setup_connections(self):
        """Set up signal connections between components."""

        # Connect inspector signals
        if self.component_inspector:
            self.component_inspector.component_modified.connect(self.on_component_modified_by_inspector)
            self.component_inspector.property_changed.connect(self.on_property_changed)

        # Connect simulation controller signals
        if self.simulation_controller:
            self.simulation_controller.simulation_started.connect(self.on_simulation_started)
            self.simulation_controller.simulation_finished.connect(self.on_simulation_finished)
            self.simulation_controller.simulation_error.connect(self.on_simulation_error)
            self.simulation_controller.progress_updated.connect(self.on_simulation_progress)

    def setup_menus(self):
        """Set up the application menu bar."""
        
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")

        # Project management actions (if available)
        if PROJECT_MANAGEMENT_AVAILABLE:
            new_project_action = QAction("New &Project", self)
            new_project_action.setShortcut("Ctrl+Shift+N")
            new_project_action.setStatusTip("Create a new project with hierarchical organization")
            new_project_action.triggered.connect(self.new_project)
            file_menu.addAction(new_project_action)

            open_project_action = QAction("Open &Project", self)
            open_project_action.setShortcut("Ctrl+Shift+O")
            open_project_action.setStatusTip("Open an existing project")
            open_project_action.triggered.connect(self.open_project)
            file_menu.addAction(open_project_action)

            file_menu.addSeparator()

        # New Model
        new_action = QAction("&New Model", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Create a new system dynamics model")
        new_action.triggered.connect(self.new_model)
        file_menu.addAction(new_action)
        
        # Open Model
        open_action = QAction("&Open Model...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open an existing YAML model file")
        open_action.triggered.connect(self.open_model)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Save Model
        save_action = QAction("&Save Model", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("Save the current model")
        save_action.triggered.connect(self.save_model)
        file_menu.addAction(save_action)
        
        # Save As
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("Save the model with a new name")
        save_as_action.triggered.connect(self.save_model_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Simulation Menu
        sim_menu = menubar.addMenu("&Simulation")
        
        # Run Simulation
        run_action = QAction("&Run Simulation", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.setStatusTip("Run the current model simulation")
        run_action.triggered.connect(self.run_simulation)
        sim_menu.addAction(run_action)
        
        # Stop Simulation
        stop_action = QAction("&Stop Simulation", self)
        stop_action.setShortcut(QKeySequence("Ctrl+F5"))
        stop_action.setStatusTip("Stop the running simulation")
        stop_action.triggered.connect(self.stop_simulation)
        stop_action.setEnabled(False)  # Initially disabled
        sim_menu.addAction(stop_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        # About
        about_action = QAction("&About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbars(self):
        """Set up application toolbars."""
        
        # Main toolbar
        main_toolbar = self.addToolBar("Main")
        main_toolbar.setMovable(False)
        
        # Add common actions to toolbar
        # (Actions will be added as functionality is implemented)
        
    def setup_status_bar(self):
        """Set up the status bar."""
        
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
    def setup_connections(self):
        """Set up signal-slot connections."""
        
        # Connect model loading signal
        self.model_loaded.connect(self.on_model_loaded)
        
    def center_on_screen(self):
        """Center the window on the screen."""
        
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())
        
    def update_window_title(self):
        """Update the window title based on current model."""

        title_parts = ["System Dynamics Modeler - Enhanced"]

        # Add project management info if available
        if PROJECT_MANAGEMENT_AVAILABLE and hasattr(self, 'current_project') and self.current_project:
            title_parts.append(f"Project: {self.current_project}")

            if hasattr(self, 'current_system') and self.current_system:
                title_parts.append(f"System: {self.current_system}")

        # Show model file info
        if self.current_model_path:
            title_parts.append(Path(self.current_model_path).name)
        if self.current_gui_model and hasattr(self.current_gui_model, 'name'):
            title_parts.append(f"({self.current_gui_model.name})")

        self.setWindowTitle(" | ".join(title_parts))

    # Project management methods (simple implementation)
    def new_project(self):
        """Create a new project."""
        if not PROJECT_MANAGEMENT_AVAILABLE:
            return

        try:
            self.project_tree.create_new_project()
            self.status_bar.showMessage("New project created in tree...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create new project: {e}")

    def open_project(self):
        """Open an existing project."""
        if not PROJECT_MANAGEMENT_AVAILABLE:
            return

        try:
            self.project_tree.load_model()
            self.status_bar.showMessage("Loading model...")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open project: {e}")

    def on_project_selected(self, project_name_or_path):
        """Handle project selection from tree."""
        # If it's a file path, load the model
        if project_name_or_path and (project_name_or_path.endswith('.yaml') or project_name_or_path.endswith('.yml')):
            self.load_model_from_path(project_name_or_path)
        else:
            self.current_project = project_name_or_path
            self.current_system = None
            self.update_window_title()
            self.status_bar.showMessage(f"Selected project: {project_name_or_path}")

    def on_system_selected(self, project_name, system_name):
        """Handle system selection from tree."""
        self.current_project = project_name
        self.current_system = system_name

        # Create a new model for this system
        try:
            model_name = f"{system_name} ({project_name})"
            self.current_gui_model = GuiModel(model_name, f"System dynamics model for {system_name}")
            self.current_sd_model = None
            self.current_model_path = None

            # Load the new model into the canvas
            if self.model_canvas:
                self.model_canvas.load_model(self.current_gui_model)

            # Update inspector
            if self.component_inspector:
                self.component_inspector.set_model(self.current_gui_model)

            # Enable component palette
            if hasattr(self, 'component_palette') and self.component_palette:
                self.component_palette.setEnabled(True)

            # Emit model loaded signal
            self.model_loaded.emit(self.current_gui_model)

            self.update_window_title()
            self.status_bar.showMessage(f"System '{system_name}' ready for modeling - you can now add components!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create model for system: {e}")
            self.status_bar.showMessage(f"Failed to create model for system: {system_name}")

    def on_component_selected_from_tree(self, project_name, system_name, component_name):
        """Handle component selection from project tree."""
        self.current_project = project_name
        self.current_system = system_name

        self.status_bar.showMessage(f"Selected component: {component_name}")

    def load_model_from_path(self, file_path):
        """Load a model from file path."""
        try:
            self.status_bar.showMessage(f"Loading model from {file_path}...")

            gui_model, sd_model = self.yaml_loader.load_model_from_file(file_path)
            self.current_gui_model = gui_model
            self.current_sd_model = sd_model
            self.current_model_path = file_path

            if self.model_canvas:
                self.model_canvas.load_model(gui_model)

            if self.component_inspector:
                self.component_inspector.set_model(gui_model)

            # Emit model loaded signal
            self.model_loaded.emit(gui_model)

            self.status_bar.showMessage(f"Loaded model: {gui_model.name}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load model: {e}")
            self.status_bar.showMessage("Failed to load model")

    # Menu action handlers
    def new_model(self):
        """Create a new model."""
        self.status_bar.showMessage("Creating new model...")
        
        try:
            # Create a new empty GUI model
            self.current_gui_model = GuiModel("New Model", "A new system dynamics model")
            self.current_sd_model = None  # Will be created when simulation is run
            self.current_model_path = None
            self.current_scenario_path = None
            self.simulation_results = None
            
            # Enable component palette
            if hasattr(self, 'component_palette') and self.component_palette:
                self.component_palette.setEnabled(True)
            
            # Emit signal to update UI (this will call on_model_loaded)
            self.model_loaded.emit(self.current_gui_model)
            
            self.status_bar.showMessage("New model created successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error Creating Model", f"Failed to create new model:\n{str(e)}")
            self.status_bar.showMessage("Failed to create new model")
        
    def open_model(self):
        """Open an existing model file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Model File",
            str(Path.cwd()),
            "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        
        if file_path:
            self.load_model_file(file_path)
            
    def load_model_file(self, file_path: str):
        """Load a model from file."""
        try:
            self.status_bar.showMessage(f"Loading model from {file_path}...")

            # Look for corresponding scenario file
            model_path = Path(file_path)
            scenario_path = None

            # Try to find scenario file in same directory
            scenario_candidates = [
                model_path.parent / "integrated_scenario_parameters.yaml",
                model_path.parent / "scenario_parameters.yaml",
                model_path.with_name(model_path.stem + "_scenario.yaml")
            ]

            for candidate in scenario_candidates:
                if candidate.exists():
                    scenario_path = str(candidate)
                    break

            # Load using YAML loader
            self.current_gui_model, self.current_sd_model = self.yaml_loader.load_model_from_file(
                file_path, scenario_path
            )

            self.current_model_path = file_path
            self.current_scenario_path = scenario_path

            # Emit signal for other components
            self.model_loaded.emit(self.current_gui_model)

            self.update_window_title()

            # Show loading success message
            scenario_msg = f" (with scenario: {Path(scenario_path).name})" if scenario_path else ""
            self.status_bar.showMessage(f"Model loaded: {Path(file_path).name}{scenario_msg}")

            # Show model info in status
            QTimer.singleShot(3000, lambda: self.status_bar.showMessage(
                f"Ready - {len(self.current_gui_model.components)} components, "
                f"{len(self.current_gui_model.connections)} connections"
            ))

        except Exception as e:
            QMessageBox.critical(self, "Error Loading Model", f"Failed to load model:\n{str(e)}")
            self.status_bar.showMessage("Failed to load model")
            
    def save_model(self):
        """Save the current model."""
        if self.current_model_path:
            self.save_model_to_file(self.current_model_path)
        else:
            self.save_model_as()
            
    def save_model_as(self):
        """Save the model with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Model As",
            str(Path.cwd()),
            "YAML Files (*.yaml);;All Files (*)"
        )
        
        if file_path:
            self.save_model_to_file(file_path)
            
    def save_model_to_file(self, file_path: str):
        """Save model to specified file."""
        try:
            if not self.current_gui_model:
                QMessageBox.warning(self, "No Model", "No model to save.")
                return

            self.status_bar.showMessage(f"Saving model to {file_path}...")

            # Determine scenario file path
            model_path = Path(file_path)
            scenario_path = model_path.with_name(model_path.stem + "_scenario.yaml")

            # Save using YAML saver
            self.yaml_saver.save_model_to_file(
                self.current_gui_model,
                file_path,
                str(scenario_path),
                save_scenario_separately=True
            )

            self.current_model_path = file_path
            self.current_scenario_path = str(scenario_path)
            self.update_window_title()

            self.status_bar.showMessage(f"Model saved: {model_path.name} (with scenario: {scenario_path.name})")

        except Exception as e:
            QMessageBox.critical(self, "Error Saving Model", f"Failed to save model:\n{str(e)}")
            self.status_bar.showMessage("Failed to save model")
            
    def run_simulation(self):
        """Run the current model simulation."""
        if not self.current_sd_model:
            QMessageBox.warning(self, "No Model", "Please load a model first.")
            return

        # Check if simulation can run
        can_run, message = self.simulation_controller.can_run_simulation()
        if not can_run:
            QMessageBox.warning(self, "Cannot Run Simulation", message)
            return

        # Start simulation
        self.simulation_controller.start_simulation()
        
    def stop_simulation(self):
        """Stop the running simulation."""
        if self.simulation_controller:
            self.simulation_controller.stop_simulation()
        self.status_bar.showMessage("Simulation stopped")
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About System Dynamics Modeler",
            """
            <h3>System Dynamics Modeler</h3>
            <p>A desktop GUI application for system dynamics modeling using the sd_toolkit framework.</p>
            <p><b>Features:</b></p>
            <ul>
            <li>Visual model design with drag-and-drop components</li>
            <li>YAML-based model loading and saving</li>
            <li>Multidimensional data visualization</li>
            <li>Simulation execution and results analysis</li>
            </ul>
            <p><b>Version:</b> 1.0.0</p>
            """
        )
        
    # Signal handlers
    def on_model_loaded(self, gui_model: GuiModel):
        """Handle model loaded signal."""
        # This is called when a model is successfully loaded
        # Load model into canvas
        if self.model_canvas:
            self.model_canvas.load_model(gui_model)

        # Update inspector with model
        if self.component_inspector:
            self.component_inspector.set_model(gui_model)

        # Update simulation controller with models
        if self.simulation_controller:
            self.simulation_controller.set_model(gui_model, self.current_sd_model)

        self.update_window_title()

    def on_component_selected(self, component):
        """Handle component selection in canvas."""
        # Update inspector with selected component
        if self.component_inspector:
            self.component_inspector.set_component(component)

        self.status_bar.showMessage(f"Selected: {component.name} ({component.component_type})")

    def on_model_modified(self):
        """Handle model modifications."""
        # Mark model as modified (could add * to title, enable save, etc.)
        self.status_bar.showMessage("Model modified")

    def on_component_modified_by_inspector(self, component):
        """Handle component modifications from inspector."""
        # Update canvas display if needed
        if self.model_canvas:
            # Find the visual item and update it
            item = self.model_canvas.component_items.get(component.name)
            if item:
                # Update text display
                item.text_item.setPlainText(component.name)
                item.update_text_position()

        self.status_bar.showMessage(f"Component modified: {component.name}")

    def on_property_changed(self, component_name, property_name, new_value):
        """Handle individual property changes."""
        self.status_bar.showMessage(f"Property changed: {component_name}.{property_name} = {new_value}")

    def on_simulation_started(self):
        """Handle simulation start."""
        self.status_bar.showMessage("Simulation started...")
        # Disable simulation controls
        self.findChild(QAction, "run_simulation").setEnabled(False) if hasattr(self, 'run_action') else None

    def on_simulation_finished(self, results):
        """Handle simulation completion."""
        self.simulation_results = results
        self.status_bar.showMessage("Simulation completed successfully!")

        # Re-enable simulation controls
        self.findChild(QAction, "run_simulation").setEnabled(True) if hasattr(self, 'run_action') else None

        # Show results summary
        if results is not None:
            summary = self.simulation_controller.get_results_summary()
            QMessageBox.information(
                self,
                "Simulation Complete",
                f"Simulation completed successfully!\n\n"
                f"Time range: {summary.get('time_range', 'N/A')}\n"
                f"Variables: {len(summary.get('variables', []))}\n"
                f"Data points: {summary.get('data_points', 'N/A')}\n\n"
                f"Results are available for visualization and export."
            )

    def on_simulation_error(self, error_message):
        """Handle simulation errors."""
        self.status_bar.showMessage("Simulation failed!")

        # Re-enable simulation controls
        self.findChild(QAction, "run_simulation").setEnabled(True) if hasattr(self, 'run_action') else None

        # Show error message
        QMessageBox.critical(
            self,
            "Simulation Error",
            f"Simulation failed with error:\n\n{error_message}"
        )

    def on_simulation_progress(self, percentage, status):
        """Handle simulation progress updates."""
        if percentage >= 0:
            self.status_bar.showMessage(f"Simulation progress: {percentage}%")
        elif status:
            self.status_bar.showMessage(status)
        
    def closeEvent(self, event):
        """Handle application close event."""
        # Add any cleanup logic here
        event.accept()
