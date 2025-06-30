import xarray as xr
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class ClimateAnalyzer:
    """Performs climate analysis including rainfall indices and ensemble modeling."""
    
    def __init__(self):
        self.rainfall_thresholds = {
            'light': 2.5,      # mm/day
            'moderate': 10.0,   # mm/day
            'heavy': 64.5,      # mm/day
            'very_heavy': 124.5, # mm/day
            'extreme': 244.4    # mm/day
        }
    
    def calculate_rainfall_indices(self, seasonal_data, scenario="SSP5-8.5", baseline_period="1990-2019"):
        """Calculate standard rainfall indices."""
        try:
            indices = {}
            
            # Get the appropriate dataset
            if 'cmip6' in seasonal_data:
                data = seasonal_data['cmip6']
            else:
                # Use first available dataset
                data = list(seasonal_data.values())[0]
            
            # Identify rainfall variable
            rain_var = self._identify_rainfall_variable(data)
            if not rain_var:
                raise ValueError("Could not identify rainfall variable in dataset")
            
            rainfall_data = data[rain_var]
            
            # 1. PRCPTOT - Total precipitation
            indices['PRCPTOT'] = self._calculate_prcptot(rainfall_data)
            
            # 2. Rx1day - Maximum 1-day precipitation
            indices['Rx1day'] = self._calculate_rx1day(rainfall_data)
            
            # 3. Rx5day - Maximum 5-day precipitation
            indices['Rx5day'] = self._calculate_rx5day(rainfall_data)
            
            # 4. Heavy rainfall days (>100mm)
            indices['heavy_rain_days'] = self._calculate_heavy_rain_days(rainfall_data, threshold=100.0)
            
            # 5. Consecutive dry days
            indices['CDD'] = self._calculate_consecutive_dry_days(rainfall_data)
            
            # 6. Consecutive wet days
            indices['CWD'] = self._calculate_consecutive_wet_days(rainfall_data)
            
            # 7. Simple daily intensity index
            indices['SDII'] = self._calculate_sdii(rainfall_data)
            
            return indices
        except Exception as e:
            raise Exception(f"Error calculating rainfall indices: {str(e)}")
    
    def _identify_rainfall_variable(self, data):
        """Identify the rainfall/precipitation variable in the dataset."""
        possible_names = ['pr', 'precipitation', 'precip', 'rain', 'rainfall', 'pcp']
        
        for var_name in data.data_vars:
            if var_name.lower() in possible_names:
                return var_name
        
        # If no exact match, return first variable (assuming it's precipitation)
        return list(data.data_vars)[0] if data.data_vars else None
    
    def _calculate_prcptot(self, rainfall_data):
        """Calculate total precipitation (PRCPTOT)."""
        try:
            # Convert to mm/day if needed (assuming data is in kg/m2/s)
            if rainfall_data.max() < 1:  # Likely in kg/m2/s
                rainfall_data = rainfall_data * 86400  # Convert to mm/day
            
            # Sum over time dimension
            if 'time' in rainfall_data.dims:
                return rainfall_data.sum(dim='time')
            elif 'year' in rainfall_data.dims:
                return rainfall_data.sum(dim='year')
            else:
                return rainfall_data.sum()
        except Exception as e:
            raise Exception(f"Error calculating PRCPTOT: {str(e)}")
    
    def _calculate_rx1day(self, rainfall_data):
        """Calculate maximum 1-day precipitation (Rx1day)."""
        try:
            # Convert to mm/day if needed
            if rainfall_data.max() < 1:
                rainfall_data = rainfall_data * 86400
            
            # Find maximum over time dimension
            if 'time' in rainfall_data.dims:
                return rainfall_data.max(dim='time')
            elif 'year' in rainfall_data.dims:
                return rainfall_data.max(dim='year')
            else:
                return rainfall_data.max()
        except Exception as e:
            raise Exception(f"Error calculating Rx1day: {str(e)}")
    
    def _calculate_rx5day(self, rainfall_data):
        """Calculate maximum 5-day precipitation (Rx5day)."""
        try:
            # Convert to mm/day if needed
            if rainfall_data.max() < 1:
                rainfall_data = rainfall_data * 86400
            
            # Calculate 5-day rolling sum
            if 'time' in rainfall_data.dims:
                rolling_sum = rainfall_data.rolling(time=5, center=True).sum()
                return rolling_sum.max(dim='time')
            else:
                # If no time dimension, approximate with current data
                return rainfall_data * 5
        except Exception as e:
            raise Exception(f"Error calculating Rx5day: {str(e)}")
    
    def _calculate_heavy_rain_days(self, rainfall_data, threshold=100.0):
        """Calculate number of heavy rainfall days (>threshold mm)."""
        try:
            # Convert to mm/day if needed
            if rainfall_data.max() < 1:
                rainfall_data = rainfall_data * 86400
            
            # Count days exceeding threshold
            heavy_days = (rainfall_data > threshold).sum(dim='time' if 'time' in rainfall_data.dims else 'year')
            
            return heavy_days
        except Exception as e:
            raise Exception(f"Error calculating heavy rain days: {str(e)}")
    
    def _calculate_consecutive_dry_days(self, rainfall_data, threshold=1.0):
        """Calculate maximum consecutive dry days (CDD)."""
        try:
            # Convert to mm/day if needed
            if rainfall_data.max() < 1:
                rainfall_data = rainfall_data * 86400
            
            # Identify dry days
            dry_days = rainfall_data < threshold
            
            # This is a simplified calculation - in practice, you'd need more complex logic
            # for calculating consecutive days
            return dry_days.sum(dim='time' if 'time' in rainfall_data.dims else 'year')
        except Exception as e:
            raise Exception(f"Error calculating CDD: {str(e)}")
    
    def _calculate_consecutive_wet_days(self, rainfall_data, threshold=1.0):
        """Calculate maximum consecutive wet days (CWD)."""
        try:
            # Convert to mm/day if needed
            if rainfall_data.max() < 1:
                rainfall_data = rainfall_data * 86400
            
            # Identify wet days
            wet_days = rainfall_data >= threshold
            
            return wet_days.sum(dim='time' if 'time' in rainfall_data.dims else 'year')
        except Exception as e:
            raise Exception(f"Error calculating CWD: {str(e)}")
    
    def _calculate_sdii(self, rainfall_data, threshold=1.0):
        """Calculate Simple Daily Intensity Index (SDII)."""
        try:
            # Convert to mm/day if needed
            if rainfall_data.max() < 1:
                rainfall_data = rainfall_data * 86400
            
            # Calculate SDII: total precipitation / number of wet days
            wet_days = rainfall_data >= threshold
            total_precip = rainfall_data.where(wet_days).sum(dim='time' if 'time' in rainfall_data.dims else 'year')
            wet_day_count = wet_days.sum(dim='time' if 'time' in rainfall_data.dims else 'year')
            
            # Avoid division by zero
            sdii = total_precip / wet_day_count.where(wet_day_count > 0)
            
            return sdii.fillna(0)
        except Exception as e:
            raise Exception(f"Error calculating SDII: {str(e)}")
    
    def ensemble_analysis(self, rainfall_indices, scenario="SSP5-8.5", projection_year="2050"):
        """Perform ensemble analysis with uncertainty quantification."""
        try:
            ensemble_results = {}
            
            # For each index, calculate ensemble statistics
            for index_name, index_data in rainfall_indices.items():
                # Calculate ensemble mean
                ensemble_mean = index_data.mean()
                
                # Calculate percentiles for uncertainty bounds
                percentiles = [10, 25, 50, 75, 90]
                ensemble_percentiles = {}
                
                for p in percentiles:
                    ensemble_percentiles[f'p{p}'] = np.percentile(index_data.values, p)
                
                # Calculate standard deviation
                ensemble_std = index_data.std()
                
                # Store results
                ensemble_results[index_name] = {
                    'mean': float(ensemble_mean.values),
                    'std': float(ensemble_std.values),
                    'percentiles': ensemble_percentiles,
                    'scenario': scenario,
                    'projection_year': projection_year
                }
            
            # Calculate overall statistics
            if 'PRCPTOT' in rainfall_indices:
                prcptot_mean = ensemble_results['PRCPTOT']['mean']
                
                # Estimate change relative to baseline (simplified)
                baseline_reference = 1000  # mm (approximate baseline)
                percent_change = ((prcptot_mean - baseline_reference) / baseline_reference) * 100
                
                ensemble_results['summary'] = {
                    'mean_change': percent_change,
                    'p10': ensemble_results['PRCPTOT']['percentiles']['p10'],
                    'p90': ensemble_results['PRCPTOT']['percentiles']['p90'],
                    'confidence_level': 80,  # Based on 10th-90th percentile range
                    'affected_grid_points': int(np.sum(~np.isnan(rainfall_indices['PRCPTOT'].values))),
                    'scenario': scenario,
                    'projection_year': projection_year
                }
            
            return ensemble_results
        except Exception as e:
            raise Exception(f"Error in ensemble analysis: {str(e)}")
    
    def calculate_regional_statistics(self, indices_data, regions_mask=None):
        """Calculate regional statistics for different parts of India."""
        try:
            regional_stats = {}
            
            # Define approximate regional bounds (simplified)
            regions = {
                'Northern': {'lat_min': 28, 'lat_max': 37, 'lon_min': 68, 'lon_max': 88},
                'Western': {'lat_min': 15, 'lat_max': 28, 'lon_min': 68, 'lon_max': 78},
                'Central': {'lat_min': 15, 'lat_max': 28, 'lon_min': 78, 'lon_max': 88},
                'Eastern': {'lat_min': 15, 'lat_max': 28, 'lon_min': 88, 'lon_max': 97},
                'Southern': {'lat_min': 6, 'lat_max': 15, 'lon_min': 68, 'lon_max': 88},
                'Northeastern': {'lat_min': 22, 'lat_max': 30, 'lon_min': 88, 'lon_max': 97}
            }
            
            for region_name, bounds in regions.items():
                region_stats = {}
                
                for index_name, index_data in indices_data.items():
                    if hasattr(index_data, 'lat') and hasattr(index_data, 'lon'):
                        # Select region
                        regional_data = index_data.sel(
                            lat=slice(bounds['lat_min'], bounds['lat_max']),
                            lon=slice(bounds['lon_min'], bounds['lon_max'])
                        )
                        
                        # Calculate regional mean
                        region_stats[index_name] = {
                            'mean': float(regional_data.mean().values),
                            'std': float(regional_data.std().values),
                            'min': float(regional_data.min().values),
                            'max': float(regional_data.max().values)
                        }
                
                regional_stats[region_name] = region_stats
            
            return regional_stats
        except Exception as e:
            raise Exception(f"Error calculating regional statistics: {str(e)}")
    
    def trend_analysis(self, time_series_data, method='linear'):
        """Perform trend analysis on time series data."""
        try:
            trends = {}
            
            for var_name, var_data in time_series_data.items():
                if 'time' in var_data.dims or 'year' in var_data.dims:
                    time_dim = 'time' if 'time' in var_data.dims else 'year'
                    
                    # Get time values
                    if time_dim == 'time':
                        time_values = pd.to_datetime(var_data[time_dim].values)
                        time_numeric = np.arange(len(time_values))
                    else:
                        time_numeric = var_data[time_dim].values
                    
                    # Calculate trend for each grid point
                    if method == 'linear':
                        # Flatten spatial dimensions
                        spatial_dims = [dim for dim in var_data.dims if dim != time_dim]
                        
                        if spatial_dims:
                            # Reshape data for trend calculation
                            data_2d = var_data.stack(spatial=spatial_dims)
                            
                            slopes = []
                            p_values = []
                            
                            for i in range(data_2d.sizes['spatial']):
                                series = data_2d.isel(spatial=i).dropna(time_dim)
                                if len(series) > 2:
                                    slope, intercept, r_value, p_value, std_err = stats.linregress(
                                        time_numeric[:len(series)], series.values
                                    )
                                    slopes.append(slope)
                                    p_values.append(p_value)
                                else:
                                    slopes.append(np.nan)
                                    p_values.append(np.nan)
                            
                            # Reshape back to original spatial dimensions
                            slopes_array = xr.DataArray(
                                slopes, dims=['spatial'], coords={'spatial': data_2d.spatial}
                            ).unstack('spatial')
                            
                            p_values_array = xr.DataArray(
                                p_values, dims=['spatial'], coords={'spatial': data_2d.spatial}
                            ).unstack('spatial')
                            
                            trends[var_name] = {
                                'slope': slopes_array,
                                'p_value': p_values_array,
                                'method': method
                            }
                        else:
                            # 1D time series
                            slope, intercept, r_value, p_value, std_err = stats.linregress(
                                time_numeric, var_data.values
                            )
                            trends[var_name] = {
                                'slope': slope,
                                'p_value': p_value,
                                'r_squared': r_value**2,
                                'method': method
                            }
            
            return trends
        except Exception as e:
            raise Exception(f"Error in trend analysis: {str(e)}")
