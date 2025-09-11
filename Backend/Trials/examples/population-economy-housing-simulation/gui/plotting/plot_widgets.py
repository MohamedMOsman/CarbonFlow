"""
Plot Widgets for Results Visualization

This module provides specialized plot widgets for displaying simulation results
using matplotlib integration with PyQt6.
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt backend for matplotlib

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QGroupBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class PlotWidget(QWidget):
    """Base plot widget with matplotlib integration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Create navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Configure matplotlib
        plt.style.use('default')
        
    def set_figure(self, figure: Figure):
        """Set a new matplotlib figure."""
        
        # Clear current figure
        self.figure.clear()
        
        # Copy axes from new figure
        for ax in figure.axes:
            new_ax = self.figure.add_subplot(ax.get_gridspec(), ax.get_subplotspec())
            
            # Copy plot elements
            for line in ax.get_lines():
                new_ax.plot(line.get_xdata(), line.get_ydata(), 
                           color=line.get_color(), label=line.get_label(),
                           linewidth=line.get_linewidth(), linestyle=line.get_linestyle())
                           
            # Copy labels and title
            new_ax.set_xlabel(ax.get_xlabel())
            new_ax.set_ylabel(ax.get_ylabel())
            new_ax.set_title(ax.get_title())
            
            # Copy legend if present
            if ax.get_legend():
                new_ax.legend()
                
            # Copy grid
            new_ax.grid(ax.get_gridlines() != [])
            
        # Refresh canvas
        self.canvas.draw()
        
    def clear_plot(self):
        """Clear the plot."""
        self.figure.clear()
        self.canvas.draw()
        
    def save_plot(self, file_path: str):
        """Save plot to file."""
        self.figure.savefig(file_path, dpi=300, bbox_inches='tight')


class TimeSeriesPlotWidget(PlotWidget):
    """Specialized widget for time series plotting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Add controls specific to time series
        self.setup_controls()
        
    def setup_controls(self):
        """Set up time series specific controls."""
        
        # Insert controls above the plot
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        
        # Y-axis scale
        self.log_scale_cb = QCheckBox("Log Scale")
        self.log_scale_cb.stateChanged.connect(self.update_scale)
        controls_layout.addWidget(self.log_scale_cb)
        
        # Grid toggle
        self.grid_cb = QCheckBox("Grid")
        self.grid_cb.setChecked(True)
        self.grid_cb.stateChanged.connect(self.update_grid)
        controls_layout.addWidget(self.grid_cb)
        
        controls_layout.addStretch()
        
        # Insert at top of layout
        self.layout().insertWidget(1, controls_widget)
        
    def plot_time_series(self, data: pd.DataFrame, variables: List[str], 
                         title: str = "Time Series Plot"):
        """Plot time series data."""
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Plot each variable
        for var in variables:
            if var in data.columns:
                ax.plot(data['time'], data[var], label=var, linewidth=2)
                
        # Formatting
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.set_title(title)
        ax.legend()
        ax.grid(self.grid_cb.isChecked())
        
        # Apply log scale if selected
        if self.log_scale_cb.isChecked():
            ax.set_yscale('log')
            
        # Tight layout
        self.figure.tight_layout()
        
        # Refresh canvas
        self.canvas.draw()
        
    def update_scale(self):
        """Update Y-axis scale."""
        for ax in self.figure.axes:
            if self.log_scale_cb.isChecked():
                ax.set_yscale('log')
            else:
                ax.set_yscale('linear')
        self.canvas.draw()
        
    def update_grid(self):
        """Update grid display."""
        for ax in self.figure.axes:
            ax.grid(self.grid_cb.isChecked())
        self.canvas.draw()


class MultidimensionalPlotWidget(PlotWidget):
    """Specialized widget for multidimensional data plotting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_controls()
        
    def setup_controls(self):
        """Set up multidimensional plotting controls."""
        
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        
        # Plot type selection
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["Heatmap", "3D Surface", "Contour", "Population Pyramid"])
        controls_layout.addWidget(QLabel("Plot Type:"))
        controls_layout.addWidget(self.plot_type_combo)
        
        # Dimension selection
        self.dim1_combo = QComboBox()
        self.dim2_combo = QComboBox()
        controls_layout.addWidget(QLabel("X Dimension:"))
        controls_layout.addWidget(self.dim1_combo)
        controls_layout.addWidget(QLabel("Y Dimension:"))
        controls_layout.addWidget(self.dim2_combo)
        
        controls_layout.addStretch()
        
        # Update button
        update_btn = QPushButton("Update Plot")
        update_btn.clicked.connect(self.update_multidim_plot)
        controls_layout.addWidget(update_btn)
        
        # Insert at top of layout
        self.layout().insertWidget(1, controls_widget)
        
    def plot_heatmap(self, data: np.ndarray, x_labels: List[str], y_labels: List[str],
                     title: str = "Heatmap", cmap: str = 'viridis'):
        """Plot a heatmap of 2D data."""
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Create heatmap
        im = ax.imshow(data, cmap=cmap, aspect='auto', origin='lower')
        
        # Set labels
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45)
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels)
        
        # Add colorbar
        self.figure.colorbar(im, ax=ax)
        
        # Set title
        ax.set_title(title)
        
        # Tight layout
        self.figure.tight_layout()
        
        # Refresh canvas
        self.canvas.draw()
        
    def plot_population_pyramid(self, data: Dict[str, np.ndarray], age_groups: List[str],
                                title: str = "Population Pyramid"):
        """Plot a population pyramid."""
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Assume data has 'male' and 'female' keys
        if 'male' in data and 'female' in data:
            male_data = data['male']
            female_data = data['female']
            
            y_pos = np.arange(len(age_groups))
            
            # Plot bars (male on left, female on right)
            ax.barh(y_pos, -male_data, align='center', alpha=0.7, label='Male', color='blue')
            ax.barh(y_pos, female_data, align='center', alpha=0.7, label='Female', color='red')
            
            # Formatting
            ax.set_yticks(y_pos)
            ax.set_yticklabels(age_groups)
            ax.set_xlabel('Population')
            ax.set_ylabel('Age Group')
            ax.set_title(title)
            ax.legend()
            
            # Add vertical line at zero
            ax.axvline(0, color='black', linewidth=0.8)
            
            # Make x-axis labels positive
            ax.set_xticklabels([abs(int(x)) for x in ax.get_xticks()])
            
        # Tight layout
        self.figure.tight_layout()
        
        # Refresh canvas
        self.canvas.draw()
        
    def update_multidim_plot(self):
        """Update multidimensional plot based on current settings."""
        # This would be implemented based on the specific data structure
        # For now, just a placeholder
        pass
        
    def set_dimensions(self, dimensions: List[str]):
        """Set available dimensions for plotting."""
        
        self.dim1_combo.clear()
        self.dim2_combo.clear()
        
        self.dim1_combo.addItems(dimensions)
        self.dim2_combo.addItems(dimensions)


