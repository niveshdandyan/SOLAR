"""
Data Validator Module
Comprehensive data quality checks and outlier detection
"""

import pandas as pd
import numpy as np
import logging
from config import VALID_RANGES, PANEL_SPECS, ERROR_MESSAGES

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates solar panel measurement data against expected ranges and logic.
    Detects outliers, missing values, and inconsistencies.
    """
    
    def __init__(self):
        """Initialize validator"""
        self.validation_errors = []
        self.validation_warnings = []
        self.outliers = pd.DataFrame()
        
    def validate_all(self, df: pd.DataFrame) -> tuple[bool, dict]:
        """
        Run all validation checks.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid: bool, report: dict)
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        # Data type checks
        self._check_data_types(df)
        
        # Range checks
        self._check_value_ranges(df)
        
        # Temporal checks
        self._check_temporal_integrity(df)
        
        # Outlier detection
        self._detect_outliers(df)
        
        # Missing data checks
        self._check_missing_data(df)
        
        is_valid = len(self.validation_errors) == 0
        
        report = {
            "is_valid": is_valid,
            "errors": self.validation_errors,
            "warnings": self.validation_warnings,
            "total_rows": len(df),
            "invalid_rows": len(self.outliers),
            "data_quality": (1 - len(self.outliers) / len(df)) * 100,
        }
        
        logger.info(f"Validation complete: {report}")
        return is_valid, report
    
    def _check_data_types(self, df: pd.DataFrame) -> None:
        """Check all columns have correct data types"""
        numeric_cols = ["voltage_V", "current_A", "power_W", "temperature_C"]
        
        for col in numeric_cols:
            try:
                pd.to_numeric(df[col], errors="coerce")
                non_numeric = df[pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()]
                if len(non_numeric) > 0:
                    self.validation_errors.append(
                        ERROR_MESSAGES["invalid_data_type"].format(col=col)
                    )
            except Exception as e:
                self.validation_errors.append(f"Error checking column {col}: {str(e)}")
    
    def _check_value_ranges(self, df: pd.DataFrame) -> None:
        """Check all values are within expected ranges"""
        for col, (min_val, max_val) in VALID_RANGES.items():
            if col in df.columns:
                out_of_range = df[(df[col] < min_val) | (df[col] > max_val)]
                if len(out_of_range) > 0:
                    self.validation_warnings.append(
                        f"{len(out_of_range)} rows have {col} outside range [{min_val}, {max_val}]"
                    )
                    self.outliers = pd.concat([self.outliers, out_of_range])
    
    def _check_temporal_integrity(self, df: pd.DataFrame) -> None:
        """Check timestamps are monotonically increasing and reasonable"""
        if "timestamp" not in df.columns:
            return
        
        df_sorted = df.sort_values("timestamp")
        
        # Check for time reversals
        if not df["timestamp"].is_monotonic_increasing:
            self.validation_warnings.append("Timestamps not in chronological order")
        
        # Check for excessive gaps
        time_diffs = df_sorted["timestamp"].diff()
        max_gap = time_diffs.max()
        if pd.isna(max_gap) or max_gap > pd.Timedelta(hours=1):
            self.validation_warnings.append(
                f"Large time gap detected: {max_gap}"
            )
    
    def _detect_outliers(self, df: pd.DataFrame) -> None:
        """Detect physical impossibilities (e.g., power > rated)"""
        rated_power = PANEL_SPECS["rated_power_W"]
        
        # Power should not exceed 2x rated (allows for measurement error)
        high_power = df[df["power_W"] > 2 * rated_power]
        if len(high_power) > 0:
            self.validation_warnings.append(
                f"{len(high_power)} measurements exceed 2x rated power ({2 * rated_power}W)"
            )
            self.outliers = pd.concat([self.outliers, high_power])
        
        # Voltage should not exceed 1.2x Voc
        voc = PANEL_SPECS["voc_V"]
        high_voltage = df[df["voltage_V"] > 1.2 * voc]
        if len(high_voltage) > 0:
            self.validation_warnings.append(
                f"{len(high_voltage)} measurements exceed 1.2x Voc ({1.2 * voc}V)"
            )
            self.outliers = pd.concat([self.outliers, high_voltage])
    
    def _check_missing_data(self, df: pd.DataFrame) -> None:
        """Check for missing or null values"""
        null_pct = (df.isnull().sum() / len(df) * 100).mean()
        
        if null_pct > 20:
            self.validation_errors.append(
                f"Data quality poor: {null_pct:.1f}% missing values"
            )
        elif null_pct > 5:
            self.validation_warnings.append(
                f"Some missing data: {null_pct:.1f}%"
            )
    
    def get_report(self) -> dict:
        """Get validation report"""
        return {
            "errors": self.validation_errors,
            "warnings": self.validation_warnings,
            "outliers_count": len(self.outliers),
        }
