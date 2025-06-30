# Climate Data Analysis Pipeline

## Overview

This is a comprehensive climate data analysis pipeline built with Streamlit that focuses on forecasting Indian rainfall patterns in 2050 using CMIP6 climate model data. The application provides an end-to-end solution for climate scientists and policy makers to analyze precipitation data, generate visualizations, and produce executive summaries for decision-making.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

### Frontend Architecture
- **Framework**: Streamlit web application
- **UI Pattern**: Multi-page application with sidebar navigation
- **State Management**: Streamlit session state for maintaining component instances
- **Layout**: Wide layout with expandable sidebar for optimal data visualization

### Backend Architecture
- **Modular Design**: Separate classes for different functionalities
- **Data Processing**: NetCDF file handling with xarray
- **Analysis Engine**: Climate analysis calculations and ensemble modeling
- **Visualization Engine**: Plotly and Matplotlib for interactive charts and maps
- **Report Generation**: Automated executive summary and policy report creation

## Key Components

### 1. Data Processor (`data_processor.py`)
- **Purpose**: Handles NetCDF data loading, preprocessing, and geographic clipping
- **Key Features**:
  - Supports both file paths and uploaded file objects
  - Clips data to Indian geographical bounds (6°N-37°N, 68°E-97°E)
  - Coordinate system standardization (WGS84)
  - Flexible coordinate name detection

### 2. Climate Analyzer (`climate_analyzer.py`)
- **Purpose**: Performs statistical climate analysis and calculates rainfall indices
- **Key Features**:
  - Standard rainfall indices calculation (PRCPTOT, Rx1day, Rx5day)
  - Rainfall threshold categorization (light to extreme)
  - Ensemble modeling capabilities
  - Baseline period comparison (1990-2019)

### 3. Visualizer (`visualizer.py`)
- **Purpose**: Creates interactive visualizations and maps
- **Key Features**:
  - Rainfall change maps with geographic context
  - Interactive Plotly charts
  - Cartopy integration for geographic projections
  - Customizable color schemes for different data types

### 4. Report Generator (`report_generator.py`)
- **Purpose**: Generates executive summaries and policy reports
- **Key Features**:
  - Automated report generation from analysis results
  - Policy recommendations based on climate projections
  - Regional analysis summaries
  - Confidence assessment reporting

### 5. Utils (`utils.py`)
- **Purpose**: Utility functions for data export and file handling
- **Key Features**:
  - Multi-format export (PDF, Excel, JSON)
  - Comprehensive export packages
  - File compression and packaging
  - Base64 encoding for web delivery

## Data Flow

1. **Data Ingestion**: Users upload NetCDF files through Streamlit interface
2. **Preprocessing**: Data is loaded, validated, and clipped to Indian boundaries
3. **Analysis**: Climate indices are calculated and ensemble modeling is performed
4. **Visualization**: Interactive maps and charts are generated
5. **Reporting**: Executive summaries and policy reports are created
6. **Export**: Results are packaged in multiple formats for download

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **xarray**: NetCDF data handling and analysis
- **numpy/pandas**: Data manipulation and numerical computing
- **plotly**: Interactive visualizations
- **matplotlib**: Static plotting and cartographic visualizations
- **cartopy**: Geographic projections and mapping

### Scientific Computing
- **scipy**: Statistical analysis functions
- **netCDF4**: NetCDF file format support (implicit through xarray)

### File Processing
- **io**: File-like object handling
- **base64**: Data encoding for web delivery
- **zipfile**: Archive creation for export packages

## Deployment Strategy

The application is designed for Replit deployment with the following considerations:

### Environment Setup
- Python 3.8+ required
- Scientific computing libraries pre-installed
- Streamlit server configuration for web access

### File Handling
- Supports both local file uploads and programmatic data loading
- Temporary file processing for large NetCDF datasets
- Memory-efficient data processing for cloud environments

### Scalability Considerations
- Session state management for multiple users
- Efficient data processing with lazy loading
- Configurable memory limits for large datasets

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Improvements

### Accuracy Enhancements (June 30, 2025)
- **Unit Conversion**: Added automatic detection and conversion of rainfall units (kg/m²/s to mm/day)
- **Baseline Calibration**: Using realistic Indian monsoon baseline (800-1200mm JJAS average)
- **Spatial Pattern Recognition**: Implemented region-specific climate patterns (Western Ghats, Northeast monsoon, etc.)
- **Uncertainty Quantification**: Enhanced confidence level calculations based on model ensemble spread
- **Data Validation**: Added comprehensive data quality checks and NaN handling

### Visualization Improvements (June 30, 2025)  
- **Dynamic Map Generation**: Maps now use actual spatial data when available
- **Realistic Climate Patterns**: Incorporated orographic effects and regional variations
- **Export Functionality**: Fixed image export using Kaleido for PNG/TIFF generation
- **Interactive Features**: Enhanced hover information and color scales

### Demo Mode (June 30, 2025)
- **Test Data Generator**: Created realistic synthetic climate data for testing
- **Pattern Accuracy**: Demo data reflects actual Indian monsoon characteristics
- **Easy Testing**: Users can test the full pipeline without NetCDF files

## Changelog

Changelog:
- June 30, 2025. Initial setup
- June 30, 2025. Major accuracy improvements and bug fixes for visualizations