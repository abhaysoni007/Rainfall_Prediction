import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class DemoDataGenerator:
    """Generate realistic demonstration climate data for testing."""
    
    def __init__(self):
        self.india_bounds = {
            'lat_min': 6.0, 'lat_max': 37.0,
            'lon_min': 68.0, 'lon_max': 97.0
        }
    
    def generate_imd_demo_data(self, start_year=1981, end_year=2010):
        """Generate realistic IMD-like historical rainfall data."""
        # Create coordinate arrays
        lat = np.arange(self.india_bounds['lat_min'], self.india_bounds['lat_max'], 0.25)
        lon = np.arange(self.india_bounds['lon_min'], self.india_bounds['lon_max'], 0.25)
        
        # Create time array (daily data for JJAS months)
        dates = []
        for year in range(start_year, end_year + 1):
            for month in [6, 7, 8, 9]:  # JJAS months
                if month in [6, 9]:
                    days = 30
                else:
                    days = 31
                for day in range(1, days + 1):
                    dates.append(datetime(year, month, day))
        
        time = pd.DatetimeIndex(dates)
        
        # Create meshgrid
        lon_grid, lat_grid = np.meshgrid(lon, lat)
        
        # Generate realistic rainfall patterns
        np.random.seed(42)
        
        # Base rainfall pattern (mm/day)
        # Western Ghats high rainfall
        western_ghats = np.exp(-((lon_grid - 75)**2 / 25 + (lat_grid - 15)**2 / 100)) * 30
        
        # Northeast monsoon
        northeast = np.exp(-((lon_grid - 92)**2 / 50 + (lat_grid - 25)**2 / 50)) * 25
        
        # Northwest dry region
        northwest_dry = np.exp(-((lon_grid - 72)**2 / 100 + (lat_grid - 28)**2 / 100)) * -10
        
        # Combine patterns
        base_pattern = 10 + western_ghats + northeast + northwest_dry
        base_pattern = np.maximum(base_pattern, 0)  # No negative rainfall
        
        # Create time-varying rainfall
        rainfall_data = np.zeros((len(time), len(lat), len(lon)))
        
        for i, date in enumerate(dates):
            # Seasonal variation
            month = date.month
            if month == 7 or month == 8:  # Peak monsoon
                seasonal_factor = 1.5
            elif month == 6:  # Early monsoon
                seasonal_factor = 0.8
            else:  # Late monsoon
                seasonal_factor = 1.0
            
            # Daily variation
            daily_variation = np.random.normal(1.0, 0.3)
            daily_variation = np.maximum(daily_variation, 0)
            
            # Spatial variation
            spatial_noise = np.random.normal(0, 0.2, base_pattern.shape)
            
            # Combine all factors
            rainfall_data[i] = base_pattern * seasonal_factor * daily_variation * (1 + spatial_noise)
            
            # Add occasional heavy rainfall events
            if np.random.random() < 0.1:  # 10% chance of heavy rainfall
                event_center_lat = np.random.uniform(lat.min(), lat.max())
                event_center_lon = np.random.uniform(lon.min(), lon.max())
                heavy_rain = np.exp(-((lon_grid - event_center_lon)**2 / 50 + 
                                     (lat_grid - event_center_lat)**2 / 50)) * 50
                rainfall_data[i] += heavy_rain
        
        # Create xarray dataset
        imd_data = xr.Dataset(
            {
                'rainfall': (['time', 'lat', 'lon'], rainfall_data),
            },
            coords={
                'time': time,
                'lat': lat,
                'lon': lon
            }
        )
        
        # Add attributes
        imd_data.attrs['title'] = 'IMD Gridded Rainfall Data (Demo)'
        imd_data.attrs['source'] = 'Demo data generator for climate analysis'
        imd_data.attrs['units'] = 'mm/day'
        imd_data['rainfall'].attrs['units'] = 'mm/day'
        imd_data['rainfall'].attrs['long_name'] = 'Daily Rainfall'
        
        return imd_data
    
    def generate_cmip6_demo_data(self, scenario='SSP5-8.5', start_year=2040, end_year=2060):
        """Generate realistic CMIP6-like projection data."""
        # Use same spatial grid as IMD data
        lat = np.arange(self.india_bounds['lat_min'], self.india_bounds['lat_max'], 0.25)
        lon = np.arange(self.india_bounds['lon_min'], self.india_bounds['lon_max'], 0.25)
        
        # Create time array
        dates = []
        for year in range(start_year, end_year + 1):
            for month in [6, 7, 8, 9]:  # JJAS months
                if month in [6, 9]:
                    days = 30
                else:
                    days = 31
                for day in range(1, days + 1):
                    dates.append(datetime(year, month, day))
        
        time = pd.DatetimeIndex(dates)
        
        # Create meshgrid
        lon_grid, lat_grid = np.meshgrid(lon, lat)
        
        # Generate future rainfall patterns with climate change signal
        np.random.seed(123)
        
        # Base pattern similar to historical but with changes
        # Enhanced Western Ghats rainfall
        western_ghats = np.exp(-((lon_grid - 75)**2 / 25 + (lat_grid - 15)**2 / 100)) * 35
        
        # Enhanced Northeast monsoon
        northeast = np.exp(-((lon_grid - 92)**2 / 50 + (lat_grid - 25)**2 / 50)) * 30
        
        # More severe northwest drying
        northwest_dry = np.exp(-((lon_grid - 72)**2 / 100 + (lat_grid - 28)**2 / 100)) * -15
        
        # Climate change signal
        if scenario == 'SSP5-8.5':
            change_factor = 1.15  # 15% increase overall
            extreme_factor = 1.3  # 30% increase in extremes
        else:  # SSP2-4.5
            change_factor = 1.08  # 8% increase overall
            extreme_factor = 1.15  # 15% increase in extremes
        
        # Combine patterns
        base_pattern = (10 + western_ghats + northeast + northwest_dry) * change_factor
        base_pattern = np.maximum(base_pattern, 0)
        
        # Create time-varying rainfall
        rainfall_data = np.zeros((len(time), len(lat), len(lon)))
        
        for i, date in enumerate(dates):
            # Seasonal variation
            month = date.month
            if month == 7 or month == 8:  # Peak monsoon
                seasonal_factor = 1.6  # Stronger peak
            elif month == 6:  # Early monsoon
                seasonal_factor = 0.7  # Delayed onset
            else:  # Late monsoon
                seasonal_factor = 1.1  # Extended monsoon
            
            # Daily variation with more extremes
            daily_variation = np.random.gamma(2, 0.5)  # More skewed distribution
            daily_variation = np.maximum(daily_variation, 0)
            
            # Spatial variation
            spatial_noise = np.random.normal(0, 0.25, base_pattern.shape)
            
            # Combine all factors
            rainfall_data[i] = base_pattern * seasonal_factor * daily_variation * (1 + spatial_noise)
            
            # Add more frequent extreme events
            if np.random.random() < 0.15:  # 15% chance of extreme rainfall
                event_center_lat = np.random.uniform(lat.min(), lat.max())
                event_center_lon = np.random.uniform(lon.min(), lon.max())
                extreme_rain = np.exp(-((lon_grid - event_center_lon)**2 / 40 + 
                                       (lat_grid - event_center_lat)**2 / 40)) * 80 * extreme_factor
                rainfall_data[i] += extreme_rain
        
        # Create xarray dataset
        cmip6_data = xr.Dataset(
            {
                'pr': (['time', 'lat', 'lon'], rainfall_data / 86400),  # Convert to kg/m2/s
            },
            coords={
                'time': time,
                'lat': lat,
                'lon': lon
            }
        )
        
        # Add attributes
        cmip6_data.attrs['title'] = f'CMIP6 Rainfall Projection ({scenario}) (Demo)'
        cmip6_data.attrs['source'] = 'Demo data generator for climate analysis'
        cmip6_data.attrs['scenario'] = scenario
        cmip6_data.attrs['model'] = 'Multi-Model Ensemble Mean'
        cmip6_data['pr'].attrs['units'] = 'kg m-2 s-1'
        cmip6_data['pr'].attrs['long_name'] = 'Precipitation'
        cmip6_data['pr'].attrs['standard_name'] = 'precipitation_flux'
        
        return cmip6_data
    
    def save_demo_files(self):
        """Save demo data as NetCDF files."""
        # Generate IMD data
        imd_data = self.generate_imd_demo_data()
        imd_data.to_netcdf('imd_demo_data.nc')
        
        # Generate CMIP6 data
        cmip6_data = self.generate_cmip6_demo_data()
        cmip6_data.to_netcdf('cmip6_demo_data.nc')
        
        return {
            'imd_file': 'imd_demo_data.nc',
            'cmip6_file': 'cmip6_demo_data.nc'
        }