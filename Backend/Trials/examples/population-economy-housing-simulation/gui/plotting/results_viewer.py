"""
Results Viewer for Simulation Results

This module provides visualization and analysis of simulation results
with integration to existing plotting capabilities.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QComboBox, QLabel, QGroupBox,
    QSplitter, QTextEdit, QFileDialog, QMessageBox, QCheckBox,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'sd_toolkit'))

from sd_toolkit.analysis.plotting import SystemPlotter
from sd_toolkit.analysis.multidimensional_plotting import MultidimensionalPlotter

from plotting.plot_widgets import PlotWidget, TimeSeriesPlotWidget, MultidimensionalPlotWidget


class ResultsViewer(QWidget):
    """
    Results viewer widget for displaying and analyzing simulation results.
    
    Provides:
    - Tabular data display
    - Time series plotting
    - Multidimensional data visualization
    - Export functionality
    - Statistical analysis
    """
    
    # Signals
    export_requested = pyqtSignal(str, str)  # file_path, format
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Current data
        self.results = None
        self.model = None
        self.plotter = None
        self.multidim_plotter = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the results viewer UI."""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title_label = QLabel("Simulation Results")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Control panel
        controls_layout = QHBoxLayout()
        
        # Variable selection
        self.variable_combo = QComboBox()
        self.variable_combo.currentTextChanged.connect(self.on_variable_changed)
        controls_layout.addWidget(QLabel("Variable:"))
        controls_layout.addWidget(self.variable_combo)
        
        controls_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export Results")
        export_btn.clicked.connect(self.export_results)
        controls_layout.addWidget(export_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_display)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Main content area
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Data table tab
        self.data_tab = self.create_data_tab()
        self.tab_widget.addTab(self.data_tab, "Data Table")
        
        # Time series plot tab
        self.plot_tab = self.create_plot_tab()
        self.tab_widget.addTab(self.plot_tab, "Time Series")
        
        # Statistics tab
        self.stats_tab = self.create_statistics_tab()
        self.tab_widget.addTab(self.stats_tab, "Statistics")
        
        # No results message
        self.no_results_label = QLabel("No simulation results available.\n\nRun a simulation to view results here.")
        self.no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results_label.setStyleSheet("QLabel { color: #666; padding: 20px; }")
        layout.addWidget(self.no_results_label)
        
        # Initially hide tabs
        self.tab_widget.hide()
        
    def create_data_tab(self) -> QWidget:
        """Create the data table tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Table info
        self.table_info_label = QLabel("Data table will be displayed here.")
        layout.addWidget(self.table_info_label)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSortingEnabled(True)
        layout.addWidget(self.data_table)
        
        return widget
        
    def create_plot_tab(self) -> QWidget:
        """Create the plotting tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Plot controls
        plot_controls = QHBoxLayout()
        
        # Variable selection for plotting
        self.plot_variables_combo = QComboBox()
        self.plot_variables_combo.setEditable(True)
        plot_controls.addWidget(QLabel("Variables:"))
        plot_controls.addWidget(self.plot_variables_combo)
        
        # Plot type selection
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["Time Series", "Phase Diagram", "Histogram"])
        plot_controls.addWidget(QLabel("Plot Type:"))
        plot_controls.addWidget(self.plot_type_combo)
        
        # Update plot button
        update_plot_btn = QPushButton("Update Plot")
        update_plot_btn.clicked.connect(self.update_plot)
        plot_controls.addWidget(update_plot_btn)
        
        plot_controls.addStretch()
        layout.addLayout(plot_controls)
        
        # Plot widget
        self.plot_widget = TimeSeriesPlotWidget()
        layout.addWidget(self.plot_widget)
        
        return widget
        
    def create_statistics_tab(self) -> QWidget:
        """Create the statistics tab."""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.stats_text)
        
        return widget
        
    def set_results(self, results: pd.DataFrame, model=None):
        """Set simulation results to display."""
        
        self.results = results
        self.model = model
        
        if results is not None and not results.empty:
            # Show tabs and hide no results message
            self.tab_widget.show()
            self.no_results_label.hide()
            
            # Create plotters
            if model:
                self.plotter = SystemPlotter(model)
                self.multidim_plotter = MultidimensionalPlotter()
                
            # Update all displays
            self.update_data_table()
            self.update_variable_selection()
            self.update_statistics()
            self.update_plot()
            
        else:
            # Hide tabs and show no results message
            self.tab_widget.hide()
            self.no_results_label.show()
            
    def update_data_table(self):
        """Update the data table with results."""
        
        if self.results is None or self.results.empty:
            return
            
        # Set table dimensions
        self.data_table.setRowCount(len(self.results))
        self.data_table.setColumnCount(len(self.results.columns))
        self.data_table.setHorizontalHeaderLabels(self.results.columns.tolist())
        
        # Populate table
        for i, row in self.results.iterrows():
            for j, (col_name, value) in enumerate(row.items()):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
                
        # Resize columns
        self.data_table.resizeColumnsToContents()
        
        # Update info label
        self.table_info_label.setText(
            f"Data table: {len(self.results)} rows × {len(self.results.columns)} columns"
        )
        
    def update_variable_selection(self):
        """Update variable selection dropdowns."""
        
        if self.results is None:
            return
            
        # Get numeric columns (excluding time)
        numeric_cols = self.results.select_dtypes(include=[np.number]).columns.tolist()
        if 'time' in numeric_cols:
            numeric_cols.remove('time')
            
        # Update variable combo
        self.variable_combo.clear()
        self.variable_combo.addItems(numeric_cols)
        
        # Update plot variables combo
        self.plot_variables_combo.clear()
        self.plot_variables_combo.addItems(numeric_cols)
        
    def update_statistics(self):
        """Update statistics display."""
        
        if self.results is None:
            return
            
        stats_text = "Simulation Results Statistics\n"
        stats_text += "=" * 40 + "\n\n"
        
        # Basic info
        stats_text += f"Time range: {self.results['time'].min():.2f} - {self.results['time'].max():.2f}\n"
        stats_text += f"Data points: {len(self.results)}\n"
        stats_text += f"Variables: {len(self.results.columns) - 1}\n\n"  # -1 for time column
        
        # Variable statistics
        numeric_cols = self.results.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col != 'time':
                stats_text += f"{col}:\n"
                stats_text += f"  Min: {self.results[col].min():.4f}\n"
                stats_text += f"  Max: {self.results[col].max():.4f}\n"
                stats_text += f"  Mean: {self.results[col].mean():.4f}\n"
                stats_text += f"  Std: {self.results[col].std():.4f}\n"
                stats_text += f"  Final: {self.results[col].iloc[-1]:.4f}\n\n"
                
        self.stats_text.setPlainText(stats_text)
        
    def update_plot(self):
        """Update the plot display."""
        
        if self.results is None or not self.plotter:
            return
            
        try:
            # Get selected variables
            selected_var = self.plot_variables_combo.currentText()
            if not selected_var:
                return
                
            # Create plot based on type
            plot_type = self.plot_type_combo.currentText()
            
            if plot_type == "Time Series":
                fig = self.plotter.plot_time_series(self.results, [selected_var])
                self.plot_widget.set_figure(fig)
                
        except Exception as e:
            print(f"Error updating plot: {e}")
            
    def on_variable_changed(self, variable_name: str):
        """Handle variable selection change."""
        
        if variable_name and self.results is not None:
            # Update plot variables combo to match
            self.plot_variables_combo.setCurrentText(variable_name)
            self.update_plot()
            
    def refresh_display(self):
        """Refresh all displays."""
        
        if self.results is not None:
            self.update_data_table()
            self.update_statistics()
            self.update_plot()
            
    def export_results(self):
        """Export results to file."""
        
        if self.results is None:
            QMessageBox.warning(self, "No Data", "No results to export.")
            return
            
        # Get export file path
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "simulation_results.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    self.results.to_excel(file_path, index=False)
                else:
                    self.results.to_csv(file_path, index=False)
                    
                QMessageBox.information(self, "Export Complete", f"Results exported to:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export results:\n{str(e)}")
                
    def get_selected_variable(self) -> Optional[str]:
        """Get currently selected variable."""
        return self.variable_combo.currentText() if self.variable_combo.currentText() else None
        
    def clear_results(self):
        """Clear all results and reset display."""
        
        self.results = None
        self.model = None
        self.plotter = None
        
        # Hide tabs and show no results message
        self.tab_widget.hide()
        self.no_results_label.show()
        
        # Clear displays
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        self.stats_text.clear()
        self.variable_combo.clear()
        self.plot_variables_combo.clear()
