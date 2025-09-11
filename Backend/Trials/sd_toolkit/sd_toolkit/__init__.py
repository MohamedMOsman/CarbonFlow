"""
High-Resolution Spatiotemporal System Dynamics Toolkit

A Python-based software toolkit for system dynamics modeling with multi-dimensional,
unit-aware data structures designed for climate action adaptation modeling.
"""

__version__ = "0.1.0"
__author__ = "System Dynamics Toolkit Team"

from .core import units
from .data import loader
from .engine import elements, system
from .analysis import plotting

__all__ = [
    "units",
    "loader", 
    "elements",
    "system",
    "plotting"
]
