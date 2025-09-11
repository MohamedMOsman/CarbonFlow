"""
Analysis and visualization tools for system dynamics models.

This module provides comprehensive plotting and analysis capabilities
for system dynamics simulation results, including time series plots,
phase diagrams, sensitivity analysis, and spatial visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Union, Tuple, Any
import warnings

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    # Create dummy classes for type hints when plotly is not available
    class DummyFigure:
        pass
    go = type('go', (), {'Figure': DummyFigure})
    px = None
    make_subplots = None
    PLOTLY_AVAILABLE = False
    warnings.warn("Plotly not available. Some interactive plotting features will be disabled.")

from ..engine.system import SystemModel
from ..data.loader import SpatioTemporalData


class SystemPlotter:
    """
    Main plotting class for system dynamics models and results.
    
    Provides methods for creating various types of plots including
    time series, phase diagrams, and model structure visualizations.
    """
    
    def __init__(self, model: Optional[SystemModel] = None, style: str = 'seaborn'):
        """
        Initialize system plotter.
        
        Parameters:
        -----------
        model : SystemModel, optional
            System dynamics model to plot
        style : str
            Matplotlib style to use
        """
        self.model = model
        self.style = style
        
        # Set plotting style
        if style in plt.style.available:
            plt.style.use(style)
        
        # Color palettes
        self.colors = {
            'stocks': '#2E86AB',
            'flows': '#A23B72',
            'auxiliaries': '#F18F01',
            'connectors': '#C73E1D'
        }
        
        self.figure_size = (12, 8)
    
    def plot_time_series(self, results: pd.DataFrame, 
                        variables: Optional[List[str]] = None,
                        title: str = "System Dynamics Time Series",
                        save_path: Optional[str] = None,
                        interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        Plot time series of model variables.
        
        Parameters:
        -----------
        results : pd.DataFrame
            Simulation results with time column
        variables : list, optional
            Variables to plot (if None, plots all except time)
        title : str
            Plot title
        save_path : str, optional
            Path to save the plot
        interactive : bool
            Whether to create interactive plot (requires plotly)
            
        Returns:
        --------
        Figure : matplotlib or plotly figure
        """
        if 'time' not in results.columns:
            raise ValueError("Results must contain 'time' column")
        
        if variables is None:
            variables = [col for col in results.columns if col != 'time']
        
        if interactive:
            if PLOTLY_AVAILABLE:
                return self._plot_time_series_interactive(results, variables, title, save_path)
            else:
                warnings.warn("Interactive plotting requested but Plotly is not available. Creating static plot instead.")

        return self._plot_time_series_static(results, variables, title, save_path)
    
    def _plot_time_series_static(self, results: pd.DataFrame, variables: List[str],
                               title: str, save_path: Optional[str]) -> plt.Figure:
        """Create static time series plot with matplotlib."""
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        for i, var in enumerate(variables):
            if var in results.columns:
                ax.plot(results['time'], results[var], 
                       label=var, linewidth=2, alpha=0.8)
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.set_title(title)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _plot_time_series_interactive(self, results: pd.DataFrame, variables: List[str],
                                    title: str, save_path: Optional[str]) -> go.Figure:
        """Create interactive time series plot with plotly."""
        if not PLOTLY_AVAILABLE:
            raise RuntimeError("Plotly is not available. Cannot create interactive plots.")

        fig = go.Figure()

        for var in variables:
            if var in results.columns:
                fig.add_trace(go.Scatter(
                    x=results['time'],
                    y=results[var],
                    mode='lines',
                    name=var,
                    line=dict(width=2)
                ))

        fig.update_layout(
            title=title,
            xaxis_title='Time',
            yaxis_title='Value',
            hovermode='x unified',
            width=800,
            height=600
        )

        if save_path:
            fig.write_html(save_path)

        return fig
    
    def plot_phase_diagram(self, results: pd.DataFrame, x_var: str, y_var: str,
                          title: Optional[str] = None,
                          save_path: Optional[str] = None) -> plt.Figure:
        """
        Create phase diagram (state space plot) of two variables.
        
        Parameters:
        -----------
        results : pd.DataFrame
            Simulation results
        x_var : str
            Variable for x-axis
        y_var : str
            Variable for y-axis
        title : str, optional
            Plot title
        save_path : str, optional
            Path to save the plot
            
        Returns:
        --------
        plt.Figure : matplotlib figure
        """
        if x_var not in results.columns or y_var not in results.columns:
            raise ValueError(f"Variables {x_var} and {y_var} must be in results")
        
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        # Plot trajectory
        ax.plot(results[x_var], results[y_var], 'b-', alpha=0.7, linewidth=2)
        
        # Mark start and end points
        ax.plot(results[x_var].iloc[0], results[y_var].iloc[0], 
               'go', markersize=8, label='Start')
        ax.plot(results[x_var].iloc[-1], results[y_var].iloc[-1], 
               'ro', markersize=8, label='End')
        
        # Add arrows to show direction
        n_arrows = 5
        arrow_indices = np.linspace(0, len(results)-2, n_arrows, dtype=int)
        for i in arrow_indices:
            dx = results[x_var].iloc[i+1] - results[x_var].iloc[i]
            dy = results[y_var].iloc[i+1] - results[y_var].iloc[i]
            ax.arrow(results[x_var].iloc[i], results[y_var].iloc[i], 
                    dx, dy, head_width=0.02, head_length=0.02, 
                    fc='black', ec='black', alpha=0.6)
        
        ax.set_xlabel(x_var)
        ax.set_ylabel(y_var)
        ax.set_title(title or f'Phase Diagram: {y_var} vs {x_var}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_model_structure(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Visualize model structure showing stocks, flows, and connections.
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save the plot
            
        Returns:
        --------
        plt.Figure : matplotlib figure
        """
        if not self.model:
            raise ValueError("Model must be provided to plot structure")
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # This is a simplified structure plot
        # A full implementation would use network layout algorithms
        
        # Position elements
        positions = {}
        y_stock = 0.7
        y_flow = 0.3
        
        # Position stocks
        stock_x = np.linspace(0.1, 0.9, len(self.model.stocks))
        for i, (stock_id, stock) in enumerate(self.model.stocks.items()):
            positions[stock_id] = (stock_x[i], y_stock)
            ax.scatter(stock_x[i], y_stock, s=200, c=self.colors['stocks'], 
                      marker='s', label='Stock' if i == 0 else "")
            ax.text(stock_x[i], y_stock + 0.05, stock.name, 
                   ha='center', va='bottom', fontsize=10)
        
        # Position flows
        flow_x = np.linspace(0.1, 0.9, len(self.model.flows))
        for i, (flow_id, flow) in enumerate(self.model.flows.items()):
            positions[flow_id] = (flow_x[i], y_flow)
            ax.scatter(flow_x[i], y_flow, s=150, c=self.colors['flows'], 
                      marker='>', label='Flow' if i == 0 else "")
            ax.text(flow_x[i], y_flow - 0.05, flow.name, 
                   ha='center', va='top', fontsize=10)
        
        # Draw connections (simplified)
        for element_id, deps in self.model.dependencies.items():
            if element_id in positions:
                x1, y1 = positions[element_id]
                for dep_id in deps:
                    if dep_id in positions:
                        x2, y2 = positions[dep_id]
                        ax.arrow(x2, y2, x1-x2, y1-y2, 
                               head_width=0.02, head_length=0.02,
                               fc='gray', ec='gray', alpha=0.6)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(f'Model Structure: {self.model.name}')
        ax.legend()
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_sensitivity_analysis(self, sensitivity_results: Dict[str, Any],
                                save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot sensitivity analysis results.
        
        Parameters:
        -----------
        sensitivity_results : dict
            Results from sensitivity analysis
        save_path : str, optional
            Path to save the plot
            
        Returns:
        --------
        plt.Figure : matplotlib figure
        """
        # This would create sensitivity analysis plots
        # Placeholder implementation
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        ax.text(0.5, 0.5, 'Sensitivity Analysis Plot\n(Implementation pending)', 
               ha='center', va='center', fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig


class SpatialPlotter:
    """
    Specialized plotter for spatially-explicit system dynamics models.
    
    Handles visualization of spatial data, maps, and spatiotemporal patterns.
    """
    
    def __init__(self):
        """Initialize spatial plotter."""
        self.figure_size = (12, 8)
    
    def plot_spatial_field(self, data: SpatioTemporalData, 
                          time_index: Optional[int] = None,
                          title: Optional[str] = None,
                          save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot spatial field at a specific time.
        
        Parameters:
        -----------
        data : SpatioTemporalData
            Spatial data to plot
        time_index : int, optional
            Time index to plot (if None, uses last time)
        title : str, optional
            Plot title
        save_path : str, optional
            Path to save the plot
            
        Returns:
        --------
        plt.Figure : matplotlib figure
        """
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        # Extract spatial data
        if 'time' in data.dims and time_index is not None:
            plot_data = data.isel(time=time_index)
        else:
            plot_data = data
        
        # Create spatial plot (simplified - assumes 2D spatial data)
        if len(plot_data.dims) == 2:
            im = ax.imshow(plot_data.values, origin='lower', aspect='auto')
            plt.colorbar(im, ax=ax, label=f'{data.name} ({data.units})')
        
        ax.set_title(title or f'Spatial Field: {data.name}')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig


class TemporalPlotter:
    """
    Specialized plotter for temporal analysis of system dynamics models.
    
    Focuses on time-based patterns, trends, and temporal statistics.
    """
    
    def __init__(self):
        """Initialize temporal plotter."""
        self.figure_size = (12, 6)
    
    def plot_temporal_statistics(self, results: pd.DataFrame,
                                variables: Optional[List[str]] = None,
                                save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot temporal statistics (mean, std, trends) for variables.
        
        Parameters:
        -----------
        results : pd.DataFrame
            Simulation results
        variables : list, optional
            Variables to analyze
        save_path : str, optional
            Path to save the plot
            
        Returns:
        --------
        plt.Figure : matplotlib figure
        """
        if variables is None:
            variables = [col for col in results.columns if col != 'time']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        # Plot 1: Time series
        for var in variables:
            if var in results.columns:
                axes[0].plot(results['time'], results[var], label=var)
        axes[0].set_title('Time Series')
        axes[0].set_xlabel('Time')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Distribution
        for var in variables:
            if var in results.columns:
                axes[1].hist(results[var], alpha=0.6, label=var, bins=20)
        axes[1].set_title('Value Distributions')
        axes[1].set_xlabel('Value')
        axes[1].set_ylabel('Frequency')
        axes[1].legend()
        
        # Plot 3: Correlation matrix
        corr_data = results[variables].corr()
        sns.heatmap(corr_data, annot=True, ax=axes[2], cmap='coolwarm', center=0)
        axes[2].set_title('Variable Correlations')
        
        # Plot 4: Trends (simplified)
        axes[3].text(0.5, 0.5, 'Trend Analysis\n(Implementation pending)', 
                    ha='center', va='center')
        axes[3].set_title('Trend Analysis')
        axes[3].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
