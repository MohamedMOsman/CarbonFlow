"""
Data loading and handling utilities for spatiotemporal system dynamics modeling.

This module provides classes and functions for loading, validating, and managing
multi-dimensional data with unit awareness and spatial/temporal indexing.
"""

import numpy as np
import pandas as pd
import xarray as xr
from typing import Union, Dict, List, Optional, Tuple, Any
from pathlib import Path
import warnings

from ..core.units import Quantity, unit_registry


class SpatioTemporalData:
    """
    Container for spatiotemporal data with unit awareness.
    
    Manages multi-dimensional data arrays with spatial and temporal coordinates,
    maintaining unit information and providing convenient access methods.
    """
    
    def __init__(self, data, coords=None, dims=None, units=None, name=None, attrs=None):
        """
        Initialize spatiotemporal data container.
        
        Parameters:
        -----------
        data : array-like
            The data values
        coords : dict, optional
            Coordinate arrays for each dimension
        dims : list, optional
            Names of dimensions
        units : str or pint.Unit, optional
            Units of the data
        name : str, optional
            Name of the data variable
        attrs : dict, optional
            Additional metadata attributes
        """
        self.name = name or "data"
        self.attrs = attrs or {}
        
        # Create xarray DataArray for efficient multi-dimensional operations
        self._data_array = xr.DataArray(
            data=data,
            coords=coords,
            dims=dims,
            name=self.name,
            attrs=self.attrs
        )
        
        # Store units information
        if units:
            self._quantity = Quantity(self._data_array.values, units)
            self.attrs['units'] = str(units)
        else:
            self._quantity = None
    
    @property
    def data(self):
        """Access to underlying data array."""
        return self._data_array
    
    @property
    def values(self):
        """Access to data values."""
        return self._data_array.values
    
    @property
    def coords(self):
        """Access to coordinates."""
        return self._data_array.coords
    
    @property
    def dims(self):
        """Access to dimension names."""
        return self._data_array.dims
    
    @property
    def units(self):
        """Get units of the data."""
        if self._quantity:
            return self._quantity.units
        return None
    
    @property
    def shape(self):
        """Shape of the data array."""
        return self._data_array.shape
    
    def sel(self, **kwargs):
        """Select data by coordinate values."""
        selected = self._data_array.sel(**kwargs)
        return SpatioTemporalData(
            data=selected.values,
            coords=dict(selected.coords),
            dims=list(selected.dims),
            units=self.units,
            name=self.name,
            attrs=self.attrs
        )
    
    def isel(self, **kwargs):
        """Select data by integer indices."""
        selected = self._data_array.isel(**kwargs)
        return SpatioTemporalData(
            data=selected.values,
            coords=dict(selected.coords),
            dims=list(selected.dims),
            units=self.units,
            name=self.name,
            attrs=self.attrs
        )
    
    def to_units(self, target_units):
        """Convert data to different units."""
        if not self._quantity:
            raise ValueError("No units defined for this data")
        
        converted = self._quantity.to(target_units)
        return SpatioTemporalData(
            data=converted.magnitude,
            coords=dict(self.coords),
            dims=list(self.dims),
            units=target_units,
            name=self.name,
            attrs=self.attrs
        )
    
    def resample_time(self, freq, method='mean'):
        """Resample data along time dimension."""
        if 'time' not in self.dims:
            raise ValueError("No time dimension found for resampling")
        
        resampled = self._data_array.resample(time=freq)
        
        if method == 'mean':
            result = resampled.mean()
        elif method == 'sum':
            result = resampled.sum()
        elif method == 'max':
            result = resampled.max()
        elif method == 'min':
            result = resampled.min()
        else:
            raise ValueError(f"Unknown resampling method: {method}")
        
        return SpatioTemporalData(
            data=result.values,
            coords=dict(result.coords),
            dims=list(result.dims),
            units=self.units,
            name=self.name,
            attrs=self.attrs
        )


