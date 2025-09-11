"""
Enhanced Main Window with Project Management

Extended version of the main window that includes hierarchical project management
with multi-project support, system organization, and enhanced component editing.
"""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QToolBar, QStatusBar, QDockWidget,
    QMessageBox, QFileDialog, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QIcon

# Import existing GUI components
from yaml_integration.yaml_loader import YAMLModelLoader, GuiModel
from yaml_integration.yaml_saver import YAMLModelSaver
from canvas.model_canvas import ModelCanvas
from components.palette import ComponentPalette
from inspector.component_inspector import ComponentInspector
from simulation.simulation_controller import SimulationController

# Import new project management components
from project_management.project_tree_widget import ProjectTreeWidget
from project_management.project_manager import ProjectManager, Project, SystemModel
from project_management.component_manager import ComponentManager
from project_management.informants_manager import InformantsManager


class EnhancedSystemDynamicsMainWindow(QMainWindow):
    """
    Enhanced main application window with hierarchical project management.
    
    Features:
    - Multi-project organization with automatic folder structure
    - Hierarchical tree view for projects, systems, and components
    - Enhanced component editing with informants management
    - Backward compatibility with existing single-model workflows
    """
    
    # Signals
    project_loaded = pyqtSignal(object)  # Project
    system_loaded = pyqtSignal(object, object)  # Project, SystemModel
    model_loaded = pyqtSignal(object)  # GuiModel (for backward compatibility)
    simulation_started = pyqtSignal()
    simulation_finished = pyqtSignal(object)  # Emitted with results
    
    def __init__(self):
        super().__init__()
        
        # Window properties
        self.setWindowTitle("System Dynamics Modeler - Enhanced")
        self.setMinimumSize(1400, 900)
        self.resize(1800, 1200)
        
        # Project management
        self.project_manager = ProjectManager()
        self.component_manager = ComponentManager()
        self.informants_manager = InformantsManager()
        
        # Current state
        self.current_project: Optional[Project] = None
        self.current_system: Optional[SystemModel] = None
        self.current_gui_model: Optional[GuiModel] = None  # For backward compatibility
        self.current_sd_model = None   # sd_toolkit model for simulation
        self.simulation_results = None
        
        # Legacy YAML integration (for backward compatibility)
        self.yaml_loader = YAMLModelLoader()
        self.yaml_saver = YAMLModelSaver()
        
        # Initialize components (will be created in setup_ui)
        self.project_tree = None
        self.model_canvas = None
        self.component_palette = None
        self.component_inspector = None
        self.simulation_controller = None
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Initialize with empty state
        self.update_window_title()
    
    def setup_ui(self):
        """Set up the enhanced user interface layout."""
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitters for resizable panels
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create main splitter (horizontal)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel: Project tree
        self.project_tree = ProjectTreeWidget()
        main_splitter.addWidget(self.project_tree)
        
        # Center panel: Canvas and tabs
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget for different views
        self.center_tabs = QTabWidget()
        
        # Model canvas tab
        self.model_canvas = ModelCanvas()
        self.center_tabs.addTab(self.model_canvas, "Model Canvas")
        
        # Future tabs could include:
        # - Informants editor
        # - System overview
        # - Validation results
        
        center_layout.addWidget(self.center_tabs)
        main_splitter.addWidget(center_widget)
        
        # Right panel: Component palette and inspector
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Component palette
        self.component_palette = ComponentPalette()
        right_layout.addWidget(self.component_palette)
        
        # Component inspector
        self.component_inspector = ComponentInspector()
        right_layout.addWidget(self.component_inspector)
        
        main_splitter.addWidget(right_widget)
        
        # Set splitter proportions: tree(300), canvas(800), palette+inspector(400)
        main_splitter.setSizes([300, 800, 400])
        
        # Create simulation controller (not visible, just for functionality)
        self.simulation_controller = SimulationController()
    
    def setup_menu_bar(self):
        """Set up the enhanced menu bar."""
        menubar = self.menuBar()
        
        # Project menu
        project_menu = menubar.addMenu("Project")
        
        new_project_action = QAction("New Project", self)
        new_project_action.setShortcut(QKeySequence.StandardKey.New)
        new_project_action.triggered.connect(self.new_project)
        project_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open Project", self)
        open_project_action.setShortcut(QKeySequence.StandardKey.Open)
        open_project_action.triggered.connect(self.open_project)
        project_menu.addAction(open_project_action)
        
        project_menu.addSeparator()
        
        save_project_action = QAction("Save Project", self)
        save_project_action.setShortcut(QKeySequence.StandardKey.Save)
        save_project_action.triggered.connect(self.save_project)
        project_menu.addAction(save_project_action)
        
        project_menu.addSeparator()
        
        # Legacy model operations for backward compatibility
        legacy_menu = project_menu.addMenu("Legacy Model")
        
        open_model_action = QAction("Open YAML Model", self)
        open_model_action.triggered.connect(self.open_legacy_model)
        legacy_menu.addAction(open_model_action)
        
        save_model_action = QAction("Save as YAML Model", self)
        save_model_action.triggered.connect(self.save_legacy_model)
        legacy_menu.addAction(save_model_action)
        
        # System menu
        system_menu = menubar.addMenu("System")
        
        new_system_action = QAction("New System", self)
        new_system_action.triggered.connect(self.new_system)
        system_menu.addAction(new_system_action)
        
        # Component menu
        component_menu = menubar.addMenu("Component")
        
        new_stock_action = QAction("New Stock", self)
        new_stock_action.triggered.connect(lambda: self.new_component("stock"))
        component_menu.addAction(new_stock_action)
        
        new_flow_action = QAction("New Flow", self)
        new_flow_action.triggered.connect(lambda: self.new_component("flow"))
        component_menu.addAction(new_flow_action)
        
        new_calculator_action = QAction("New Calculator", self)
        new_calculator_action.triggered.connect(lambda: self.new_component("calculator"))
        component_menu.addAction(new_calculator_action)
        
        # Simulation menu
        simulation_menu = menubar.addMenu("Simulation")
        
        run_simulation_action = QAction("Run Simulation", self)
        run_simulation_action.setShortcut("F5")
        run_simulation_action.triggered.connect(self.run_simulation)
        simulation_menu.addAction(run_simulation_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        validate_action = QAction("Validate Model", self)
        validate_action.triggered.connect(self.validate_current_model)
        tools_menu.addAction(validate_action)
        
        manage_informants_action = QAction("Manage Informants", self)
        manage_informants_action.triggered.connect(self.manage_informants)
        tools_menu.addAction(manage_informants_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Set up the toolbar."""
        toolbar = self.addToolBar("Main")
        
        # Project operations
        toolbar.addAction("New Project", self.new_project)
        toolbar.addAction("Open Project", self.open_project)
        toolbar.addAction("Save Project", self.save_project)
        toolbar.addSeparator()
        
        # Simulation
        toolbar.addAction("Run Simulation", self.run_simulation)
        toolbar.addSeparator()
        
        # Validation
        toolbar.addAction("Validate", self.validate_current_model)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Enhanced System Dynamics Modeler")
    
    def setup_connections(self):
        """Set up signal connections."""
        # Project tree connections
        self.project_tree.project_selected.connect(self.on_project_selected)
        self.project_tree.system_selected.connect(self.on_system_selected)
        self.project_tree.component_selected.connect(self.on_component_selected)
        
        # Canvas connections
        if self.model_canvas:
            self.model_canvas.component_selected.connect(self.on_canvas_component_selected)
            self.model_canvas.model_modified.connect(self.on_model_modified)
        
        # Component palette connections
        if self.component_palette:
            self.component_palette.component_requested.connect(self.on_component_requested)
    
    def update_window_title(self):
        """Update the window title based on current state."""
        title_parts = ["System Dynamics Modeler - Enhanced"]
        
        if self.current_project:
            title_parts.append(f"Project: {self.current_project.name}")
            
            if self.current_system:
                title_parts.append(f"System: {self.current_system.name}")
        
        self.setWindowTitle(" | ".join(title_parts))
    
    # Project management methods
    def new_project(self):
        """Create a new project."""
        # This would open a project creation dialog
        # For now, use the project tree's method
        self.project_tree.create_new_project()
    
    def open_project(self):
        """Open an existing project."""
        project_dir = QFileDialog.getExistingDirectory(
            self, "Open Project", "", QFileDialog.Option.ShowDirsOnly
        )
        
        if project_dir:
            try:
                self.project_tree.load_project(project_dir)
                self.status_bar.showMessage(f"Opened project from {project_dir}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project: {e}")
    
    def save_project(self):
        """Save the current project."""
        if self.current_project:
            try:
                self.project_manager.save_project(self.current_project)
                self.status_bar.showMessage(f"Saved project: {self.current_project.name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project: {e}")
        else:
            QMessageBox.information(self, "No Project", "No project is currently open.")
    
    def new_system(self):
        """Create a new system in the current project."""
        if self.current_project:
            self.project_tree.create_new_system(self.current_project)
        else:
            QMessageBox.information(self, "No Project", "Please open or create a project first.")
    
    def new_component(self, component_type: str):
        """Create a new component in the current system."""
        if self.current_system and self.current_project:
            self.project_tree.create_new_component(self.current_project, self.current_system, component_type)
        else:
            QMessageBox.information(self, "No System", "Please select a system first.")
    
    # Event handlers
    def on_project_selected(self, project: Project):
        """Handle project selection."""
        self.current_project = project
        self.current_system = None
        self.current_gui_model = None
        self.update_window_title()
        self.status_bar.showMessage(f"Selected project: {project.name}")
    
    def on_system_selected(self, project: Project, system: SystemModel):
        """Handle system selection."""
        self.current_project = project
        self.current_system = system
        
        # Convert to GuiModel for backward compatibility
        self.current_gui_model = system.to_gui_model()
        
        # Load into canvas
        if self.model_canvas:
            self.model_canvas.load_model(self.current_gui_model)
        
        # Update inspector
        if self.component_inspector:
            self.component_inspector.set_model(self.current_gui_model)
        
        self.update_window_title()
        self.status_bar.showMessage(f"Selected system: {system.name}")
    
    def on_component_selected(self, project: Project, system: SystemModel, component):
        """Handle component selection from tree."""
        self.current_project = project
        self.current_system = system
        
        # Update inspector with component
        if self.component_inspector:
            self.component_inspector.set_current_component(component)
        
        self.status_bar.showMessage(f"Selected component: {component.name}")
    
    def on_canvas_component_selected(self, component):
        """Handle component selection from canvas."""
        if self.component_inspector:
            self.component_inspector.set_current_component(component)
    
    def on_model_modified(self):
        """Handle model modification."""
        self.status_bar.showMessage("Model modified")
    
    def on_component_requested(self, component_type: str):
        """Handle component creation request from palette."""
        self.new_component(component_type)
    
    # Legacy compatibility methods
    def open_legacy_model(self):
        """Open a legacy YAML model file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open YAML Model", "", "YAML Files (*.yaml *.yml)"
        )
        
        if file_path:
            try:
                gui_model, sd_model = self.yaml_loader.load_model_from_file(file_path)
                self.current_gui_model = gui_model
                self.current_sd_model = sd_model
                
                # Load into canvas
                if self.model_canvas:
                    self.model_canvas.load_model(gui_model)
                
                self.status_bar.showMessage(f"Loaded legacy model: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load model: {e}")
    
    def save_legacy_model(self):
        """Save current model as legacy YAML."""
        if self.current_gui_model:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save YAML Model", "", "YAML Files (*.yaml)"
            )
            
            if file_path:
                try:
                    self.yaml_saver.save_model_to_file(self.current_gui_model, file_path)
                    self.status_bar.showMessage(f"Saved legacy model: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save model: {e}")
        else:
            QMessageBox.information(self, "No Model", "No model is currently loaded.")
    
    # Simulation and validation methods
    def run_simulation(self):
        """Run simulation on current model."""
        if self.current_gui_model and self.simulation_controller:
            try:
                self.simulation_controller.set_model(self.current_gui_model, self.current_sd_model)
                # This would trigger the simulation
                self.status_bar.showMessage("Running simulation...")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to run simulation: {e}")
        else:
            QMessageBox.information(self, "No Model", "No model is currently loaded.")
    
    def validate_current_model(self):
        """Validate the current model."""
        if self.current_system:
            validation_results = self.informants_manager.validate_system_informants(self.current_system)
            
            if validation_results:
                error_messages = []
                for component_name, errors in validation_results.items():
                    error_messages.append(f"{component_name}: {', '.join(errors)}")
                
                QMessageBox.warning(self, "Validation Errors", 
                                  "Model validation found issues:\n\n" + "\n".join(error_messages))
            else:
                QMessageBox.information(self, "Validation Success", "Model validation passed!")
        else:
            QMessageBox.information(self, "No System", "No system is currently selected.")
    
    def manage_informants(self):
        """Open informants management dialog."""
        if self.current_system:
            # This would open an informants management dialog
            QMessageBox.information(self, "Manage Informants", 
                                  f"Opening informants manager for {self.current_system.name}")
        else:
            QMessageBox.information(self, "No System", "No system is currently selected.")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", 
                         "Enhanced System Dynamics Modeler\n\n"
                         "Features hierarchical project management with:\n"
                         "• Multi-project organization\n"
                         "• System-level component organization\n"
                         "• Enhanced multidimensional editing\n"
                         "• Informants data management\n"
                         "• Backward compatibility with existing models")
