"""
Visualization Module
Creates charts and graphs for data analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from pathlib import Path
from datetime import datetime
from config import CHART_CONFIG

logger = logging.getLogger(__name__)


class Visualizer:
    """
    Creates publication-quality charts from solar data.
    """
    
    def __init__(self, output_dir: str = "outputs/"):
        """Initialize visualizer with output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set matplotlib style
        plt.style.use("seaborn-v0_8-darkgrid")
    
    def plot_daily_power_trend(self, df_daily: pd.DataFrame) -> str:
        """
        Plot daily peak power over time with color coding by classification.
        
        Args:
            df_daily: Daily summary DataFrame
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=CHART_CONFIG["figsize"], dpi=CHART_CONFIG["dpi"])
        
        dates = pd.to_datetime(df_daily["date"])
        ax.plot(dates, df_daily["peak_power_W"], marker="o", linewidth=2, markersize=4)
        
        ax.set_xlabel("Date")
        ax.set_ylabel("Peak Power (W)")
        ax.set_title("Daily Peak Power Trend")
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_path = self.output_dir / "01_daily_power_trend.png"
        plt.savefig(output_path, dpi=CHART_CONFIG["dpi"])
        plt.close()
        
        logger.info(f"Saved daily power trend to {output_path}")
        return str(output_path)
    
    def plot_hourly_pattern(self, df_hourly: pd.DataFrame) -> str:
        """
        Plot hourly power pattern (all vs clear only).
        
        Args:
            df_hourly: Hourly summary DataFrame
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=CHART_CONFIG["figsize"], dpi=CHART_CONFIG["dpi"])
        
        hourly_avg = df_hourly.groupby("hour")["avg_power_W"].mean()
        
        ax.plot(hourly_avg.index, hourly_avg.values, marker="o", label="All Data", linewidth=2)
        
        if "classification" in df_hourly.columns:
            clear_data = df_hourly[df_hourly["classification"] == "CLEAR"]
            if len(clear_data) > 0:
                hourly_clear = clear_data.groupby("hour")["avg_power_W"].mean()
                ax.plot(hourly_clear.index, hourly_clear.values, marker="s", 
                       label="Clear Days Only", linewidth=2)
        
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Average Power (W)")
        ax.set_title("Hourly Power Pattern")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        output_path = self.output_dir / "02_hourly_pattern.png"
        plt.savefig(output_path, dpi=CHART_CONFIG["dpi"])
        plt.close()
        
        logger.info(f"Saved hourly pattern to {output_path}")
        return str(output_path)
    
    def plot_power_ratio_distribution(self, df_classified: pd.DataFrame, threshold: float = 0.70) -> str:
        """
        Plot histogram of power ratios with threshold marker.
        
        Args:
            df_classified: Classified measurements DataFrame
            threshold: Classification threshold
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=CHART_CONFIG["figsize"], dpi=CHART_CONFIG["dpi"])
        
        ax.hist(df_classified["power_ratio"], bins=50, alpha=0.7, edgecolor="black")
        ax.axvline(threshold, color="red", linestyle="--", linewidth=2, label=f"Threshold ({threshold})")
        
        ax.set_xlabel("Power Ratio")
        ax.set_ylabel("Frequency")
        ax.set_title("Power Ratio Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")
        
        output_path = self.output_dir / "03_power_ratio_distribution.png"
        plt.savefig(output_path, dpi=CHART_CONFIG["dpi"])
        plt.close()
        
        logger.info(f"Saved power ratio distribution to {output_path}")
        return str(output_path)
    
    def plot_temperature_analysis(self, df: pd.DataFrame) -> str:
        """
        Plot power vs temperature scatter with trend line.
        
        Args:
            df: Measurement DataFrame
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=CHART_CONFIG["figsize"], dpi=CHART_CONFIG["dpi"])
        
        # Filter to high irradiance points only (power > 50W)
        high_power = df[df["power_W"] > 50]
        
        ax.scatter(high_power["temperature_C"], high_power["power_W"], alpha=0.5)
        
        # Fit trend line
        if len(high_power) > 2:
            z = np.polyfit(high_power["temperature_C"], high_power["power_W"], 1)
            p = np.poly1d(z)
            temps = np.linspace(high_power["temperature_C"].min(), 
                               high_power["temperature_C"].max(), 100)
            ax.plot(temps, p(temps), "r--", linewidth=2, label=f"Trend: {z:.3f}W/°C")
        
        ax.set_xlabel("Temperature (°C)")
        ax.set_ylabel("Power (W)")
        ax.set_title("Power vs Temperature (High Irradiance)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        output_path = self.output_dir / "04_temperature_analysis.png"
        plt.savefig(output_path, dpi=CHART_CONFIG["dpi"])
        plt.close()
        
        logger.info(f"Saved temperature analysis to {output_path}")
        return str(output_path)
    
    def plot_classification_summary(self, summary: dict) -> str:
        """
        Plot pie chart of classification summary.
        
        Args:
            summary: Classification summary dictionary
            
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(8, 6), dpi=CHART_CONFIG["dpi"])
        
        labels = ["Clear", "Marginal", "Cloudy"]
        sizes = [
            summary.get("clear_count", 0),
            summary.get("marginal_count", 0),
            summary.get("cloudy_count", 0),
        ]
        colors = [
            CHART_CONFIG["color_clear"],
            CHART_CONFIG["color_marginal"],
            CHART_CONFIG["color_cloudy"],
        ]
        
        ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        ax.set_title("Sky Classification Distribution")
        
        output_path = self.output_dir / "05_classification_summary.png"
        plt.savefig(output_path, dpi=CHART_CONFIG["dpi"])
        plt.close()
        
        logger.info(f"Saved classification summary to {output_path}")
        return str(output_path)
