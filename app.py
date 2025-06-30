import streamlit as st
import pandas as pd
import numpy as np
import xarray as xr
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime
import os
import io
import base64
from data_processor import DataProcessor
from climate_analyzer import ClimateAnalyzer
from visualizer import Visualizer
from report_generator import ReportGenerator
from utils import Utils

# Configure page
st.set_page_config(
    page_title="Climate Data Analysis Pipeline",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()
if 'climate_analyzer' not in st.session_state:
    st.session_state.climate_analyzer = ClimateAnalyzer()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = Visualizer()
if 'report_generator' not in st.session_state:
    st.session_state.report_generator = ReportGenerator()
if 'utils' not in st.session_state:
    st.session_state.utils = Utils()

def main():
    st.title("🌧️ Climate Data Analysis Pipeline")
    st.markdown("### Forecasting Indian Rainfall Patterns in 2050 using CMIP6 Data")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Analysis Module",
        ["Data Upload & Processing", "Climate Analysis", "Visualizations", "Executive Summary", "Export Results"]
    )
    
    if page == "Data Upload & Processing":
        data_processing_page()
    elif page == "Climate Analysis":
        climate_analysis_page()
    elif page == "Visualizations":
        visualization_page()
    elif page == "Executive Summary":
        executive_summary_page()
    elif page == "Export Results":
        export_page()

def data_processing_page():
    st.header("📊 Data Upload & Processing")
    
    # Add demo mode option
    demo_mode = st.checkbox("Use demo data for testing", value=False)
    
    if demo_mode:
        st.info("Demo mode enabled - using synthetic climate data for demonstration")
        if st.button("Generate Demo Data"):
            with st.spinner("Generating demonstration data..."):
                try:
                    from demo_data_generator import DemoDataGenerator
                    generator = DemoDataGenerator()
                    
                    # Generate demo data
                    imd_data = generator.generate_imd_demo_data()
                    cmip6_data = generator.generate_cmip6_demo_data()
                    
                    # Store in session state
                    st.session_state.imd_processed = imd_data
                    st.session_state.cmip6_processed = cmip6_data
                    
                    st.success("✅ Demo data generated successfully!")
                    
                    # Display data info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**IMD Demo Data (1981-2010)**")
                        st.write(f"Variables: {list(imd_data.data_vars.keys())}")
                        st.write(f"Grid points: {len(imd_data.lat)} x {len(imd_data.lon)}")
                        st.write(f"Time steps: {len(imd_data.time)}")
                    
                    with col2:
                        st.write("**CMIP6 Demo Data (SSP5-8.5)**")
                        st.write(f"Variables: {list(cmip6_data.data_vars.keys())}")
                        st.write(f"Grid points: {len(cmip6_data.lat)} x {len(cmip6_data.lon)}")
                        st.write(f"Time steps: {len(cmip6_data.time)}")
                    
                except Exception as e:
                    st.error(f"Error generating demo data: {str(e)}")
    else:
        # Data upload section
        st.subheader("1. Upload Climate Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**IMD Historical Data (1981-2010)**")
            imd_file = st.file_uploader(
                "Upload IMD NetCDF file",
                type=['nc', 'netcdf'],
                key="imd_upload"
            )
            
            if imd_file is not None:
                try:
                    # Process IMD data
                    with st.spinner("Processing IMD data..."):
                        imd_data = st.session_state.data_processor.load_netcdf_data(imd_file)
                        st.session_state.imd_processed = imd_data
                        st.success("✅ IMD data loaded successfully!")
                        
                        # Display data info
                        st.write("**Data Information:**")
                        st.write(f"Variables: {list(imd_data.data_vars.keys())}")
                        st.write(f"Dimensions: {dict(imd_data.dims)}")
                        st.write(f"Time range: {imd_data.time.min().values} to {imd_data.time.max().values}")
                        
                except Exception as e:
                    st.error(f"Error processing IMD data: {str(e)}")
        
        with col2:
            st.write("**CMIP6 Projection Data**")
            cmip6_file = st.file_uploader(
                "Upload CMIP6 NetCDF file",
                type=['nc', 'netcdf'],
                key="cmip6_upload"
            )
            
            if cmip6_file is not None:
                try:
                    # Process CMIP6 data
                    with st.spinner("Processing CMIP6 data..."):
                        cmip6_data = st.session_state.data_processor.load_netcdf_data(cmip6_file)
                        st.session_state.cmip6_processed = cmip6_data
                        st.success("✅ CMIP6 data loaded successfully!")
                        
                        # Display data info
                        st.write("**Data Information:**")
                        st.write(f"Variables: {list(cmip6_data.data_vars.keys())}")
                        st.write(f"Dimensions: {dict(cmip6_data.dims)}")
                        st.write(f"Time range: {cmip6_data.time.min().values} to {cmip6_data.time.max().values}")
                        
                except Exception as e:
                    st.error(f"Error processing CMIP6 data: {str(e)}")
    
    # Data preprocessing section
    st.subheader("2. Data Preprocessing")
    
    if st.button("Start Preprocessing"):
        if hasattr(st.session_state, 'imd_processed') and hasattr(st.session_state, 'cmip6_processed'):
            with st.spinner("Preprocessing data..."):
                try:
                    # Regrid to common grid
                    st.info("Regridding to 0.25°x0.25° grid...")
                    regridded_data = st.session_state.data_processor.regrid_data(
                        st.session_state.imd_processed,
                        st.session_state.cmip6_processed,
                        target_resolution=0.25
                    )
                    st.session_state.regridded_data = regridded_data
                    
                    # Calculate seasonal totals
                    st.info("Calculating seasonal (JJAS) totals...")
                    seasonal_data = st.session_state.data_processor.calculate_seasonal_totals(regridded_data)
                    st.session_state.seasonal_data = seasonal_data
                    
                    st.success("✅ Preprocessing completed successfully!")
                    
                    # Display preprocessing summary
                    st.write("**Preprocessing Summary:**")
                    st.write("- Data regridded to 0.25°x0.25° resolution")
                    st.write("- Seasonal (JJAS) totals calculated")
                    st.write("- Data harmonized for ensemble analysis")
                    
                except Exception as e:
                    st.error(f"Error during preprocessing: {str(e)}")
        else:
            st.warning("Please upload both IMD and CMIP6 data files first.")

