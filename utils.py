import os
import json
import pandas as pd
import numpy as np
import base64
import io
from datetime import datetime
import zipfile

class Utils:
    """Utility functions for data export, file handling, and common operations."""
    
    def __init__(self):
        self.supported_formats = {
            'images': ['png', 'jpg', 'svg', 'pdf'],
            'data': ['csv', 'json', 'xlsx', 'parquet'],
            'reports': ['pdf', 'docx', 'html', 'markdown']
        }
    
    def create_export_package(self, ensemble_results, executive_summary, visualizations, formats, config):
        """Create comprehensive export package with all analysis results."""
        try:
            export_files = []
            
            # 1. Export executive summary report
            if 'PDF Report' in formats:
                pdf_content = self._create_pdf_report(executive_summary)
                export_files.append({
                    'name': 'Climate_Analysis_Report.pdf',
                    'data': pdf_content,
                    'type': 'application/pdf'
                })
            
            # 2. Export data files
            if 'Excel Data' in formats:
                excel_content = self._create_excel_export(ensemble_results, config)
                export_files.append({
                    'name': 'Climate_Data_Analysis.xlsx',
                    'data': excel_content,
                    'type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                })
            
            # 3. Export JSON data
            if 'JSON Data' in formats:
                json_content = self._create_json_export(ensemble_results, executive_summary)
                export_files.append({
                    'name': 'climate_analysis_data.json',
                    'data': json_content,
                    'type': 'application/json'
                })
            
            # 4. Export visualization files
            if 'PNG Maps' in formats and config.get('include_maps', True):
                map_files = self._create_map_exports(ensemble_results, 'png', config.get('high_resolution', True))
                export_files.extend(map_files)
            
            if 'TIFF Maps' in formats and config.get('include_maps', True):
                map_files = self._create_map_exports(ensemble_results, 'tiff', config.get('high_resolution', True))
                export_files.extend(map_files)
            
            return export_files
        except Exception as e:
            raise Exception(f"Error creating export package: {str(e)}")
    
    def _create_pdf_report(self, executive_summary):
        """Create PDF report from executive summary."""
        try:
            # Simulate PDF creation (in practice, use libraries like reportlab or weasyprint)
            markdown_content = executive_summary.get('full_report', '')
            
            # Convert markdown to simple text for simulation
            pdf_text = f"""
CLIMATE DATA ANALYSIS REPORT
Generated on: {datetime.now().strftime('%B %d, %Y')}

{markdown_content}

---
End of Report
"""
            
            # Return as bytes (simulated PDF content)
            return pdf_text.encode('utf-8')
        except Exception as e:
            raise Exception(f"Error creating PDF report: {str(e)}")
    
    def _create_excel_export(self, ensemble_results, config):
        """Create Excel file with analysis results."""
        try:
            # Create a BytesIO buffer
            buffer = io.BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = ensemble_results.get('summary', {})
                summary_df = pd.DataFrame([summary_data])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Individual indices sheets
                for index_name, index_data in ensemble_results.items():
                    if index_name != 'summary' and isinstance(index_data, dict):
                        if 'mean' in index_data:
                            df_data = {
                                'Index': [index_name],
                                'Mean': [index_data.get('mean', 0)],
                                'Std': [index_data.get('std', 0)],
                                'P10': [index_data.get('percentiles', {}).get('p10', 0)],
                                'P25': [index_data.get('percentiles', {}).get('p25', 0)],
                                'P50': [index_data.get('percentiles', {}).get('p50', 0)],
                                'P75': [index_data.get('percentiles', {}).get('p75', 0)],
                                'P90': [index_data.get('percentiles', {}).get('p90', 0)]
                            }
                            df = pd.DataFrame(df_data)
                            df.to_excel(writer, sheet_name=index_name[:31], index=False)  # Excel sheet name limit
                
                # Metadata sheet
                metadata = {
                    'Generated_On': [datetime.now().isoformat()],
                    'Analysis_Type': ['CMIP6 Ensemble Analysis'],
                    'Scenario': [ensemble_results.get('summary', {}).get('scenario', 'SSP5-8.5')],
                    'Projection_Year': [ensemble_results.get('summary', {}).get('projection_year', '2050')],
                    'Confidence_Level': [ensemble_results.get('summary', {}).get('confidence_level', 80)]
                }
                metadata_df = pd.DataFrame(metadata)
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            raise Exception(f"Error creating Excel export: {str(e)}")
    
    def _create_json_export(self, ensemble_results, executive_summary):
        """Create JSON export of all analysis data."""
        try:
            export_data = {
                'metadata': {
                    'generated_on': datetime.now().isoformat(),
                    'analysis_type': 'CMIP6 Climate Projection Analysis',
                    'version': '1.0'
                },
                'ensemble_results': self._serialize_for_json(ensemble_results),
                'executive_summary': executive_summary,
                'data_sources': {
                    'historical_data': 'IMD Rainfall Data (1981-2010)',
                    'projection_data': 'CMIP6 Multi-Model Ensemble',
                    'scenarios': ['SSP2-4.5', 'SSP5-8.5']
                },
                'methodology': {
                    'regridding': '0.25° x 0.25° resolution',
                    'season': 'JJAS (June-September)',
                    'indices': ['PRCPTOT', 'Rx1day', 'Rx5day', 'Heavy Rain Days'],
                    'uncertainty_method': '10th-90th percentile bounds'
                }
            }
            
            return json.dumps(export_data, indent=2, default=str).encode('utf-8')
        except Exception as e:
            raise Exception(f"Error creating JSON export: {str(e)}")
    
    def _create_map_exports(self, ensemble_results, format_type, high_resolution=True):
        """Create map image exports."""
        try:
            map_files = []
            
            # Simulate map image creation
            map_types = [
                'rainfall_change_map',
                'extreme_days_map',
                'uncertainty_map',
                'regional_summary_map'
            ]
            
            for map_type in map_types:
                # Create dummy image content (in practice, this would render actual maps)
                if format_type.lower() == 'png':
                    # Simulate PNG content
                    image_content = self._create_dummy_png()
                    extension = 'png'
                    mime_type = 'image/png'
                elif format_type.lower() == 'tiff':
                    # Simulate TIFF content
                    image_content = self._create_dummy_tiff()
                    extension = 'tiff'
                    mime_type = 'image/tiff'
                else:
                    continue
                
                resolution_suffix = '_high_res' if high_resolution else ''
                filename = f"{map_type}{resolution_suffix}.{extension}"
                
                map_files.append({
                    'name': filename,
                    'data': image_content,
                    'type': mime_type
                })
            
            return map_files
        except Exception as e:
            raise Exception(f"Error creating map exports: {str(e)}")
    
    def _create_dummy_png(self):
        """Create dummy PNG content for demonstration."""
        # This is a minimal PNG header - in practice, use actual plotting libraries
        png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x007n\xf9$\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        return png_header
    
    def _create_dummy_tiff(self):
        """Create dummy TIFF content for demonstration."""
        # Minimal TIFF header - in practice, use actual TIFF libraries
        tiff_header = b'II*\x00\x08\x00\x00\x00\x00\x00'
        return tiff_header
    
    def _serialize_for_json(self, data):
        """Serialize complex data structures for JSON export."""
        if isinstance(data, dict):
            return {k: self._serialize_for_json(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._serialize_for_json(item) for item in data]
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, (np.integer, np.floating)):
            return float(data)
        elif hasattr(data, 'values'):  # xarray or pandas objects
            try:
                return data.values.tolist()
            except:
                return str(data)
        else:
            return data
    
    def validate_file_format(self, file_path, expected_format):
        """Validate uploaded file format."""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            valid_extensions = {
                'netcdf': ['.nc', '.netcdf', '.nc4'],
                'csv': ['.csv'],
                'json': ['.json'],
                'excel': ['.xlsx', '.xls']
            }
            
            if expected_format in valid_extensions:
                return file_extension in valid_extensions[expected_format]
            
            return False
        except Exception:
            return False
    
    def format_number(self, value, precision=2, unit=""):
        """Format numbers for display."""
        try:
            if isinstance(value, (int, float)) and not np.isnan(value):
                if abs(value) >= 1e6:
                    return f"{value/1e6:.{precision}f}M {unit}".strip()
                elif abs(value) >= 1e3:
                    return f"{value/1e3:.{precision}f}K {unit}".strip()
                else:
                    return f"{value:.{precision}f} {unit}".strip()
            else:
                return "N/A"
        except Exception:
            return "N/A"
    
    def create_download_link(self, data, filename, mime_type):
        """Create download link for data."""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            b64_data = base64.b64encode(data).decode()
            return f"data:{mime_type};base64,{b64_data}"
        except Exception as e:
            raise Exception(f"Error creating download link: {str(e)}")
    
    def log_analysis_session(self, session_data):
        """Log analysis session for audit trail."""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'session_id': session_data.get('session_id', 'unknown'),
                'user_actions': session_data.get('actions', []),
                'data_processed': session_data.get('data_files', []),
                'outputs_generated': session_data.get('outputs', [])
            }
            
            # In practice, this would write to a proper logging system
            return log_entry
        except Exception as e:
            raise Exception(f"Error logging session: {str(e)}")
    
    def get_system_info(self):
        """Get system information for debugging."""
        try:
            import platform
            import sys
            
            return {
                'python_version': sys.version,
                'platform': platform.platform(),
                'processor': platform.processor(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception:
            return {'error': 'Could not retrieve system information'}
