import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    """Handles data loading, preprocessing, and regridding operations."""
    
    def __init__(self):
        self.target_crs = "EPSG:4326"  # WGS84
        self.india_bounds = {
            'lat_min': 6.0, 'lat_max': 37.0,
            'lon_min': 68.0, 'lon_max': 97.0
        }
    
    def load_netcdf_data(self, file_path):
        """Load NetCDF data from file or file-like object."""
        try:
            if hasattr(file_path, 'read'):
                # File-like object (uploaded file)
                data = xr.open_dataset(file_path)
            else:
                # File path string
                data = xr.open_dataset(file_path)
            
            # Clip to India bounds
            data = self.clip_to_india(data)
            
            return data
        except Exception as e:
            raise Exception(f"Error loading NetCDF data: {str(e)}")
    
    def clip_to_india(self, data):
        """Clip dataset to India geographical bounds."""
        try:
            # Try to identify lat/lon coordinates
            lat_names = ['lat', 'latitude', 'y', 'rlat']
            lon_names = ['lon', 'longitude', 'x', 'rlon']
            
            lat_coord = None
            lon_coord = None
            
            for coord in data.coords:
                if coord.lower() in lat_names:
                    lat_coord = coord
                elif coord.lower() in lon_names:
                    lon_coord = coord
            
            if lat_coord and lon_coord:
                # Clip to India bounds
                data = data.sel(
                    {lat_coord: slice(self.india_bounds['lat_min'], self.india_bounds['lat_max']),
                     lon_coord: slice(self.india_bounds['lon_min'], self.india_bounds['lon_max'])}
                )
            
            return data
        except Exception as e:
            print(f"Warning: Could not clip to India bounds: {str(e)}")
            return data
    
    def regrid_data(self, imd_data, cmip6_data, target_resolution=0.25):
        """Regrid datasets to common resolution."""
        try:
            # Create target grid
            target_lat = np.arange(
                self.india_bounds['lat_min'],
                self.india_bounds['lat_max'] + target_resolution,
                target_resolution
            )
            target_lon = np.arange(
                self.india_bounds['lon_min'],
                self.india_bounds['lon_max'] + target_resolution,
                target_resolution
            )
            
            # Regrid IMD data
            imd_regridded = self._interpolate_to_grid(imd_data, target_lat, target_lon)
            
            # Regrid CMIP6 data
            cmip6_regridded = self._interpolate_to_grid(cmip6_data, target_lat, target_lon)
            
            return {
                'imd': imd_regridded,
                'cmip6': cmip6_regridded,
                'target_grid': {'lat': target_lat, 'lon': target_lon}
            }
        except Exception as e:
            raise Exception(f"Error regridding data: {str(e)}")
    
    def _interpolate_to_grid(self, data, target_lat, target_lon):
        """Interpolate data to target grid."""
        try:
            # Identify coordinate names
            lat_coord = self._get_coord_name(data, ['lat', 'latitude', 'y'])
            lon_coord = self._get_coord_name(data, ['lon', 'longitude', 'x'])
            
            if not lat_coord or not lon_coord:
                raise ValueError("Could not identify lat/lon coordinates")
            
            # Interpolate to target grid
            interpolated = data.interp(
                {lat_coord: target_lat, lon_coord: target_lon},
                method='linear'
            )
            
            # Rename coordinates to standard names
            interpolated = interpolated.rename({lat_coord: 'lat', lon_coord: 'lon'})
            
            return interpolated
        except Exception as e:
            raise Exception(f"Error interpolating data: {str(e)}")
    
    def _get_coord_name(self, data, possible_names):
        """Get coordinate name from possible variations."""
        for coord in data.coords:
            if coord.lower() in [name.lower() for name in possible_names]:
                return coord
        return None
    
    def calculate_seasonal_totals(self, regridded_data, season="JJAS"):
        """Calculate seasonal totals (default: JJAS - June to September)."""
        try:
            seasonal_data = {}
            
            for dataset_name, dataset in regridded_data.items():
                if dataset_name == 'target_grid':
                    continue
                
                # Group by season and calculate totals
                if 'time' in dataset.dims:
                    # Convert time to pandas datetime if needed
                    if not isinstance(dataset.time.values[0], (pd.Timestamp, np.datetime64)):
                        dataset['time'] = pd.to_datetime(dataset.time.values)
                    
                    # Filter for JJAS season (June to September)
                    seasonal = dataset.sel(
                        time=dataset.time.dt.month.isin([6, 7, 8, 9])
                    )
                    
                    # Check if data is in flux units (kg/m2/s or mm/s) and convert to daily
                    precip_vars = ['pr', 'precipitation', 'precip', 'rain', 'rainfall']
                    for var in dataset.data_vars:
                        if var.lower() in precip_vars:
                            if hasattr(dataset[var], 'units'):
                                units = dataset[var].attrs.get('units', '')
                                if 'kg m-2 s-1' in units or 'kg/m2/s' in units or 'mm/s' in units:
                                    # Convert from per second to per day
                                    seasonal[var] = seasonal[var] * 86400
                                    seasonal[var].attrs['units'] = 'mm/day'
                    
                    # Group by year and sum to get seasonal totals
                    seasonal_totals = seasonal.groupby('time.year').sum('time', skipna=True)
                    
                    # Add metadata
                    seasonal_totals.attrs['season'] = season
                    seasonal_totals.attrs['months'] = 'June-September'
                    
                    seasonal_data[dataset_name] = seasonal_totals
                else:
                    # If no time dimension, use data as is
                    seasonal_data[dataset_name] = dataset
            
            return seasonal_data
        except Exception as e:
            raise Exception(f"Error calculating seasonal totals: {str(e)}")
    
    def extract_time_period(self, data, start_year, end_year):
        """Extract data for specific time period."""
        try:
            if 'year' in data.coords:
                return data.sel(year=slice(start_year, end_year))
            elif 'time' in data.coords:
                return data.sel(time=slice(f"{start_year}-01-01", f"{end_year}-12-31"))
            else:
                return data
        except Exception as e:
            raise Exception(f"Error extracting time period: {str(e)}")
    
    def calculate_anomalies(self, data, baseline_data):
        """Calculate anomalies relative to baseline."""
        try:
            # Calculate baseline mean
            baseline_mean = baseline_data.mean(dim='year' if 'year' in baseline_data.dims else 'time')
            
            # Calculate anomalies
            anomalies = data - baseline_mean
            
            # Calculate percentage change
            percent_change = (anomalies / baseline_mean) * 100
            
            return {
                'absolute_anomalies': anomalies,
                'percent_change': percent_change,
                'baseline_mean': baseline_mean
            }
        except Exception as e:
            raise Exception(f"Error calculating anomalies: {str(e)}")
    
    def validate_data_quality(self, data):
        """Validate data quality and completeness."""
        quality_report = {}
        
        try:
            for var_name, var_data in data.data_vars.items():
                # Check for missing values
                missing_pct = (var_data.isnull().sum() / var_data.size * 100).values
                
                # Check for extreme values
                if var_data.dtype in [np.float32, np.float64]:
                    extreme_low = (var_data < var_data.quantile(0.001)).sum().values
                    extreme_high = (var_data > var_data.quantile(0.999)).sum().values
                else:
                    extreme_low = extreme_high = 0
                
                quality_report[var_name] = {
                    'missing_percentage': float(missing_pct),
                    'extreme_low_count': int(extreme_low),
                    'extreme_high_count': int(extreme_high),
                    'data_range': [float(var_data.min()), float(var_data.max())]
                }
            
            return quality_report
        except Exception as e:
            raise Exception(f"Error validating data quality: {str(e)}")
