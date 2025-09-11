"""
Advanced plotting functions for multidimensional system dynamics models.

This module provides specialized visualization tools for multidimensional
population models and climate adaptation analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
import xarray as xr
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D


class MultidimensionalPlotter:
    """Advanced plotting class for multidimensional system dynamics results."""
    
    def __init__(self, style='seaborn-v0_8'):
        """Initialize the plotter with specified style."""
        plt.style.use(style)
        sns.set_palette("husl")
        self.default_figsize = (12, 8)
    

    


    
    def plot_multidimensional_heatmap(self, data: np.ndarray,
                                     dimension_labels: List[str],
                                     title: str = "Multidimensional Data Heatmap",
                                     figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a generic heatmap for multidimensional data.

        Parameters:
        -----------
        data : np.ndarray
            2D array of data to visualize
        dimension_labels : list
            Labels for each dimension
        title : str
            Plot title
        figsize : tuple, optional
            Figure size

        Returns:
        --------
        plt.Figure : The created figure
        """
        if figsize is None:
            figsize = (10, 8)

        fig, ax = plt.subplots(figsize=figsize)

        im = ax.imshow(data, cmap='viridis', aspect='auto')
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Set labels
        if len(dimension_labels) >= 2:
            ax.set_xlabel(dimension_labels[1])
            ax.set_ylabel(dimension_labels[0])

        # Add colorbar
        plt.colorbar(im, ax=ax, shrink=0.8, label='Value')

        # Add value annotations if data is small enough
        if data.shape[0] <= 10 and data.shape[1] <= 10:
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    text = ax.text(j, i, f'{data[i, j]:.2f}',
                                 ha="center", va="center", color="white", fontweight='bold')

        plt.tight_layout()
        return fig

    def plot_scenario_comparison(self, baseline_results: pd.DataFrame,
                               comparison_results: pd.DataFrame,
                               variables: List[str],
                               figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Create a generic scenario comparison plot.

        Parameters:
        -----------
        baseline_results : pd.DataFrame
            Baseline scenario results
        comparison_results : pd.DataFrame
            Comparison scenario results
        variables : list
            Variables to compare
        figsize : tuple, optional
            Figure size

        Returns:
        --------
        plt.Figure : The created figure
        """
        if figsize is None:
            figsize = (15, 10)

        n_vars = len(variables)
        cols = min(3, n_vars)
        rows = (n_vars + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        fig.suptitle('Scenario Comparison Dashboard', fontsize=16, fontweight='bold')

        if n_vars == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes if isinstance(axes, np.ndarray) else [axes]
        else:
            axes = axes.flatten()

        for i, var in enumerate(variables):
            if i >= len(axes):
                break

            if var in baseline_results.columns and var in comparison_results.columns:
                axes[i].plot(baseline_results['time'], baseline_results[var],
                           label='Baseline', linewidth=2, color='blue', alpha=0.8)
                axes[i].plot(comparison_results['time'], comparison_results[var],
                           label='Comparison', linewidth=2, color='red', alpha=0.8)
                axes[i].set_title(f'{var} Comparison')
                axes[i].set_xlabel('Time')
                axes[i].set_ylabel(var)
                axes[i].legend()
                axes[i].grid(True, alpha=0.3)

        # Hide unused subplots
        for i in range(len(variables), len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()
        return fig