def climate_analysis_page():
    st.header("🌡️ Climate Analysis")
    
    if not hasattr(st.session_state, 'seasonal_data'):
        st.warning("Please complete data preprocessing first.")
        return
    
    # Analysis configuration
    st.subheader("Analysis Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        scenario = st.selectbox("Select SSP Scenario", ["SSP2-4.5", "SSP5-8.5"])
    
    with col2:
        baseline_period = st.selectbox("Baseline Period", ["1990-2019", "1981-2010"])
    
    with col3:
        projection_year = st.selectbox("Projection Year", ["2050", "2080", "2100"])
    
    # Rainfall indices calculation
    st.subheader("Rainfall Indices Calculation")
    
    if st.button("Calculate Rainfall Indices"):
        with st.spinner("Calculating rainfall indices..."):
            try:
                indices = st.session_state.climate_analyzer.calculate_rainfall_indices(
                    st.session_state.seasonal_data,
                    scenario=scenario,
                    baseline_period=baseline_period
                )
                st.session_state.rainfall_indices = indices
                
                # Display indices summary
                st.success("✅ Rainfall indices calculated successfully!")
                
                # Create tabs for different indices
                tab1, tab2, tab3, tab4 = st.tabs(["PRCPTOT", "Rx1day", "Rx5day", "Heavy Rain Days"])
                
                with tab1:
                    st.write("**Total Precipitation (PRCPTOT)**")
                    if 'PRCPTOT' in indices:
                        st.dataframe(indices['PRCPTOT'].to_dataframe().head())
                
                with tab2:
                    st.write("**Maximum 1-day Precipitation (Rx1day)**")
                    if 'Rx1day' in indices:
                        st.dataframe(indices['Rx1day'].to_dataframe().head())
                
                with tab3:
                    st.write("**Maximum 5-day Precipitation (Rx5day)**")
                    if 'Rx5day' in indices:
                        st.dataframe(indices['Rx5day'].to_dataframe().head())
                
                with tab4:
                    st.write("**Heavy Rainfall Days (>100mm)**")
                    if 'heavy_rain_days' in indices:
                        st.dataframe(indices['heavy_rain_days'].to_dataframe().head())
                
            except Exception as e:
                st.error(f"Error calculating indices: {str(e)}")
    
    # Ensemble analysis
    st.subheader("Ensemble Analysis")
    
    if st.button("Perform Ensemble Analysis"):
        if hasattr(st.session_state, 'rainfall_indices'):
            with st.spinner("Performing ensemble analysis..."):
                try:
                    ensemble_results = st.session_state.climate_analyzer.ensemble_analysis(
                        st.session_state.rainfall_indices,
                        scenario=scenario,
                        projection_year=projection_year
                    )
                    st.session_state.ensemble_results = ensemble_results
                    
                    st.success("✅ Ensemble analysis completed!")
                    
                    # Display ensemble statistics
                    st.write("**Ensemble Statistics:**")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Mean Rainfall Change (%)",
                            f"{ensemble_results.get('mean_change', 0):.1f}%",
                            delta=f"{ensemble_results.get('mean_change', 0):.1f}%"
                        )
                    
                    with col2:
                        st.metric(
                            "10th Percentile (%)",
                            f"{ensemble_results.get('p10', 0):.1f}%"
                        )
                    
                    with col3:
                        st.metric(
                            "90th Percentile (%)",
                            f"{ensemble_results.get('p90', 0):.1f}%"
                        )
                    
                except Exception as e:
                    st.error(f"Error in ensemble analysis: {str(e)}")
        else:
            st.warning("Please calculate rainfall indices first.")

