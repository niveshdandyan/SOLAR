"""
Data Processor Module
Aggregations, calculations, and statistical processing
"""

import pandas as pd
import numpy as np
import logging
from config import PANEL_SPECS

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes validated data to compute aggregations and statistics.
    Handles hourly/daily summaries, performance metrics, etc.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize processor with data.
        
        Args:
            df: Validated DataFrame with measurements
        """
        self.df = df.copy()
        self.hourly_summary = None
        self.daily_summary = None
        
    def compute_hourly_aggregations(self, classifications: pd.Series = None) -> pd.DataFrame:
        """
        Compute hourly averages and statistics.
        
        Args:
            classifications: Optional Series with CLEAR/CLOUDY classifications
            
        Returns:
            DataFrame with hourly summaries
        """
        # Group by date and hour
        hourly = self.df.groupby(["date", "hour"]).agg({
            "power_W": ["mean", "std", "count"],
            "voltage_V": "mean",
            "current_A": "mean",
            "temperature_C": "mean",
        }).reset_index()
        
        # Flatten column names
        hourly.columns = [
            "date", "hour",
            "avg_power_W", "std_power_W", "count_measurements",
            "avg_voltage_V", "avg_current_A", "avg_temperature_C"
        ]
        
        # Add classification if provided
        if classifications is not None:
            hourly = hourly.merge(
                classifications.groupby(["date", "hour"]).first().reset_index(),
                on=["date", "hour"],
                how="left"
            )
        
        self.hourly_summary = hourly
        logger.info(f"Computed {len(hourly)} hourly summaries")
        return hourly
    
    def compute_daily_aggregations(self, hourly: pd.DataFrame = None) -> pd.DataFrame:
        """
        Compute daily summaries from hourly data.
        
        Args:
            hourly: Optional pre-computed hourly DataFrame
            
        Returns:
            DataFrame with daily summaries
        """
        if hourly is None:
            hourly = self.compute_hourly_aggregations()
        
        daily = hourly.groupby("date").agg({
            "avg_power_W": ["max", "mean"],
            "count_measurements": "sum",
            "avg_temperature_C": "mean",
        }).reset_index()
        
        # Flatten column names
        daily.columns = ["date", "peak_power_W", "avg_power_W", "hours_measured", "temp_avg_C"]
        
        # Compute daily energy (integrate power over time)
        # Assuming hourly averages approximate integral over hour
        daily["energy_Wh"] = daily["avg_power_W"] * daily["hours_measured"]
        
        self.daily_summary = daily
        logger.info(f"Computed {len(daily)} daily summaries")
        return daily
    
    def compute_temperature_correction(self) -> pd.DataFrame:
        """
        Compute temperature-corrected power values.
        P_corrected = P * [1 + alpha * (T_ref - T)]
        
        Returns:
            DataFrame with temperature-corrected power
        """
        df_corrected = self.df.copy()
        
        alpha = PANEL_SPECS["temp_coefficient_per_celsius"]
        t_ref = PANEL_SPECS["reference_temperature_celsius"]
        
        df_corrected["power_W_corrected"] = df_corrected["power_W"] * (
            1 + alpha * (t_ref - df_corrected["temperature_C"])
        )
        
        logger.info("Temperature correction applied")
        return df_corrected
    
    def compute_performance_ratio(self, df_classified: pd.DataFrame) -> dict:
        """
        Compute performance ratio: actual power / expected power
        
        Args:
            df_classified: DataFrame with classification column
            
        Returns:
            Dictionary with PR metrics
        """
        rated_power = PANEL_SPECS["rated_power_W"]
        
        # PR for all data
        pr_all = (df_classified["power_W"].sum() / 
                  (rated_power * len(df_classified) / (1000 / 500)))  # Assuming 15-min intervals
        
        # PR for clear days only
        if "classification" in df_classified.columns:
            clear_data = df_classified[df_classified["classification"] == "CLEAR"]
            if len(clear_data) > 0:
                pr_clear = (clear_data["power_W"].sum() / 
                           (rated_power * len(clear_data) / (1000 / 500)))
            else:
                pr_clear = 0
        else:
            pr_clear = pr_all
        
        return {
            "pr_all": max(0, min(1.5, pr_all)),  # Clip between 0-150%
            "pr_clear": max(0, min(1.5, pr_clear)),
        }
    
    def get_hourly_summary(self) -> pd.DataFrame:
        """Get cached hourly summary"""
        if self.hourly_summary is None:
            return self.compute_hourly_aggregations()
        return self.hourly_summary
    
    def get_daily_summary(self) -> pd.DataFrame:
        """Get cached daily summary"""
        if self.daily_summary is None:
            return self.compute_daily_aggregations()
        return self.daily_summary
