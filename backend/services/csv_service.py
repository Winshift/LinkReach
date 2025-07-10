import pandas as pd
import io
import tempfile
import os
from typing import Tuple, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CSVService:
    """Service class for CSV operations"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "linkedin_filter"
        self.temp_dir.mkdir(exist_ok=True)
    
    def validate_csv(self, file_content: bytes) -> Tuple[bool, str, pd.DataFrame]:
        """
        Validate and parse CSV file
        
        Returns:
            Tuple[bool, str, pd.DataFrame]: (is_valid, error_message, dataframe)
        """
        try:
            # Try to read the CSV with different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
                    return True, "", df
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    continue
            
            return False, "Unable to read CSV file. Please ensure it's a valid CSV format.", pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error validating CSV: {str(e)}")
            return False, f"Error processing CSV file: {str(e)}", pd.DataFrame()
    
    def get_preview_data(self, df: pd.DataFrame, max_rows: int = 5) -> List[Dict[str, Any]]:
        """Get preview data from dataframe"""
        try:
            preview_df = df.head(max_rows)
            return preview_df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting preview data: {str(e)}")
            return []
    
    def save_filtered_results(self, df: pd.DataFrame, filename: str = None) -> str:
        """Save filtered results to temporary file and return download path"""
        try:
            if filename is None:
                filename = f"filtered_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            file_path = self.temp_dir / filename
            df.to_csv(file_path, index=False)
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving filtered results: {str(e)}")
            raise
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        try:
            current_time = pd.Timestamp.now()
            for file_path in self.temp_dir.glob("*.csv"):
                file_age = current_time - pd.Timestamp.fromtimestamp(file_path.stat().st_mtime)
                if file_age.total_seconds() > max_age_hours * 3600:
                    file_path.unlink()
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}") 