def visualization_page():
    st.header("📈 Visualizations")
    
    if not hasattr(st.session_state, 'ensemble_results'):
        st.warning("Please complete climate analysis first.")
        return
    
    # Visualization options
    st.subheader("Select Visualizations")
    
    viz_options = st.multiselect(
        "Choose visualizations to generate:",
        [
            "JJAS Rainfall Change Map",
            "Extreme Rainfall Days Change",
            "District-wise Anomaly Analysis",
            "Uncertainty Bounds Visualization",
            "Scenario Comparison Charts",
            "Regional Summary Charts"
        ],
        default=["JJAS Rainfall Change Map", "Extreme Rainfall Days Change"]
    )
    
    if st.button("Generate Visualizations"):
        with st.spinner("Generating visualizations..."):
            try:
                for viz_type in viz_options:
                    st.subheader(f"📊 {viz_type}")
                    
                    if viz_type == "JJAS Rainfall Change Map":
                        fig = st.session_state.visualizer.create_rainfall_change_map(
                            st.session_state.ensemble_results
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Extreme Rainfall Days Change":
                        fig = st.session_state.visualizer.create_extreme_days_map(
                            st.session_state.ensemble_results
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "District-wise Anomaly Analysis":
                        fig = st.session_state.visualizer.create_district_anomaly_chart(
                            st.session_state.ensemble_results
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Uncertainty Bounds Visualization":
                        fig = st.session_state.visualizer.create_uncertainty_visualization(
                            st.session_state.ensemble_results
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Scenario Comparison Charts":
                        fig = st.session_state.visualizer.create_scenario_comparison(
                            st.session_state.ensemble_results
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Regional Summary Charts":
                        fig = st.session_state.visualizer.create_regional_summary(
                            st.session_state.ensemble_results
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Store visualizations for export
                st.session_state.generated_visualizations = viz_options
                st.success("✅ All visualizations generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating visualizations: {str(e)}")

def executive_summary_page():
    st.header("📋 Executive Summary")
    
    if not hasattr(st.session_state, 'ensemble_results'):
        st.warning("Please complete climate analysis first.")
        return
    
    # Generate executive summary
    if st.button("Generate Executive Summary"):
        with st.spinner("Generating executive summary..."):
            try:
                summary = st.session_state.report_generator.generate_executive_summary(
                    st.session_state.ensemble_results
                )
                st.session_state.executive_summary = summary
                
                # Display executive summary
                st.markdown("---")
                st.markdown(summary['full_report'])
                
                # Key metrics display
                st.subheader("📊 Key Metrics Dashboard")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Mean Rainfall Increase",
                        f"{summary['key_metrics']['mean_increase']}%",
                        delta=f"+{summary['key_metrics']['mean_increase']}%"
                    )
                
                with col2:
                    st.metric(
                        "Affected Districts",
                        summary['key_metrics']['affected_districts']
                    )
                
                with col3:
                    st.metric(
                        "High Risk States",
                        summary['key_metrics']['high_risk_states']
                    )
                
                with col4:
                    st.metric(
                        "Confidence Level",
                        f"{summary['key_metrics']['confidence_level']}%"
                    )
                
                # Regional analysis
                st.subheader("🗺️ Regional Analysis")
                
                regional_data = summary.get('regional_analysis', {})
                if regional_data:
                    for region, data in regional_data.items():
                        with st.expander(f"{region} Region"):
                            st.write(f"**Rainfall Change:** {data.get('change', 'N/A')}%")
                            st.write(f"**Risk Level:** {data.get('risk_level', 'N/A')}")
                            st.write(f"**Priority Actions:** {data.get('actions', 'N/A')}")
                
                # Policy recommendations
                st.subheader("🎯 Policy Recommendations")
                
                recommendations = summary.get('recommendations', [])
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"**{i}.** {rec}")
                
                st.success("✅ Executive summary generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating executive summary: {str(e)}")

def export_page():
    st.header("💾 Export Results")
    
    if not hasattr(st.session_state, 'executive_summary'):
        st.warning("Please generate executive summary first.")
        return
    
    st.subheader("Export Options")
    
    # Export format selection
    export_formats = st.multiselect(
        "Select export formats:",
        ["PDF Report", "Excel Data", "PNG Maps", "TIFF Maps", "JSON Data"],
        default=["PDF Report", "PNG Maps"]
    )
    
    # Export configuration
    col1, col2 = st.columns(2)
    
    with col1:
        include_uncertainty = st.checkbox("Include Uncertainty Bounds", value=True)
        include_maps = st.checkbox("Include All Maps", value=True)
    
    with col2:
        high_resolution = st.checkbox("High Resolution Images", value=True)
        include_raw_data = st.checkbox("Include Raw Data", value=False)
    
    # Export button
    if st.button("Generate Export Package"):
        with st.spinner("Preparing export package..."):
            try:
                export_package = st.session_state.utils.create_export_package(
                    ensemble_results=st.session_state.ensemble_results,
                    executive_summary=st.session_state.executive_summary,
                    visualizations=getattr(st.session_state, 'generated_visualizations', []),
                    formats=export_formats,
                    config={
                        'include_uncertainty': include_uncertainty,
                        'include_maps': include_maps,
                        'high_resolution': high_resolution,
                        'include_raw_data': include_raw_data
                    }
                )
                
                st.success("✅ Export package created successfully!")
                
                # Provide download links
                st.subheader("📁 Download Files")
                
                for file_info in export_package:
                    file_name = file_info['name']
                    file_data = file_info['data']
                    file_type = file_info['type']
                    
                    # Create download button
                    st.download_button(
                        label=f"📄 Download {file_name}",
                        data=file_data,
                        file_name=file_name,
                        mime=file_type
                    )
                
                # Export summary
                st.info(f"Export package contains {len(export_package)} files")
                
            except Exception as e:
                st.error(f"Error creating export package: {str(e)}")

if __name__ == "__main__":
    main()
