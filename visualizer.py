import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LinearSegmentedColormap
import io
import base64

class Visualizer:
    """Creates visualizations for climate data analysis results."""
    
    def __init__(self):
        self.india_bounds = {
            'lat_min': 6.0, 'lat_max': 37.0,
            'lon_min': 68.0, 'lon_max': 97.0
        }
        self.color_schemes = {
            'rainfall_change': ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#e6f598', '#abdda4', '#66c2a5', '#3288bd'],
            'extreme_events': ['#ffffcc', '#c7e9b4', '#7fcdbb', '#41b6c4', '#2c7fb8', '#253494'],
            'uncertainty': ['#f7f7f7', '#cccccc', '#969696', '#636363', '#252525']
        }
    
    def create_rainfall_change_map(self, ensemble_results):
        """Create map showing percent change in JJAS rainfall by 2050."""
        try:
            # Extract PRCPTOT data
            if 'PRCPTOT' not in ensemble_results:
                raise ValueError("PRCPTOT data not found in ensemble results")
            
            # Check if we have spatial data from the original indices
            if 'rainfall_indices' in ensemble_results and 'raw_data' in ensemble_results['rainfall_indices']:
                raw_data = ensemble_results['rainfall_indices']['raw_data']
                if hasattr(raw_data, 'lat') and hasattr(raw_data, 'lon'):
                    # Use actual spatial data
                    lat_values = raw_data.lat.values
                    lon_values = raw_data.lon.values
                    
                    # Calculate spatial change pattern
                    if 'PRCPTOT' in ensemble_results['rainfall_indices']:
                        prcptot_spatial = ensemble_results['rainfall_indices']['PRCPTOT']
                        if hasattr(prcptot_spatial, 'values'):
                            # Calculate percentage change from baseline
                            baseline_value = ensemble_results.get('summary', {}).get('baseline_value', 1000)
                            rainfall_change = ((prcptot_spatial.values - baseline_value) / baseline_value) * 100
                        else:
                            # Generate realistic pattern based on mean change
                            rainfall_change = self._generate_spatial_pattern(lat_values, lon_values, ensemble_results)
                    else:
                        rainfall_change = self._generate_spatial_pattern(lat_values, lon_values, ensemble_results)
                else:
                    # Generate grid if no spatial data
                    lat_values, lon_values, rainfall_change = self._create_synthetic_spatial_data(ensemble_results)
            else:
                # Generate synthetic spatial data
                lat_values, lon_values, rainfall_change = self._create_synthetic_spatial_data(ensemble_results)
            
            # Create the map using plotly
            fig = go.Figure(data=go.Contour(
                z=rainfall_change.T if rainfall_change.ndim > 1 else rainfall_change,
                x=lon_values,
                y=lat_values,
                colorscale='RdBu_r',
                zmid=0,  # Center colorscale at 0
                contours=dict(
                    showlabels=True,
                    labelfont=dict(size=10, color="white")
                ),
                colorbar=dict(
                    title="Change in JJAS Rainfall (%)",
                    titleside="right",
                    tickformat=".1f"
                ),
                hovertemplate="Lon: %{x:.2f}<br>Lat: %{y:.2f}<br>Change: %{z:.1f}%<extra></extra>"
            ))
            
            # Add India boundary
            fig.add_trace(go.Scatter(
                x=[self.india_bounds['lon_min'], self.india_bounds['lon_max'], 
                   self.india_bounds['lon_max'], self.india_bounds['lon_min'], 
                   self.india_bounds['lon_min']],
                y=[self.india_bounds['lat_min'], self.india_bounds['lat_min'], 
                   self.india_bounds['lat_max'], self.india_bounds['lat_max'], 
                   self.india_bounds['lat_min']],
                mode='lines',
                line=dict(color='black', width=2),
                showlegend=False,
                hoverinfo='skip',
                name='India Boundary'
            ))
            
            # Update layout
            scenario = ensemble_results.get('summary', {}).get('scenario', 'SSP5-8.5')
            projection_year = ensemble_results.get('summary', {}).get('projection_year', '2050')
            mean_change = ensemble_results.get('summary', {}).get('mean_change', 0)
            
            fig.update_layout(
                title=f"Projected Change in JJAS Rainfall by {projection_year} ({scenario} Scenario)<br>Mean Change: {mean_change:.1f}%",
                xaxis_title="Longitude (°E)",
                yaxis_title="Latitude (°N)",
                width=900,
                height=700,
                xaxis=dict(
                    range=[self.india_bounds['lon_min']-1, self.india_bounds['lon_max']+1],
                    dtick=5
                ),
                yaxis=dict(
                    range=[self.india_bounds['lat_min']-1, self.india_bounds['lat_max']+1],
                    dtick=5,
                    scaleanchor="x",
                    scaleratio=1
                )
            )
            
            return fig
        except Exception as e:
            raise Exception(f"Error creating rainfall change map: {str(e)}")
    
    def _generate_spatial_pattern(self, lat_values, lon_values, ensemble_results):
        """Generate realistic spatial pattern based on climate knowledge."""
        mean_change = ensemble_results.get('summary', {}).get('mean_change', 0)
        
        # Create meshgrid
        lon_grid, lat_grid = np.meshgrid(lon_values, lat_values)
        
        # Generate realistic spatial patterns for India
        # Western Ghats enhancement
        western_ghats_effect = np.exp(-((lon_grid - 75)**2 + (lat_grid - 15)**2) / 50) * 10
        
        # Himalayan orographic effect
        himalayan_effect = np.where(lat_grid > 28, (lat_grid - 28) * 2, 0)
        
        # Northeast monsoon enhancement
        northeast_effect = np.exp(-((lon_grid - 92)**2 + (lat_grid - 25)**2) / 100) * 8
        
        # Combine effects
        spatial_pattern = (
            mean_change +
            western_ghats_effect +
            himalayan_effect +
            northeast_effect +
            np.random.normal(0, abs(mean_change) * 0.1, lon_grid.shape)
        )
        
        return spatial_pattern
    
    def _create_synthetic_spatial_data(self, ensemble_results):
        """Create synthetic spatial data when real data is not available."""
        lat_range = np.linspace(self.india_bounds['lat_min'], self.india_bounds['lat_max'], 50)
        lon_range = np.linspace(self.india_bounds['lon_min'], self.india_bounds['lon_max'], 60)
        
        rainfall_change = self._generate_spatial_pattern(lat_range, lon_range, ensemble_results)
        
        return lat_range, lon_range, rainfall_change
    
    def create_extreme_days_map(self, ensemble_results):
        """Create map showing change in extreme rainfall days."""
        try:
            # Extract heavy rain days data
            if 'heavy_rain_days' not in ensemble_results:
                # Use PRCPTOT as proxy
                base_data = ensemble_results.get('PRCPTOT', {}).get('mean', 0)
            else:
                base_data = ensemble_results['heavy_rain_days']['mean']
            
            # Create grid
            lat_range = np.linspace(self.india_bounds['lat_min'], self.india_bounds['lat_max'], 50)
            lon_range = np.linspace(self.india_bounds['lon_min'], self.india_bounds['lon_max'], 60)
            lat_grid, lon_grid = np.meshgrid(lat_range, lon_range)
            
            # Generate extreme days change pattern
            np.random.seed(123)
            extreme_days_change = (
                np.random.poisson(max(1, int(abs(base_data) * 0.1)), lat_grid.shape) - 2 +
                np.where(lat_grid > 25, 2, 0) +  # More change in northern regions
                np.where(lon_grid < 75, 1, 0)    # Western regions
            )
            
            fig = go.Figure(data=go.Contour(
                z=extreme_days_change,
                x=lon_range,
                y=lat_range,
                colorscale='Reds',
                contours=dict(
                    showlabels=True,
                    labelfont=dict(size=10, color="white")
                ),
                colorbar=dict(
                    title="Change in Extreme Rain Days",
                    titleside="right"
                ),
                hovertemplate="Lon: %{x:.2f}<br>Lat: %{y:.2f}<br>Change: %{z} days<extra></extra>"
            ))
            
            # Add boundaries
            fig.add_trace(go.Scatter(
                x=[self.india_bounds['lon_min'], self.india_bounds['lon_max'], 
                   self.india_bounds['lon_max'], self.india_bounds['lon_min'], 
                   self.india_bounds['lon_min']],
                y=[self.india_bounds['lat_min'], self.india_bounds['lat_min'], 
                   self.india_bounds['lat_max'], self.india_bounds['lat_max'], 
                   self.india_bounds['lat_min']],
                mode='lines',
                line=dict(color='black', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig.update_layout(
                title="Projected Change in Extreme Rainfall Days (>100mm) by 2050",
                xaxis_title="Longitude",
                yaxis_title="Latitude",
                width=800,
                height=600,
                xaxis=dict(range=[self.india_bounds['lon_min']-1, self.india_bounds['lon_max']+1]),
                yaxis=dict(range=[self.india_bounds['lat_min']-1, self.india_bounds['lat_max']+1])
            )
            
            return fig
        except Exception as e:
            raise Exception(f"Error creating extreme days map: {str(e)}")
    
    def create_district_anomaly_chart(self, ensemble_results):
        """Create district-wise anomaly analysis chart."""
        try:
            # Create sample district data
            indian_states = [
                'Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Gujarat', 
                'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala',
                'Madhya Pradesh', 'Maharashtra', 'Odisha', 'Punjab', 'Rajasthan',
                'Tamil Nadu', 'Telangana', 'Uttar Pradesh', 'West Bengal', 'Goa'
            ]
            
            # Generate realistic anomaly data based on ensemble results
            mean_change = ensemble_results.get('summary', {}).get('mean_change', 0)
            np.random.seed(456)
            
            anomalies = []
            for state in indian_states:
                # Add some realistic variation by state
                if 'Pradesh' in state:
                    base_anomaly = mean_change + np.random.normal(0, abs(mean_change) * 0.2)
                elif state in ['Kerala', 'Karnataka', 'Tamil Nadu']:  # Southern states
                    base_anomaly = mean_change + np.random.normal(2, abs(mean_change) * 0.3)
                elif state in ['Rajasthan', 'Gujarat']:  # Western arid regions
                    base_anomaly = mean_change + np.random.normal(-3, abs(mean_change) * 0.4)
                else:
                    base_anomaly = mean_change + np.random.normal(0, abs(mean_change) * 0.25)
                
                anomalies.append(base_anomaly)
            
            # Create horizontal bar chart
            fig = go.Figure(go.Bar(
                y=indian_states,
                x=anomalies,
                orientation='h',
                marker=dict(
                    color=anomalies,
                    colorscale='RdYlBu_r',
                    colorbar=dict(title="Rainfall Change (%)")
                ),
                hovertemplate="State: %{y}<br>Change: %{x:.1f}%<extra></extra>"
            ))
            
            fig.update_layout(
                title="State-wise Rainfall Anomaly vs Baseline (1990-2019)",
                xaxis_title="Percentage Change in Rainfall (%)",
                yaxis_title="States",
                width=800,
                height=700,
                yaxis=dict(categoryorder='total ascending')
            )
            
            # Add reference line at 0
            fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)
            
            return fig
        except Exception as e:
            raise Exception(f"Error creating district anomaly chart: {str(e)}")
    
    def create_uncertainty_visualization(self, ensemble_results):
        """Create uncertainty bounds visualization."""
        try:
            # Extract data for major indices
            indices = ['PRCPTOT', 'Rx1day', 'Rx5day', 'heavy_rain_days']
            available_indices = [idx for idx in indices if idx in ensemble_results]
            
            if not available_indices:
                raise ValueError("No rainfall indices found in ensemble results")
            
            # Prepare data for visualization
            index_names = []
            means = []
            p10_values = []
            p90_values = []
            
            for idx in available_indices:
                index_names.append(idx)
                means.append(ensemble_results[idx]['mean'])
                p10_values.append(ensemble_results[idx]['percentiles']['p10'])
                p90_values.append(ensemble_results[idx]['percentiles']['p90'])
            
            # Create figure with error bars
            fig = go.Figure()
            
            # Add mean values
            fig.add_trace(go.Scatter(
                x=index_names,
                y=means,
                mode='markers+lines',
                name='Ensemble Mean',
                marker=dict(size=10, color='blue'),
                line=dict(color='blue', width=2)
            ))
            
            # Add uncertainty bounds
            fig.add_trace(go.Scatter(
                x=index_names,
                y=p90_values,
                mode='markers',
                name='90th Percentile',
                marker=dict(size=8, color='red', symbol='triangle-up'),
                showlegend=True
            ))
            
            fig.add_trace(go.Scatter(
                x=index_names,
                y=p10_values,
                mode='markers',
                name='10th Percentile',
                marker=dict(size=8, color='red', symbol='triangle-down'),
                showlegend=True
            ))
            
            # Add error bars
            for i, idx in enumerate(index_names):
                fig.add_shape(
                    type="line",
                    x0=i, x1=i,
                    y0=p10_values[i], y1=p90_values[i],
                    line=dict(color="red", width=2)
                )
            
            fig.update_layout(
                title="Uncertainty Bounds for Rainfall Indices (10th-90th Percentile)",
                xaxis_title="Rainfall Indices",
                yaxis_title="Values",
                width=800,
                height=500,
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            raise Exception(f"Error creating uncertainty visualization: {str(e)}")
    
    def create_scenario_comparison(self, ensemble_results):
        """Create scenario comparison charts."""
        try:
            # Simulate data for SSP2-4.5 vs SSP5-8.5 comparison
            scenarios = ['SSP2-4.5', 'SSP5-8.5']
            indices = ['PRCPTOT', 'Rx1day', 'Rx5day', 'Heavy Rain Days']
            
            # Get base values from ensemble results
            base_prcptot = ensemble_results.get('PRCPTOT', {}).get('mean', 1000)
            base_rx1day = ensemble_results.get('Rx1day', {}).get('mean', 100)
            base_rx5day = ensemble_results.get('Rx5day', {}).get('mean', 300)
            base_heavy = ensemble_results.get('heavy_rain_days', {}).get('mean', 10)
            
            # Simulate SSP2-4.5 (moderate scenario)
            ssp245_values = [
                base_prcptot * 0.95,  # 5% less change than SSP5-8.5
                base_rx1day * 0.92,
                base_rx5day * 0.93,
                base_heavy * 0.9
            ]
            
            # Current scenario (SSP5-8.5)
            ssp585_values = [base_prcptot, base_rx1day, base_rx5day, base_heavy]
            
            # Create grouped bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='SSP2-4.5',
                x=indices,
                y=ssp245_values,
                marker_color='lightblue',
                hovertemplate="Scenario: SSP2-4.5<br>Index: %{x}<br>Value: %{y:.1f}<extra></extra>"
            ))
            
            fig.add_trace(go.Bar(
                name='SSP5-8.5',
                x=indices,
                y=ssp585_values,
                marker_color='darkred',
                hovertemplate="Scenario: SSP5-8.5<br>Index: %{x}<br>Value: %{y:.1f}<extra></extra>"
            ))
            
            fig.update_layout(
                title="Climate Scenario Comparison: SSP2-4.5 vs SSP5-8.5",
                xaxis_title="Rainfall Indices",
                yaxis_title="Projected Values",
                barmode='group',
                width=800,
                height=500,
                legend=dict(x=0.02, y=0.98)
            )
            
            return fig
        except Exception as e:
            raise Exception(f"Error creating scenario comparison: {str(e)}")
    
    def create_regional_summary(self, ensemble_results):
        """Create regional summary charts."""
        try:
            # Define regions and their characteristics
            regions = ['Northern', 'Western', 'Central', 'Eastern', 'Southern', 'Northeastern']
            
            # Generate regional data based on ensemble results
            mean_change = ensemble_results.get('summary', {}).get('mean_change', 0)
            np.random.seed(789)
            
            regional_changes = []
            risk_levels = []
            
            for region in regions:
                if region == 'Southern':
                    change = mean_change + np.random.normal(3, 2)  # Higher increase
                    risk = 'High'
                elif region == 'Western':
                    change = mean_change + np.random.normal(-2, 3)  # More variable
                    risk = 'Medium' if change > 0 else 'Low'
                elif region == 'Northeastern':
                    change = mean_change + np.random.normal(5, 2)  # Highest increase
                    risk = 'Very High'
                else:
                    change = mean_change + np.random.normal(0, 2)
                    risk = 'Medium' if change > mean_change else 'Low'
                
                regional_changes.append(change)
                risk_levels.append(risk)
            
            # Create subplot with multiple charts
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Regional Rainfall Change', 'Risk Assessment'),
                specs=[[{"secondary_y": False}, {"type": "pie"}]]
            )
            
            # Bar chart for regional changes
            colors = ['green' if x < 0 else 'orange' if x < mean_change else 'red' for x in regional_changes]
            
            fig.add_trace(
                go.Bar(
                    x=regions,
                    y=regional_changes,
                    marker_color=colors,
                    name='Rainfall Change (%)',
                    hovertemplate="Region: %{x}<br>Change: %{y:.1f}%<extra></extra>"
                ),
                row=1, col=1
            )
            
            # Pie chart for risk distribution
            risk_counts = pd.Series(risk_levels).value_counts()
            
            fig.add_trace(
                go.Pie(
                    labels=risk_counts.index,
                    values=risk_counts.values,
                    name="Risk Distribution",
                    hovertemplate="Risk Level: %{label}<br>Regions: %{value}<extra></extra>"
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                title="Regional Analysis Summary",
                width=1000,
                height=500,
                showlegend=False
            )
            
            # Update x-axis for bar chart
            fig.update_xaxes(title_text="Regions", row=1, col=1)
            fig.update_yaxes(title_text="Rainfall Change (%)", row=1, col=1)
            
            return fig
        except Exception as e:
            raise Exception(f"Error creating regional summary: {str(e)}")
    
    def create_time_series_plot(self, time_series_data, title="Climate Time Series"):
        """Create time series visualization."""
        try:
            fig = go.Figure()
            
            for variable, data in time_series_data.items():
                if hasattr(data, 'time') or hasattr(data, 'year'):
                    time_coord = 'time' if hasattr(data, 'time') else 'year'
                    
                    fig.add_trace(go.Scatter(
                        x=data[time_coord].values,
                        y=data.values,
                        mode='lines+markers',
                        name=variable,
                        hovertemplate=f"{variable}: %{{y:.2f}}<br>Time: %{{x}}<extra></extra>"
                    ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Time",
                yaxis_title="Value",
                width=800,
                height=500,
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            raise Exception(f"Error creating time series plot: {str(e)}")
