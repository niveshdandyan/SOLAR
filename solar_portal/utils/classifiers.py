"""
Cloud Classifier Module
Classifies measurements as CLEAR, CLOUDY, or MARGINAL sky
"""

import pandas as pd
import numpy as np
import logging
from config import PANEL_SPECS

logger = logging.getLogger(__name__)


class CloudClassifier:
    """
    Classifies sky conditions based on power ratio method.
    
    Logic:
    1. Compute median power for each hour across all days
    2. For each measurement, compute power_ratio = actual_power / median_power
    3. If power_ratio >= threshold: CLEAR
    4. If power_ratio < 0.5 * threshold: CLOUDY
    5. Otherwise: MARGINAL
    """
    
    def __init__(self, df: pd.DataFrame, threshold: float = 0.70):
        """
        Initialize classifier.
        
        Args:
            df: DataFrame with measurements
            threshold: Classification threshold (0.5-0.9, default 0.70)
        """
        self.df = df.copy()
        self.threshold = max(0.5, min(0.9, threshold))  # Clamp to valid range
        self.classifications = None
        self.hourly_medians = None
        
    def compute_hourly_medians(self) -> pd.DataFrame:
        """
        Compute median power for each hour of day (across all days).
        
        Returns:
            DataFrame with hourly median powers
        """
        hourly_medians = self.df.groupby("hour")["power_W"].median().reset_index()
        hourly_medians.columns = ["hour", "median_power_W"]
        
        self.hourly_medians = hourly_medians
        logger.info(f"Computed hourly medians for {len(hourly_medians)} hours")
        return hourly_medians
    
    def classify(self) -> pd.DataFrame:
        """
        Classify all measurements.
        
        Returns:
            DataFrame with classification column
        """
        if self.hourly_medians is None:
            self.compute_hourly_medians()
        
        # Merge median power for each hour
        df_classified = self.df.merge(
            self.hourly_medians,
            on="hour",
            how="left"
        )
        
        # Compute power ratio
        df_classified["power_ratio"] = (
            df_classified["power_W"] / (df_classified["median_power_W"] + 1e-6)
        )
        
        # Classify based on threshold
        df_classified["classification"] = "CLOUDY"  # Default
        df_classified.loc[
            df_classified["power_ratio"] >= self.threshold,
            "classification"
        ] = "CLEAR"
        df_classified.loc[
            (df_classified["power_ratio"] >= 0.5 * self.threshold) &
            (df_classified["power_ratio"] < self.threshold),
            "classification"
        ] = "MARGINAL"
        
        # Compute confidence score (0-1)
        # Higher when power_ratio is far from threshold
        df_classified["confidence"] = 1 - np.abs(
            df_classified["power_ratio"] - self.threshold
        ) / max(self.threshold, 1 - self.threshold)
        df_classified["confidence"] = df_classified["confidence"].clip(0, 1)
        
        self.classifications = df_classified
        logger.info(f"Classified {len(df_classified)} measurements")
        return df_classified
    
    def get_classification_summary(self) -> dict:
        """
        Get summary of classifications.
        
        Returns:
            Dictionary with classification counts
        """
        if self.classifications is None:
            self.classify()
        
        counts = self.classifications["classification"].value_counts().to_dict()
        total = len(self.classifications)
        
        return {
            "clear_count": counts.get("CLEAR", 0),
            "clear_pct": counts.get("CLEAR", 0) / total * 100,
            "marginal_count": counts.get("MARGINAL", 0),
            "marginal_pct": counts.get("MARGINAL", 0) / total * 100,
            "cloudy_count": counts.get("CLOUDY", 0),
            "cloudy_pct": counts.get("CLOUDY", 0) / total * 100,
        }
    
    def get_classifications(self) -> pd.DataFrame:
        """Get classified data"""
        if self.classifications is None:
            return self.classify()
        return self.classifications
