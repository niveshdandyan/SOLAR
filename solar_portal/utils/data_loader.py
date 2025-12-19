"""
Data Loader Module
Handles CSV reading, parsing, and initial data preparation
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from config import (
    VALID_RANGES,
    ANALYSIS_DEFAULTS,
    ERROR_MESSAGES,
    PANEL_SPECS,
)

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads and parses CSV files containing solar panel measurements.
    
    Expected CSV columns:
    - timestamp (YYYY-MM-DD HH:MM:SS format)
    - voltage_V (float)
    - current_A (float)
    - power_W (float)
    - temperature_C (float)
    """
    
    REQUIRED_COLUMNS = ["timestamp", "voltage_V", "current_A", "power_W", "temperature_C"]
    
    def __init__(self):
        """Initialize DataLoader"""
        self.data = None
        self.validation_report = {}
        
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load CSV file and perform basic parsing.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Parsed DataFrame
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        file_path = Path(file_path)
        
        # Check file exists
        if not file_path.exists():
            raise FileNotFoundError(ERROR_MESSAGES["file_not_found"])
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > ANALYSIS_DEFAULTS["max_file_size_mb"]:
            raise ValueError(ERROR_MESSAGES["file_too_large"])
        
        # Load CSV
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded CSV with {len(df)} rows")
        except Exception as e:
            raise ValueError(f"Error reading CSV: {str(e)}")
        
        # Check not empty
        if len(df) < ANALYSIS_DEFAULTS["min_upload_rows"]:
            raise ValueError(ERROR_MESSAGES["empty_file"])
        
        # Check columns exist
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(ERROR_MESSAGES["missing_columns"].format(missing=", ".join(missing_cols)))
        
        # Select only required columns
        df = df[self.REQUIRED_COLUMNS].copy()
        
        # Parse timestamp
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        except Exception as e:
            raise ValueError(ERROR_MESSAGES["invalid_timestamp"])
        
        # Extract date and hour for grouping
        df["date"] = df["timestamp"].dt.date
        df["hour"] = df["timestamp"].dt.hour
        
        self.data = df
        logger.info("CSV parsing successful")
        return df
    
    def get_data(self) -> pd.DataFrame:
        """
        Get loaded data.
        
        Returns:
            Loaded DataFrame
        """
        if self.data is None:
            raise RuntimeError("No data loaded. Call load_csv() first.")
        return self.data.copy()
    
    def get_info(self) -> dict:
        """
        Get information about loaded data.
        
        Returns:
            Dictionary with data summary
        """
        if self.data is None:
            return {}
        
        return {
            "total_rows": len(self.data),
            "date_range": f"{self.data['date'].min()} to {self.data['date'].max()}",
            "columns": list(self.data.columns),
            "memory_mb": self.data.memory_usage(deep=True).sum() / (1024 ** 2),
        }