class DataLoader:
    """
    Flexible data loader for various spatiotemporal data formats.
    
    Supports loading from CSV, NetCDF, GeoTIFF, and other common formats
    used in climate and environmental modeling.
    """
    
    def __init__(self):
        self.supported_formats = {
            '.csv': self._load_csv,
            '.nc': self._load_netcdf,
            '.nc4': self._load_netcdf,
            '.tif': self._load_geotiff,
            '.tiff': self._load_geotiff,
            '.json': self._load_json
        }
    
    def load(self, filepath, **kwargs):
        """
        Load data from file with automatic format detection.
        
        Parameters:
        -----------
        filepath : str or Path
            Path to the data file
        **kwargs : dict
            Additional arguments passed to specific loader
            
        Returns:
        --------
        SpatioTemporalData : Loaded data container
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        suffix = filepath.suffix.lower()
        
        if suffix not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {suffix}")
        
        loader_func = self.supported_formats[suffix]
        return loader_func(filepath, **kwargs)
    
    def _load_csv(self, filepath, time_col=None, spatial_cols=None, 
                  value_col=None, units=None, **kwargs):
        """Load data from CSV file."""
        df = pd.read_csv(filepath, **kwargs)
        
        # Auto-detect columns if not specified
        if time_col is None:
            time_candidates = ['time', 'date', 'datetime', 'timestamp']
            time_col = next((col for col in df.columns if col.lower() in time_candidates), None)
        
        if spatial_cols is None:
            spatial_candidates = [['lat', 'lon'], ['latitude', 'longitude'], ['x', 'y']]
            for candidates in spatial_candidates:
                if all(col in df.columns for col in candidates):
                    spatial_cols = candidates
                    break
        
        if value_col is None:
            # Use first numeric column that's not time or spatial
            exclude_cols = [time_col] + (spatial_cols or [])
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            value_col = next((col for col in numeric_cols if col not in exclude_cols), None)
        
        if value_col is None:
            raise ValueError("Could not identify value column")
        
        # Create coordinates dictionary
        coords = {}
        dims = []
        
        if time_col and time_col in df.columns:
            coords['time'] = pd.to_datetime(df[time_col])
            dims.append('time')
        
        if spatial_cols:
            for col in spatial_cols:
                if col in df.columns:
                    coords[col] = df[col].values
                    dims.append(col)
        
        # Extract data values
        data = df[value_col].values
        
        # Reshape data if needed (this is simplified - real implementation would be more complex)
        if len(dims) > 1:
            # For multi-dimensional data, we'd need more sophisticated reshaping
            pass
        
        return SpatioTemporalData(
            data=data,
            coords=coords,
            dims=dims,
            units=units,
            name=value_col
        )
    
    def _load_netcdf(self, filepath, var_name=None, **kwargs):
        """Load data from NetCDF file."""
        try:
            import xarray as xr
        except ImportError:
            raise ImportError("xarray is required for NetCDF support")
        
        ds = xr.open_dataset(filepath, **kwargs)
        
        if var_name is None:
            # Use first data variable
            data_vars = list(ds.data_vars.keys())
            if not data_vars:
                raise ValueError("No data variables found in NetCDF file")
            var_name = data_vars[0]
        
        da = ds[var_name]
        
        # Extract units from attributes
        units = da.attrs.get('units', None)
        
        return SpatioTemporalData(
            data=da.values,
            coords=dict(da.coords),
            dims=list(da.dims),
            units=units,
            name=var_name,
            attrs=dict(da.attrs)
        )
    
    def _load_geotiff(self, filepath, **kwargs):
        """Load data from GeoTIFF file."""
        try:
            import rasterio
        except ImportError:
            raise ImportError("rasterio is required for GeoTIFF support")
        
        with rasterio.open(filepath) as src:
            data = src.read()
            transform = src.transform
            crs = src.crs
            
            # Create spatial coordinates
            height, width = data.shape[-2:]
            x_coords = np.linspace(transform.c, transform.c + width * transform.a, width)
            y_coords = np.linspace(transform.f, transform.f + height * transform.e, height)
            
            coords = {'x': x_coords, 'y': y_coords}
            dims = ['y', 'x']
            
            # Handle multi-band data
            if data.ndim == 3:
                coords['band'] = np.arange(data.shape[0])
                dims = ['band'] + dims
            else:
                data = data.squeeze()
            
            attrs = {
                'crs': str(crs),
                'transform': transform,
                'source_file': str(filepath)
            }
            
            return SpatioTemporalData(
                data=data,
                coords=coords,
                dims=dims,
                name=filepath.stem,
                attrs=attrs
            )
    
    def _load_json(self, filepath, **kwargs):
        """Load data from JSON file (simplified implementation)."""
        import json
        
        with open(filepath, 'r') as f:
            data_dict = json.load(f)
        
        # This is a simplified implementation
        # Real implementation would handle various JSON structures
        if 'data' in data_dict:
            data = np.array(data_dict['data'])
            coords = data_dict.get('coords', {})
            dims = data_dict.get('dims', [])
            units = data_dict.get('units', None)
            name = data_dict.get('name', filepath.stem)
            attrs = data_dict.get('attrs', {})
            
            return SpatioTemporalData(
                data=data,
                coords=coords,
                dims=dims,
                units=units,
                name=name,
                attrs=attrs
            )
        else:
            raise ValueError("Invalid JSON structure for spatiotemporal data")


class DataValidator:
    """
    Validator for spatiotemporal data quality and consistency.
    
    Provides methods to check data integrity, unit consistency,
    and spatial/temporal coverage.
    """
    
    def __init__(self):
        pass
    
    def validate_data(self, data: SpatioTemporalData) -> Dict[str, Any]:
        """
        Comprehensive validation of spatiotemporal data.
        
        Parameters:
        -----------
        data : SpatioTemporalData
            Data to validate
            
        Returns:
        --------
        dict : Validation results with issues and statistics
        """
        results = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check for missing values
        if np.isnan(data.values).any():
            nan_count = np.isnan(data.values).sum()
            total_count = data.values.size
            nan_percentage = (nan_count / total_count) * 100
            
            results['warnings'].append(
                f"Data contains {nan_count} NaN values ({nan_percentage:.2f}%)"
            )
            results['statistics']['nan_count'] = nan_count
            results['statistics']['nan_percentage'] = nan_percentage
        
        # Check for infinite values
        if np.isinf(data.values).any():
            inf_count = np.isinf(data.values).sum()
            results['issues'].append(f"Data contains {inf_count} infinite values")
            results['valid'] = False
        
        # Check coordinate consistency
        for dim in data.dims:
            if dim in data.coords:
                coord = data.coords[dim]
                if len(coord) != data.shape[data.dims.index(dim)]:
                    results['issues'].append(
                        f"Coordinate '{dim}' length doesn't match data dimension"
                    )
                    results['valid'] = False
        
        # Basic statistics
        results['statistics'].update({
            'shape': data.shape,
            'min_value': float(np.nanmin(data.values)),
            'max_value': float(np.nanmax(data.values)),
            'mean_value': float(np.nanmean(data.values)),
            'std_value': float(np.nanstd(data.values))
        })
        
        return results
    
    def check_temporal_coverage(self, data: SpatioTemporalData, 
                              expected_start=None, expected_end=None) -> Dict[str, Any]:
        """Check temporal coverage and continuity."""
        if 'time' not in data.dims:
            return {'valid': False, 'issue': 'No time dimension found'}
        
        time_coord = data.coords['time']
        
        results = {
            'valid': True,
            'start_time': time_coord[0],
            'end_time': time_coord[-1],
            'time_steps': len(time_coord),
            'issues': []
        }
        
        # Check expected coverage
        if expected_start and time_coord[0] > pd.to_datetime(expected_start):
            results['issues'].append(f"Data starts later than expected: {time_coord[0]}")
        
        if expected_end and time_coord[-1] < pd.to_datetime(expected_end):
            results['issues'].append(f"Data ends earlier than expected: {time_coord[-1]}")
        
        # Check for gaps (simplified)
        if len(time_coord) > 1:
            time_diffs = np.diff(pd.to_datetime(time_coord))
            if len(np.unique(time_diffs)) > 1:
                results['issues'].append("Irregular time intervals detected")
        
        results['valid'] = len(results['issues']) == 0
        return results
