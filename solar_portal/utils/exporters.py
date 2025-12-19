"""
Exporter Module
Creates CSV files, PDF reports, and archives
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class Exporter:
    """
    Exports analysis results to CSV, PDF, and other formats.
    """
    
    def __init__(self, output_dir: str = "outputs/"):
        """Initialize exporter"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_hourly_all_data(self, df_hourly: pd.DataFrame) -> str:
        """
        Export hourly analysis for all data (including cloudy).
        
        Args:
            df_hourly: Hourly summary DataFrame
            
        Returns:
            Path to exported CSV
        """
        output_file = self.output_dir / "hourly_analysis_all_data.csv"
        
        # Select relevant columns in order
        cols = ["date", "hour", "avg_power_W", "avg_current_A", "avg_voltage_V", "count_measurements"]
        available_cols = [col for col in cols if col in df_hourly.columns]
        
        df_hourly[available_cols].to_csv(output_file, index=False)
        
        logger.info(f"Exported hourly analysis (all) to {output_file}")
        return str(output_file)
    
    def export_hourly_clear_days(self, df_hourly: pd.DataFrame) -> str:
        """
        Export hourly analysis for clear days only.
        
        Args:
            df_hourly: Hourly summary DataFrame with classification
            
        Returns:
            Path to exported CSV
        """
        output_file = self.output_dir / "hourly_analysis_clear_days_only.csv"
        
        # Filter to clear days only
        if "classification" in df_hourly.columns:
            df_clear = df_hourly[df_hourly["classification"] == "CLEAR"]
        else:
            df_clear = df_hourly
        
        cols = ["date", "hour", "avg_power_W", "avg_current_A", "avg_voltage_V", 
                "count_measurements", "classification"]
        available_cols = [col for col in cols if col in df_clear.columns]
        
        df_clear[available_cols].to_csv(output_file, index=False)
        
        logger.info(f"Exported hourly analysis (clear) to {output_file}")
        return str(output_file)
    
    def export_daily_summary(self, df_daily: pd.DataFrame) -> str:
        """
        Export daily summary statistics.
        
        Args:
            df_daily: Daily summary DataFrame
            
        Returns:
            Path to exported CSV
        """
        output_file = self.output_dir / "daily_summary.csv"
        
        cols = ["date", "peak_power_W", "energy_Wh", "temp_avg_C"]
        available_cols = [col for col in cols if col in df_daily.columns]
        
        df_daily[available_cols].to_csv(output_file, index=False)
        
        logger.info(f"Exported daily summary to {output_file}")
        return str(output_file)
    
    def export_classification_details(self, df_classified: pd.DataFrame) -> str:
        """
        Export detailed classification results.
        
        Args:
            df_classified: Full classified measurements DataFrame
            
        Returns:
            Path to exported CSV
        """
        output_file = self.output_dir / "classification_details.csv"
        
        cols = ["timestamp", "power_W", "power_ratio", "median_power_W", 
                "classification", "confidence"]
        available_cols = [col for col in cols if col in df_classified.columns]
        
        df_classified[available_cols].to_csv(output_file, index=False)
        
        logger.info(f"Exported classification details to {output_file}")
        return str(output_file)
    
    def create_summary_report(self, 
                             metadata: dict,
                             df_daily: pd.DataFrame,
                             classification_summary: dict,
                             pr_metrics: dict) -> str:
        """
        Create markdown summary report.
        
        Args:
            metadata: Analysis metadata (location, dates, etc.)
            df_daily: Daily summary DataFrame
            classification_summary: Classification counts
            pr_metrics: Performance ratio metrics
            
        Returns:
            Path to report file
        """
        output_file = self.output_dir / "analysis_report.md"
        
        report = f"""# SOLAR PANEL DATA ANALYSIS REPORT

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Analysis Period
- Location: {metadata.get('location', 'Unknown')}
- Date Range: {metadata.get('date_range', 'Unknown')}
- Total Measurements: {metadata.get('total_measurements', 0)}

## Key Metrics

### Power Summary
- Peak Power: {df_daily['peak_power_W'].max():.1f} W
- Average Peak: {df_daily['peak_power_W'].mean():.1f} W
- Total Energy: {df_daily['energy_Wh'].sum():.1f} Wh
- Avg Daily Energy: {df_daily['energy_Wh'].mean():.1f} Wh

### Sky Classification
- Clear Hours: {classification_summary.get('clear_count', 0)} ({classification_summary.get('clear_pct', 0):.1f}%)
- Marginal Hours: {classification_summary.get('marginal_count', 0)} ({classification_summary.get('marginal_pct', 0):.1f}%)
- Cloudy Hours: {classification_summary.get('cloudy_count', 0)} ({classification_summary.get('cloudy_pct', 0):.1f}%)

### Performance
- PR (All Days): {pr_metrics.get('pr_all', 0):.1%}
- PR (Clear Days): {pr_metrics.get('pr_clear', 0):.1%}

## Temperature Analysis
- Average: {df_daily['temp_avg_C'].mean():.1f} °C
- Min: {df_daily['temp_avg_C'].min():.1f} °C
- Max: {df_daily['temp_avg_C'].max():.1f} °C

## Generated Files
- hourly_analysis_all_data.csv
- hourly_analysis_clear_days_only.csv
- daily_summary.csv
- classification_details.csv
- Charts (PNG): 01_daily_power_trend, 02_hourly_pattern, 03_power_ratio_distribution, 04_temperature_analysis, 05_classification_summary
"""
        
        with open(output_file, "w") as f:
            f.write(report)
        
        logger.info(f"Exported summary report to {output_file}")
        return str(output_file)
