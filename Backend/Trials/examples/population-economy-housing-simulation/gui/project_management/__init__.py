"""
Project Management Module for System Dynamics GUI

This module provides hierarchical project management capabilities including:
- Multi-project organization with automatic folder structure generation
- System-level organization within projects
- Component file management with YAML compatibility
- Informants data management for dimensional data
- Project configuration and metadata handling

Key Classes:
- ProjectManager: Main project management interface
- Project: Individual project representation
- SystemModel: System-level organization within projects
- ComponentManager: Handles component file operations
- InformantsManager: Manages dimensional data separately from components
"""

__version__ = "1.0.0"
__author__ = "System Dynamics Toolkit"

from .project_manager import ProjectManager, Project, SystemModel
from .component_manager import ComponentManager
from .informants_manager import InformantsManager
from .project_tree_widget import ProjectTreeWidget

__all__ = [
    'ProjectManager',
    'Project', 
    'SystemModel',
    'ComponentManager',
    'InformantsManager',
    'ProjectTreeWidget'
]