class StatisticsPlotWidget(PlotWidget):
    """Widget for statistical plots (histograms, box plots, etc.)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_controls()
        
    def setup_controls(self):
        """Set up statistics plotting controls."""
        
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        
        # Plot type
        self.stats_type_combo = QComboBox()
        self.stats_type_combo.addItems(["Histogram", "Box Plot", "Violin Plot", "Scatter"])
        controls_layout.addWidget(QLabel("Plot Type:"))
        controls_layout.addWidget(self.stats_type_combo)
        
        # Bins for histogram
        self.bins_spinbox = QSpinBox()
        self.bins_spinbox.setRange(5, 100)
        self.bins_spinbox.setValue(20)
        controls_layout.addWidget(QLabel("Bins:"))
        controls_layout.addWidget(self.bins_spinbox)
        
        controls_layout.addStretch()
        
        # Insert at top of layout
        self.layout().insertWidget(1, controls_widget)
        
    def plot_histogram(self, data: pd.Series, title: str = "Histogram", bins: int = 20):
        """Plot histogram of data."""
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Create histogram
        ax.hist(data.dropna(), bins=bins, alpha=0.7, edgecolor='black')
        
        # Formatting
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # Add statistics text
        mean_val = data.mean()
        std_val = data.std()
        ax.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
        ax.axvline(mean_val + std_val, color='orange', linestyle='--', alpha=0.7, label=f'+1σ: {mean_val + std_val:.2f}')
        ax.axvline(mean_val - std_val, color='orange', linestyle='--', alpha=0.7, label=f'-1σ: {mean_val - std_val:.2f}')
        
        ax.legend()
        
        # Tight layout
        self.figure.tight_layout()
        
        # Refresh canvas
        self.canvas.draw()
        
    def plot_box_plot(self, data: Dict[str, pd.Series], title: str = "Box Plot"):
        """Plot box plot of multiple data series."""
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Prepare data
        plot_data = [series.dropna() for series in data.values()]
        labels = list(data.keys())
        
        # Create box plot
        bp = ax.boxplot(plot_data, labels=labels, patch_artist=True)
        
        # Color the boxes
        colors = plt.cm.Set3(np.linspace(0, 1, len(plot_data)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            
        # Formatting
        ax.set_ylabel('Value')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # Rotate labels if many
        if len(labels) > 5:
            plt.setp(ax.get_xticklabels(), rotation=45)
            
        # Tight layout
        self.figure.tight_layout()
        
        # Refresh canvas
        self.canvas.draw()
