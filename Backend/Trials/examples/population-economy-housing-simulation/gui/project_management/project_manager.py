"""
Project Management Core Classes

Provides the main project management functionality including project creation,
system organization, and file structure management.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..yaml_integration.yaml_loader import GuiModel, ModelComponent


@dataclass
class SystemModel:
    """Represents a system within a project with its components and metadata."""
    
    name: str
    description: str = ""
    system_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    # Component organization
    stocks: Dict[str, ModelComponent] = field(default_factory=dict)
    flows: Dict[str, ModelComponent] = field(default_factory=dict)
    calculators: Dict[str, ModelComponent] = field(default_factory=dict)
    constants: Dict[str, Any] = field(default_factory=dict)
    
    # System configuration
    dimensions: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Any] = field(default_factory=dict)
    connections: List[Tuple[str, str, str]] = field(default_factory=list)
    
    # File paths (relative to project root)
    system_path: Optional[str] = None
    
    def add_component(self, component: ModelComponent):
        """Add a component to the appropriate category."""
        if component.component_type == 'stock':
            self.stocks[component.name] = component
        elif component.component_type == 'flow':
            self.flows[component.name] = component
        elif component.component_type == 'calculator':
            self.calculators[component.name] = component
        
        self.modified_at = datetime.now()
    
    def remove_component(self, component_name: str) -> bool:
        """Remove a component by name. Returns True if found and removed."""
        for category in [self.stocks, self.flows, self.calculators]:
            if component_name in category:
                del category[component_name]
                self.modified_at = datetime.now()
                return True
        return False
    
    def get_all_components(self) -> Dict[str, ModelComponent]:
        """Get all components in a single dictionary."""
        all_components = {}
        all_components.update(self.stocks)
        all_components.update(self.flows)
        all_components.update(self.calculators)
        return all_components
    
    def to_gui_model(self) -> GuiModel:
        """Convert to GuiModel for compatibility with existing GUI."""
        gui_model = GuiModel(self.name, self.description)
        gui_model.dimensions = self.dimensions.copy()
        gui_model.functions = self.functions.copy()
        gui_model.constants = self.constants.copy()
        
        # Add all components
        for component in self.get_all_components().values():
            gui_model.add_component(component)
        
        # Add connections
        gui_model.connections = self.connections.copy()
        
        return gui_model


@dataclass
class Project:
    """Represents a complete project with multiple systems and metadata."""
    
    name: str
    description: str = ""
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    # Project organization
    systems: Dict[str, SystemModel] = field(default_factory=dict)
    project_path: Optional[str] = None
    
    # Project-level configuration
    global_dimensions: Dict[str, Any] = field(default_factory=dict)
    global_constants: Dict[str, Any] = field(default_factory=dict)
    
    def add_system(self, system: SystemModel):
        """Add a system to the project."""
        self.systems[system.name] = system
        self.modified_at = datetime.now()
    
    def remove_system(self, system_name: str) -> bool:
        """Remove a system by name. Returns True if found and removed."""
        if system_name in self.systems:
            del self.systems[system_name]
            self.modified_at = datetime.now()
            return True
        return False
    
    def get_system(self, system_name: str) -> Optional[SystemModel]:
        """Get a system by name."""
        return self.systems.get(system_name)


class ProjectManager:
    """
    Main project management interface.
    
    Handles project creation, loading, saving, and file structure management.
    Maintains compatibility with existing sd_toolkit YAML patterns.
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        """
        Initialize project manager.
        
        Parameters:
        -----------
        workspace_root : str, optional
            Root directory for all projects. Defaults to current directory.
        """
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.current_project: Optional[Project] = None
        self.projects: Dict[str, Project] = {}
    
    def create_project(self, name: str, description: str = "", 
                      project_path: Optional[str] = None) -> Project:
        """
        Create a new project with automatic folder structure.
        
        Parameters:
        -----------
        name : str
            Project name
        description : str
            Project description
        project_path : str, optional
            Custom project path. If None, uses workspace_root/project_name
            
        Returns:
        --------
        Project : The created project
        """
        # Determine project path
        if project_path is None:
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            project_path = self.workspace_root / safe_name
        else:
            project_path = Path(project_path)
        
        # Create project structure
        self._create_project_structure(project_path)
        
        # Create project object
        project = Project(name=name, description=description, project_path=str(project_path))
        
        # Save project configuration
        self._save_project_config(project)
        
        # Add to projects registry
        self.projects[name] = project
        
        return project
    
    def load_project(self, project_path: str) -> Project:
        """
        Load an existing project from disk.
        
        Parameters:
        -----------
        project_path : str
            Path to the project directory
            
        Returns:
        --------
        Project : The loaded project
        """
        project_path = Path(project_path)
        config_path = project_path / "project_config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Project configuration not found: {config_path}")
        
        # Load project configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Create project object
        project = Project(
            name=config['project']['name'],
            description=config['project'].get('description', ''),
            project_id=config['project'].get('project_id', str(uuid.uuid4())),
            project_path=str(project_path)
        )
        
        # Load global configuration
        if 'global_dimensions' in config:
            project.global_dimensions = config['global_dimensions']
        if 'global_constants' in config:
            project.global_constants = config['global_constants']
        
        # Load systems
        systems_path = project_path / "systems"
        if systems_path.exists():
            for system_dir in systems_path.iterdir():
                if system_dir.is_dir():
                    system = self._load_system(system_dir, project)
                    if system:
                        project.add_system(system)
        
        # Add to projects registry
        self.projects[project.name] = project
        
        return project
    
    def save_project(self, project: Project):
        """Save project and all its systems to disk."""
        if not project.project_path:
            raise ValueError("Project path not set")
        
        project_path = Path(project.project_path)
        
        # Ensure project structure exists
        self._create_project_structure(project_path)
        
        # Save project configuration
        self._save_project_config(project)
        
        # Save all systems
        for system in project.systems.values():
            self._save_system(system, project)
    
    def _create_project_structure(self, project_path: Path):
        """Create the standard project folder structure."""
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / "systems").mkdir(exist_ok=True)
        
    def _save_project_config(self, project: Project):
        """Save project configuration to YAML file."""
        config_path = Path(project.project_path) / "project_config.yaml"
        
        config = {
            'project': {
                'name': project.name,
                'description': project.description,
                'project_id': project.project_id,
                'created_at': project.created_at.isoformat(),
                'modified_at': project.modified_at.isoformat(),
                'version': '1.0'
            }
        }
        
        if project.global_dimensions:
            config['global_dimensions'] = project.global_dimensions
        
        if project.global_constants:
            config['global_constants'] = project.global_constants
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    def _load_system(self, system_path: Path, project: Project) -> Optional[SystemModel]:
        """Load a system from its directory."""
        from .component_manager import ComponentManager
        component_manager = ComponentManager()
        return component_manager.load_system(system_path, project)

    def _save_system(self, system: SystemModel, project: Project):
        """Save a system to its directory."""
        from .component_manager import ComponentManager
        component_manager = ComponentManager()
        component_manager.save_system(system, project)
