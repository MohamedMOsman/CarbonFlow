"""
Simulation Controller for Model Execution

This module provides simulation control and execution functionality,
integrating with the existing sd_toolkit simulation engine.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QApplication

# Add sd_toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'sd_toolkit'))

from sd_toolkit.engine.system import SystemModel
from sd_toolkit.analysis.plotting import SystemPlotter
from yaml_integration.yaml_loader import GuiModel


class SimulationWorker(QThread):
    """Worker thread for running simulations without blocking the GUI."""
    
    # Signals
    progress_updated = pyqtSignal(int)  # Progress percentage
    status_updated = pyqtSignal(str)   # Status message
    simulation_finished = pyqtSignal(object)  # Results
    simulation_error = pyqtSignal(str)  # Error message
    
    def __init__(self, sd_model: SystemModel, time_horizon: float = None, dt: float = None):
        super().__init__()
        
        self.sd_model = sd_model
        self.time_horizon = time_horizon
        self.dt = dt
        self.should_stop = False
        
    def run(self):
        """Run the simulation in the worker thread."""
        
        try:
            self.status_updated.emit("Initializing simulation...")
            self.progress_updated.emit(0)
            
            # Validate model
            validation = self.sd_model.validate_model()
            if not validation['valid']:
                error_msg = f"Model validation failed: {', '.join(validation['errors'])}"
                self.simulation_error.emit(error_msg)
                return
                
            self.status_updated.emit("Model validated successfully")
            self.progress_updated.emit(10)
            
            if self.should_stop:
                return
                
            # Set simulation parameters
            time_horizon = self.time_horizon or self.sd_model.time_horizon
            dt = self.dt or self.sd_model.dt
            
            self.status_updated.emit(f"Running simulation (T={time_horizon}, dt={dt})...")
            self.progress_updated.emit(20)
            
            # Run simulation with progress updates
            results = self.run_simulation_with_progress(time_horizon, dt)
            
            if self.should_stop:
                return
                
            self.status_updated.emit("Simulation completed successfully")
            self.progress_updated.emit(100)
            
            # Emit results
            self.simulation_finished.emit(results)
            
        except Exception as e:
            error_msg = f"Simulation error: {str(e)}"
            self.simulation_error.emit(error_msg)
            
    def run_simulation_with_progress(self, time_horizon: float, dt: float) -> pd.DataFrame:
        """Run simulation with progress updates."""
        
        # For now, use the standard simulate method
        # In a more advanced implementation, we could modify the simulation loop
        # to emit progress updates during execution
        
        results = self.sd_model.simulate(
            time_horizon=time_horizon,
            dt=dt,
            method='euler'
        )
        
        # Simulate progress updates (since we can't easily modify the core simulation)
        import time
        for i in range(20, 90, 10):
            if self.should_stop:
                break
            time.sleep(0.1)  # Small delay to show progress
            self.progress_updated.emit(i)
            
        return results
        
    def stop(self):
        """Request simulation stop."""
        self.should_stop = True


class SimulationController(QObject):
    """
    Controller for managing simulation execution and results.
    
    Provides:
    - Simulation execution with progress monitoring
    - Start/stop/pause controls
    - Results management and visualization
    - Scenario parameter switching
    """
    
    # Signals
    simulation_started = pyqtSignal()
    simulation_finished = pyqtSignal(object)  # Results
    simulation_error = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)  # Progress percentage and status
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Current state
        self.gui_model = None
        self.sd_model = None
        self.current_results = None
        self.is_running = False
        
        # Simulation worker
        self.simulation_worker = None
        
        # Progress dialog
        self.progress_dialog = None
        
        # Plotting
        self.plotter = None
        
    def set_model(self, gui_model: GuiModel, sd_model: SystemModel):
        """Set the models for simulation."""
        self.gui_model = gui_model
        self.sd_model = sd_model
        
        # Create plotter
        if sd_model:
            self.plotter = SystemPlotter(sd_model)
            
    def can_run_simulation(self) -> tuple[bool, str]:
        """Check if simulation can be run."""
        
        if not self.sd_model:
            return False, "No model loaded"
            
        if self.is_running:
            return False, "Simulation already running"
            
        # Validate model
        validation = self.sd_model.validate_model()
        if not validation['valid']:
            return False, f"Model validation failed: {', '.join(validation['errors'])}"
            
        return True, "Ready to run"
        
    def start_simulation(self, time_horizon: float = None, dt: float = None):
        """Start simulation execution."""
        
        # Check if we can run
        can_run, message = self.can_run_simulation()
        if not can_run:
            self.simulation_error.emit(message)
            return
            
        # Set running state
        self.is_running = True
        
        # Create and configure worker
        self.simulation_worker = SimulationWorker(self.sd_model, time_horizon, dt)
        
        # Connect worker signals
        self.simulation_worker.progress_updated.connect(self.on_progress_updated)
        self.simulation_worker.status_updated.connect(self.on_status_updated)
        self.simulation_worker.simulation_finished.connect(self.on_simulation_finished)
        self.simulation_worker.simulation_error.connect(self.on_simulation_error)
        
        # Create progress dialog
        self.create_progress_dialog()
        
        # Start worker
        self.simulation_worker.start()
        
        # Emit started signal
        self.simulation_started.emit()
        
    def stop_simulation(self):
        """Stop running simulation."""
        
        if self.simulation_worker and self.simulation_worker.isRunning():
            self.simulation_worker.stop()
            self.simulation_worker.wait(3000)  # Wait up to 3 seconds
            
            if self.simulation_worker.isRunning():
                self.simulation_worker.terminate()
                
        self.is_running = False
        
        if self.progress_dialog:
            self.progress_dialog.close()
            
    def create_progress_dialog(self):
        """Create progress dialog for simulation."""
        
        self.progress_dialog = QProgressDialog("Initializing simulation...", "Cancel", 0, 100)
        self.progress_dialog.setWindowTitle("Running Simulation")
        self.progress_dialog.setModal(True)
        self.progress_dialog.setMinimumDuration(0)
        
        # Connect cancel button
        self.progress_dialog.canceled.connect(self.stop_simulation)
        
        self.progress_dialog.show()
        
    def on_progress_updated(self, percentage: int):
        """Handle progress updates."""
        
        if self.progress_dialog:
            self.progress_dialog.setValue(percentage)
            
        self.progress_updated.emit(percentage, "")
        
    def on_status_updated(self, status: str):
        """Handle status updates."""
        
        if self.progress_dialog:
            self.progress_dialog.setLabelText(status)
            
        self.progress_updated.emit(-1, status)
        
    def on_simulation_finished(self, results: pd.DataFrame):
        """Handle simulation completion."""
        
        self.is_running = False
        self.current_results = results
        
        if self.progress_dialog:
            self.progress_dialog.close()
            
        # Emit finished signal
        self.simulation_finished.emit(results)
        
    def on_simulation_error(self, error_message: str):
        """Handle simulation errors."""
        
        self.is_running = False
        
        if self.progress_dialog:
            self.progress_dialog.close()
            
        # Emit error signal
        self.simulation_error.emit(error_message)
        
    def get_results(self) -> Optional[pd.DataFrame]:
        """Get current simulation results."""
        return self.current_results
        
    def export_results(self, file_path: str, format: str = 'csv'):
        """Export simulation results to file."""
        
        if not self.current_results:
            raise ValueError("No results to export")
            
        if format.lower() == 'csv':
            self.current_results.to_csv(file_path, index=False)
        elif format.lower() == 'excel':
            self.current_results.to_excel(file_path, index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
    def create_results_plot(self, variables: list = None, plot_type: str = 'time_series'):
        """Create a plot of simulation results."""
        
        if not self.current_results or not self.plotter:
            return None
            
        if plot_type == 'time_series':
            return self.plotter.plot_time_series(self.current_results, variables)
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")
            
    def get_results_summary(self) -> Dict[str, Any]:
        """Get summary statistics of simulation results."""
        
        if not self.current_results:
            return {}
            
        summary = {
            'time_range': (self.current_results['time'].min(), self.current_results['time'].max()),
            'variables': list(self.current_results.columns),
            'data_points': len(self.current_results),
            'statistics': {}
        }
        
        # Calculate statistics for numeric columns
        numeric_cols = self.current_results.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col != 'time':
                summary['statistics'][col] = {
                    'min': self.current_results[col].min(),
                    'max': self.current_results[col].max(),
                    'mean': self.current_results[col].mean(),
                    'std': self.current_results[col].std(),
                    'final_value': self.current_results[col].iloc[-1]
                }
                
        return summary
        
    def update_scenario_parameters(self, new_parameters: Dict[str, Any]):
        """Update scenario parameters for next simulation."""
        
        if not self.gui_model:
            return
            
        # Update GUI model constants
        self.gui_model.constants.update(new_parameters)
        
        # Rebuild sd_toolkit model with new parameters
        # This would require re-creating the model from the GUI model
        # For now, we'll just update the constants
        
    def cleanup(self):
        """Clean up resources."""
        
        if self.simulation_worker and self.simulation_worker.isRunning():
            self.stop_simulation()
            
        if self.progress_dialog:
            self.progress_dialog.close()
